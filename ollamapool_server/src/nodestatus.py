#NodeStatus Class - tracks the health of the node, available models and manages communicating state
import socket
import json
from ollama import Client
from azure.servicebus import ServiceBusClient, ServiceBusMessage

class NodeStatus():
    
    def __init__(self,Ollamahost:str,QueueName:str,ConnectionString:str):
        self.__Client__=ServiceBusClient.from_connection_string(ConnectionString)
        self.__sender__ = self.__Client__.get_queue_sender(queue_name=QueueName)       
        self.Host=socket.gethostname()
        self.Ollamahost=Ollamahost
        self.Models=[]
        self.Status="Initializing..."
        self.Message=""
        self.LastQueryTime=0
        self.Client=None

    def to_json(self):
        return {"Host":self.Host,
                "OllamaHost":self.Ollamahost,
                "Status":self.Status,
                "Message":self.Message,
                "Models":self.Models,
                "LastQueryTime":self.LastQueryTime}


    def from_json(self,json_str):
        self.__dict__=json.loads(json_str)

    def SyncStatus(self):
        try:
            message = ServiceBusMessage(json.dumps(self.to_json()))
            self.__sender__.send_messages(message)
            print("Sent status to Queue")
        except Exception as e:
            print(f"Error Sending Status to Queue: {str(e)}")        
        
    def SetStatus(self,Status:str,Message:str):
        print(f"Status: {Message}")
        self.Status=Status
        self.Message=Message
        self.SyncStatus()
        
    def SetErrorStatus(self,Message:str):
        print(f"Error: {Message}")
        self.Status="Error"
        self.Message=Message 
        self.SyncStatus()  
    
    def HasModel(self,Model:str)->bool:
        modelLatest=Model.lower()+":latest"
        return (Model in self.Models) or (modelLatest in self.Models)
    
    #Connects to OLLAMA server and gets the list of models
    def Connect(self):
        try:
            self.Client=Client(host=self.Ollamahost)
            models=self.Client.list()
            self.Models=[model["name"] for model in models["models"]]
            self.SetStatus("Ready","Connected to Ollama Server")
            return True
        except Exception as e:
            self.SetErrorStatus(str(e))
            self.Models=[]
            return False

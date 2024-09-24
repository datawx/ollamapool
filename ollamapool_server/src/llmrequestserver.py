#Ollama Processing Code
import datetime
import json
from ollama import Client
from llmresult import LLMResult
from llmrequest import LLMRequest
from nodestatus import NodeStatus
from azure.servicebus import ServiceBusClient, ServiceBusMessage

#Handles running the LLMRequest and posting the result back to the results queue
class LLMRequestServer():
    
    def __init__(self,node:NodeStatus,ResultsConnectionString:str,ResultsQueueName:str):
        self.Client=Client(host=node.Ollamahost)
        self.ResultsConnectionString=ResultsConnectionString
        self.ResultsQueueName=ResultsQueueName
        self.node=node

    #Post to a service bus queue    
    def AzurePost_ServiceBus(self,json_payload):
        try:
            with ServiceBusClient.from_connection_string(self.ResultsConnectionString) as client:
                sender = client.get_queue_sender(queue_name=self.ResultsQueueName)
                message = ServiceBusMessage(json.dumps(json_payload))
                with sender:
                    sender.send_messages(message)
                    print(f"Queued message: {json_payload['UUID']}")
        except Exception as e:
            print(f"Error Sending to Queue: {str(e)}")

    def ProcessLLMRequest(self,request:LLMRequest)->LLMResult:
        try:
            #Download the model if it is not already downloaded
            if not self.node.HasModel(request.Model):
                self.node.SetStatus("Downloading",f"Downloading Model {request.Model}")
                self.Client.pull(request.Model)
                self.node.SetStatus("Ready",f"Model {request.Model} Downloaded")
            
            #Run LLM query
            timerStart=datetime.datetime.now()
            self.node.SetStatus("Running",f"Processing{request.UUID}")    
            ret = self.Client.chat(
                model=request.Model,
                messages=request.Messages,
                stream=False)
        
            #get result/timing and post back to results queue
            timerEnd=datetime.datetime.now()
            timeDelta=timerEnd-timerStart
            result=LLMResult(UUID=request.UUID,result=ret,timeDelta=str(timeDelta))
            self.AzurePost_ServiceBus(result.to_json())
            self.node.LastQueryTime=timeDelta.total_seconds()
            self.node.SetStatus("Finsihed",f"Processing{request.UUID}")    
            
        except Exception as e:
            #Print Exeption Type and Message
            print("Exception!-------------------------------------------------")
            print(e)
            self.node.SetErrorStatus(f"Error Processing{request.UUID}: {str(e)}")
            print("Exception!-------------------------------------------------\n")
            result=LLMResult(UUID=request.UUID,errorMsg=str(e))
            self.AzurePost_ServiceBus(result.to_json())
            
        return result
    

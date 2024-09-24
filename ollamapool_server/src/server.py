#OLLAMAPool Server Prototype Code
import os
from llmrequest import LLMRequest
from llmrequestserver import LLMRequestServer
from nodestatus import NodeStatus
import time
from typing import List
from azure.servicebus import ServiceBusClient, ServiceBusMessage
import signal

#--------------------------------------------------------------------------------------------------
#Environment Variables
EndPoint_Queries=os.environ.get('EndPoint_Queries')
Endpoint_Results=os.environ.get('Endpoint_Results')
EndPoint_NodeStatus=os.environ.get('EndPoint_NodeStatus')
OLLAMA_Host=os.environ.get('OLLAMA_Host')
#--------------------------------------------------------------------------------------------------

def get_queue_name_from_connection_string(connection_string):
    # Split the connection string by ";" and find the EntityPath part
    key_value_pairs = connection_string.split(';')
    for pair in key_value_pairs:
        if pair.startswith('EntityPath='):
            # Return the part after 'EntityPath=' which is the queue name
            return pair.split('=')[1]
    return None

#Assert if the environment variables are set
if EndPoint_Queries is None:
    raise ValueError("EndPoint_Queries is not set")
if Endpoint_Results is None:
    raise ValueError("Endpoint_Results is not set")
if EndPoint_NodeStatus is None:
    raise ValueError("EndPoint_NodeStatus is not set")
if OLLAMA_Host is None:
    raise ValueError("Ollama_Host is not set")
print("Environment Variables are set OK")

#Get the queue names from the connection strings
QueueName_Queries = get_queue_name_from_connection_string(EndPoint_Queries) 
QueueName_Results = get_queue_name_from_connection_string(Endpoint_Results)
QueueName_NodeStatus = get_queue_name_from_connection_string(EndPoint_NodeStatus)

#--------------------------------------------------------------------------------------------------
#Startup / Main loop
#--------------------------------------------------------------------------------------------------

node=NodeStatus(OLLAMA_Host,QueueName_NodeStatus,EndPoint_NodeStatus)
print("Checking Ollama Server Connection...")
if not node.Connect():
    print("Error Connecting to Ollama Server")
    exit(1)

llmserver=LLMRequestServer(node,Endpoint_Results,QueueName_Results)
running=True

def handle_signal(signal_number, frame):
    global running
    print("Signal received:", signal_number)
    running = False

# Register the signal handler
signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

#Main Message Handling Loop
servicebus_client = ServiceBusClient.from_connection_string(conn_str=EndPoint_Queries)

def receive_messages_from_queue(node:NodeStatus):
    # Create a receiver for the queue
    try:
        with servicebus_client.get_queue_receiver(queue_name=QueueName_Queries) as receiver:
            print("Receiving messages from the queue...")
            received_msgs = receiver.receive_messages(max_message_count=1, max_wait_time=30)
            for msg in received_msgs:
                print(f"Received message: {str(msg)}")
                receiver.complete_message(msg)
                llmRequest=LLMRequest()
                llmRequest.from_json(str(msg))
                result=llmserver.ProcessLLMRequest(llmRequest)
    except Exception as e:
        print(f"Error Receiving from Queue: {str(e)}")
        node.SetErrorStatus(f"Error Receiving from Queue: {str(e)}")
        time.sleep(5)
        return
            
#Main loop
try:
    while running:
        receive_messages_from_queue(node)
except Exception as e:
    print(f"Error in Main Loop: {str(e)}")
finally:
    node.SetStatus("Shutdown","Shut Down Complete")    
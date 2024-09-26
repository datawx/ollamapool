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
ENDPOINT_QUERIES=os.environ.get('ENDPOINT_QUERIES')
ENDPOINT_RESULTS=os.environ.get('ENDPOINT_RESULTS')
ENDPOINT_NODESTATUS=os.environ.get('ENDPOINT_NODESTATUS')
OLLAMA_HOST=os.environ.get('OLLAMA_HOST')
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
if ENDPOINT_QUERIES is None:
    raise ValueError("ENDPOINT_QUERIES is not set")
if ENDPOINT_RESULTS is None:
    raise ValueError("ENDPOINT_RESULTS is not set")
if ENDPOINT_NODESTATUS is None:
    raise ValueError("ENDPOINT_NODESTATUS is not set")
if OLLAMA_HOST is None:
    raise ValueError("OLLAMA_HOST is not set")
print("Environment Variables are set OK")

#Get the queue names from the connection strings
QueueName_Queries = get_queue_name_from_connection_string(ENDPOINT_QUERIES) 
QueueName_Results = get_queue_name_from_connection_string(ENDPOINT_RESULTS)
QueueName_NodeStatus = get_queue_name_from_connection_string(ENDPOINT_NODESTATUS)

#--------------------------------------------------------------------------------------------------
#Startup / Main loop
#--------------------------------------------------------------------------------------------------

node=NodeStatus(OLLAMA_HOST,QueueName_NodeStatus,ENDPOINT_NODESTATUS)
print("Checking Ollama Server Connection...")
if not node.Connect():
    print("Error Connecting to Ollama Server")
    exit(1)

llmserver=LLMRequestServer(node,ENDPOINT_RESULTS,QueueName_Results)
running=True

def handle_signal(signal_number, frame):
    global running
    print("Signal received:", signal_number)
    running = False

# Register the signal handler
signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

#Main Message Handling Loop
servicebus_client = ServiceBusClient.from_connection_string(conn_str=ENDPOINT_QUERIES)

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
#--------------------------------------------------------------------------------------------------------------------------------------------------------------
OLLAMAPOOL - your highly scalable simple LLM service
#--------------------------------------------------------------------------------------------------------------------------------------------------------------

Like LLMs and want to use AI do do hundreds/thousands or more GPT-style queries to transform one dataset into another or do a repetive task?
Want to work with sensitive data you don't want to share with an external provider like OpenAI? 
Want to just run locally and OWN your weights/models and never have them taken away or modified to have safeguards so your app stops working?


Welcome to OLLAMAPOOL!
This tool is built around the already awesome OLLAMA docker package and allows you to setup indepedent OLLAMA workers and run queries on them.
Anything with processing power and RAM can be a potential worker node (LLAMA3.1 runs pretty well with just 4 cores and 8GB of RAM).
Best of all very little RAM or processing is power is used when its not in action.
So drop a couple of nodes on your gaming machine, one on the laptop, one on the fileserver or spin up a bunch in the cloud.

It's designed to be relatively simple and doesn't expose open ports to the network/internet/world+dog
The only requirement is you need to have some queues (like Azure Service Bus, GCP PubSub or AWS Simple Notification Service) - but these are pretty much free.
Only Azure is supported for now but other providers will be supported in time - you can easily sign up for a free Azure account with lots of credits.
Queues are _really_ cheap on Azure. About $0.05/month for a million messages (which you'll never use).
The benefit of using Queues is that the orchestration across nodes is all handled as a service and you don't need to setup networking/security and expose ports.

#--------------------------------------------------------------------------------------------------------------------------------------------------------------
What is OLLAMAPOOL not suitable for?

.GPT Style chat - there's no token streaming since this is a batch tool and many solutions to this problem exist already (see my OLLAMAFARM repo for this!)
.Full On Production - it'll work, but be prepared to roll up your sleeves and improve it. If you feel like it check in those changes 
.Kubernetes - it'll probably work as is quite well but it'd be better if we used Kubernetes jobs (I'll get to that one day!)


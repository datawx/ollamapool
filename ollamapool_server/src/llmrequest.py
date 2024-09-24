import json
import uuid

class LLMRequest:
    def __init__(self,Model:str="",systemMessage:str="",query:str=""):
        self.UUID=str(uuid.uuid4())
        self.Model=Model
        self.systemMessage=systemMessage
        self.query=query
        self.Messages=[{'role': 'system', 'content': systemMessage},
                       {'role': 'user', 'content': query}]

    def to_json(self):
        return self.__dict__
    
    def from_json(self,json_str):
        self.__dict__=json.loads(json_str)
        

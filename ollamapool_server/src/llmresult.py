import json

class LLMResult:
    def __init__(self,UUID:str="",result:str="",errorMsg:str="",timeDelta:str=""):
        self.UUID=UUID
        self.result=result
        self.errorMsg=errorMsg
        self.HasError=errorMsg!=""
        self.timeDelta=timeDelta

    def to_json(self):
        return self.__dict__
    
    def from_json(self,json_str):
        self.__dict__=json.loads(json_str)
    
from pydantic import BaseModel,ConfigDict
from enum import Enum

class Question(BaseModel):
    question : str 
    ground_truth : list[str]

class Questions(BaseModel):
    Questions : list[Question]

class Verdict(str, Enum):
    TP = "TP"
    FP = "FP"
    FN = "FN"

class ItemAC(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    reason: str
    verdict: Verdict
    
class StructureAC(BaseModel):
    items: list[ItemAC]
    
class ItemF(BaseModel):
    reason: str
    verdict: int

class StructureF(BaseModel):
    items: list[ItemF]
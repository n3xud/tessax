from pydantic import BaseModel
from typing import List

class Question(BaseModel):
    question : str 
    ground_truth : str

class Questions(BaseModel):
    Questions : List[Question]

from pandas import DataFrame
import typing as t
import json
import numpy as np
from abc import ABC,abstractmethod
from .llm import as_query_json
from .tools import retrieve_context
def _get_faithfulness_score(rows):
        structure = {
                    
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "statement": {"type": "string"},
                                    
                                },
                                "required": ["statement"]
                            }
                        }
        question = rows["question"]
        answer = rows["answer"]
        
        prompt = f"""Given this question and answer, break down the answer into clear, standalone statements.
                    Replace all pronouns with their referents.

                    Question: {question}
                    Answer: {answer}

                    Return ONLY a JSON array of statements. Each statement should be a complete, self-contained sentence."""
        
        statements = as_query_json(prompt,structure)
       
        context = retrieve_context(question)
        print(statements)
        prompt = f"Your task is to judge the faithfulness of statements:{statements} based on a given context:{context}. For each statement you must return verdict as 1 if the statement can be directly inferred based on the context or 0 if the statement can not be directly inferred based on the context."
        structure = {
                    
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "verdict": {"type": "integer"},
                                    
                                },
                                "required": ["verdict"]
                            }
                        }
        scores = as_query_json(prompt,structure)
        print(scores)
        score_list = json.loads(scores)
       
        score_list = [item["verdict"] for item in score_list]
    
        score_arr = np.array(score_list)
        
        faitfulness = np.mean(score_arr==1)
        return faitfulness

     

def _get_context_relevancy_score(rows):
    
    question = rows["question"]
    context = retrieve_context(question)
    
    prompt1 = f"""You are a world class expert designed to evaluate the relevance score of a Context:{context} in order to answer the Question:{question}.
        Your task is to determine if the Context contains proper information to answer the Question.
        Do not rely on your previous knowledge about the Question.
        Use only what is written in the Context and in the Question.
        Follow the instructions below:
        0. If the context does not contains any relevant information to answer the question, say 0.
        1. If the context partially contains relevant information to answer the question, say 1.
        2. If the context contains any relevant information to answer the question, say 2.
        """
    structure = {
                    
                            
                                "type": "object",
                                "properties": {
                                    "rating": {"type": "integer"},
                                    
                                },
                                "required": ["rating"]
                            }
    score1 = json.loads(as_query_json(prompt1,structure))     
    score1 = score1["rating"]
    n_score1 = score1 / 2       
    prompt2 = """As a specially designed expert to assess the relevance score of a given Context in relation to a Question, my task is to determine the extent to which the Context provides information necessary to answer the Question. I will rely solely on the information provided in the Context and Question, and not on any prior knowledge.

        Here are the instructions I will follow:
        * If the Context does not contain any relevant information to answer the Question, I will respond with a relevance score of 0.
        * If the Context partially contains relevant information to answer the Question, I will respond with a relevance score of 1.
        * If the Context contains any relevant information to answer the Question, I will respond with a relevance score of 2."""
    score2 = json.loads(as_query_json(prompt2,structure)) 
    score2 = score2["rating"]
    n_score2 = score2 / 2 
    final_score = (n_score1 + n_score2) / 2
    return final_score
class Metric(ABC):
    @abstractmethod
    def score(self,df:DataFrame):
        pass
    
    
    
    
class Faithfulness(Metric):
    def score(self,df:DataFrame):
        
                  
        df["faithfulness"] = df.apply(_get_faithfulness_score,axis=1)     
      
        
    
    
class AnswerRelevance(Metric):
    
    #How relevant is the given answer to the question
    def score():
        
        pass
    
class ContextRelevance(Metric):
    #How relevant is the retireved context to the question
    def score(self,df:DataFrame):
        
        df["contex_relevancy"] = df.apply(_get_context_relevancy_score,axis=1)   
    
    
class Evaluate:
    def __init__(self,metrics : t.List[Metric]):
        self.metrics = metrics
    
    def run_metrics(self,qa:DataFrame):
        
        for metric in self.metrics:
            metric.score(qa)
        

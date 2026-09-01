from pandas import DataFrame
import typing as t
import json
import numpy as np
from abc import ABC,abstractmethod
from .llm import as_query_json,generate_atomic,askgpt_struct
from .tools import retrieve_context
from .embedding import _get_similarities
from .config import cfg
from .models import StructureAC,StructureF
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
        
       
        context = retrieve_context(question)
      
        prompt = f"""You will be given a question, an answer, and a context. Perform two steps:

STEP 1 - BREAK DOWN: Break down the answer into clear, standalone statements. Replace all pronouns with their referents. Each statement should be a complete, self-contained sentence.

STEP 2 - JUDGE FAITHFULNESS: For each statement from Step 1, judge its faithfulness against the given context using these rules:
1. Return 1 if ALL claims in the statement can be directly inferred from the context.
2. Return 1 if the statement explicitly states that it does not know, cannot answer, or that the context lacks sufficient information (and makes no further ungrounded claims).
3. Return 0 if the statement contains any claim, fact, or assumption that CANNOT be directly inferred from the context.

Question: {question}
Answer: {answer}
Context: {context}

OUTPUT REQUIREMENT:
Return ONLY a valid JSON array of objects, no markdown fences, no commentary before or after. Each object must have exactly these keys:
- "statement": the standalone statement from Step 1
- "reason": a brief explanation for the verdict
- "verdict": 1 or 0"""
        structure = {
                    
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "reason":{"type":"string"},
                                    "verdict": {"type": "integer"},
                                    
                                },
                                "required": ["reason","verdict"]
                            }
                        }
        if cfg.use_gpt:
            
            faith = askgpt_struct(systemprompt="",userprompt=prompt,structure=StructureF)
            score_list = [x.verdict for x in faith.items]
            
        else:
            
            scores = as_query_json(prompt,structure)
       
            score_list = json.loads(scores)
       
            score_list = [item["verdict"] for item in score_list]
    
        score_arr = np.array(score_list)
        
        faitfulness = np.mean(score_arr==1)
        return faitfulness

     
def _get_answer_correctness_score(rows):
    ground_truth = rows["ground_truth"]
    answer = rows["answer"]
    # atomic_answer = generate_atomic(answer)
    
    prompt = f"""Given ground truth statements and an answer, first break the answer down into atomic statements (each statement should express exactly one fact or claim). Then analyze each atomic statement and classify it into one of the following categories:
                    - TP (true positive): statements from the answer that are directly supported by one or more statements in the ground truth
                    - FP (false positive): statements from the answer that are NOT directly supported by any statement in the ground truth
                    - FN (false negative): statements found in the ground truth but not present in the answer

                    Each statement can only belong to one category.

                    GROUND TRUTH STATEMENTS:
                    {ground_truth}

                    ANSWER:
                    {answer}

                    OUTPUT REQUIREMENT:
                    Return ONLY a valid JSON array of objects, no markdown fences, no commentary before or after. Each object must have exactly these keys:
                    - "reason": a brief explanation
                    - "label": one of "TP", "FP", "FN"
        
    """
    structure = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "reason": {"type": "string"},
            "verdict": {"type": "string", "enum": ["TP", "FP", "FN"]},
        },
        "required": ["reason", "verdict"],
    },
}
    
    if cfg.use_gpt:
        correctness = askgpt_struct(systemprompt="",userprompt=prompt,structure=StructureAC)
        verdicts = [x.verdict for x in correctness.items]
    else:
        correctness = json.loads(as_query_json(prompt,structure))
  
        verdicts = [x["verdict"] for x in correctness]
  
    array = np.array(verdicts)
    TP_count = np.count_nonzero(array == "TP")
    FP_count = np.count_nonzero(array == "FP")
    FN_count = np.count_nonzero(array == "FN")
    denominator = TP_count + 0.5 * (FP_count + FN_count)
    F1_score = 0
    if denominator != 0:
        
        F1_score = TP_count / denominator
      
    emb_gt = " ".join(ground_truth)
    emb_a = answer
    simil = _get_similarities(emb_gt,emb_a)
    return ((F1_score * 0.7) + (simil * 0.3)).item()


def _get_context_recall_score(rows):
    
    ground_truth = rows["ground_truth"]
    
    question = rows["question"]
    context = retrieve_context(question)
  
   
    
    prompt = f"""You are an uncompromising factual verification assistant. Your task is to evaluate a list of standalone "Ground Truth" statements against a provided "Context" text and determine if each statement can be fully verified  by that context.
    Definitions:
        - 1 (Verified): Every single element of the statement is explicitly supported by the provided Context. No assumptions, extrapolations, or external knowledge allowed.
        - 0 (Unverified): The context contradicts the statement, fails to mention the facts inside the statement, or only partially supports it.

        Input Data:
        ---
        CONTEXT:
        {context}

        GROUND TRUTH STATEMENTS:
        {ground_truth}
        ---
        Output Requirements:
        
        Return ONLY a valid JSON array of objects, no markdown fences, no commentary before or after. Each object must have exactly these keys:
                - "reason": a brief explanation
                - "verdict": 0 or 1
    
    
    """

    
    structure2={
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "reason": {"type": "string"},
            "verdict": {"type": "integer"},
        },
        "required": ["reason", "verdict"],
    },
}
    
    
    if cfg.use_gpt:
        recall = askgpt_struct(systemprompt="",userprompt=prompt,structure=StructureF)
        verdicts = [x.verdict for x in recall.items]
    else:
        
        recall = json.loads(as_query_json(prompt,structure2))
        verdicts = [x["verdict"] for x in recall]
    recall_arr = np.array(verdicts)
    recall_all = recall_arr.size
    recall_positive  = (recall_arr == 1).sum()
    return recall_positive/recall_all


def _get_context_precision_score(rows):
    
    
    ground_truth = rows["ground_truth"]
    
    question = rows["question"]
    context = retrieve_context(question)
  
    prompt = f"""Given question: {question}, answer: {ground_truth} and list of context: {context} verify for every element in the context list if is useful in arriving at the given answer. 
    Definitions:
            - 1 : if useful
            - 0 : if not
            
            Give verdict as "1" if useful and "0" if not with.
            
    Output Requirements:        
    Return ONLY a valid JSON array of objects, no markdown fences, no commentary before or after. Each object must have exactly these keys:
                    - "reason": a brief explanation
                    - "verdict": 0 or 1
            
            """
    structure1 = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "reason": {"type": "string"},
            "verdict": {"type": "integer"},
        },
        "required": ["reason", "verdict"],
    },
}
    
    
    if cfg.use_gpt:
            precision = askgpt_struct(systemprompt="",userprompt=prompt,structure=StructureF)
            verdicts = [x.verdict for x in precision.items]
    else:
        verdict_list = json.loads(as_query_json(prompt,structure1))
        verdicts = [x["verdict"] for x in verdict_list]
    verdict_arr = np.array(verdicts)
    index = np.arange(1,len(verdict_arr)+1)
    cumsum = np.cumsum(verdict_arr)
    prec = cumsum / index
    prec_relevant = prec * verdict_arr
    context_precision = prec_relevant.sum() / verdict_arr.sum() if verdict_arr.sum() else 0.0

    return context_precision


class Metric(ABC):
    @staticmethod
    @abstractmethod
    def score(df:DataFrame) -> float:
        pass
    
    
    
#Retrieval part
    
    
 
class ContextPrecision(Metric):
    
    @staticmethod
    def score(df:DataFrame) -> float:
    
        df["context_precision"] = df.apply(_get_context_precision_score,axis=1)  
        return df["context_precision"].mean()
    
class ContextRecall(Metric):   
    @staticmethod
    def score(df:DataFrame) -> float:
    
        df["context_recall"] = df.apply(_get_context_recall_score,axis=1)   
        return df["context_recall"].mean()
 
 
      
        


#Generation part

class Faithfulness(Metric):
    @staticmethod
    def score(df:DataFrame) -> float:
        
                  
        df["faithfulness"] = df.apply(_get_faithfulness_score,axis=1)    
        return df["faithfulness"].mean()
 
class AnswerCorrectness(Metric):
    
    #Compare Ground Truth with answer factual and semantic
    @staticmethod
    def score(df:DataFrame) -> float:
        
        df["answer_correctness"] = df.apply(_get_answer_correctness_score,axis=1)
        return df["answer_correctness"].mean()
          




class Evaluate:
    def __init__(self,metrics : t.List[Metric]):
        self.metrics = metrics

    def run_metrics(self,qa:DataFrame):
        scores = []
        for metric in self.metrics:
            scores.append(metric.score(qa))
        return scores

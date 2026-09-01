from pandas import DataFrame

from .llm import generate_questions ,as_query
from . import prompts
from .tools import retrieve_context
from .config import cfg
__all__ = [
    "generate_qa",
    "generate_answers"
]

def generate_q(html):
    """Generates an Q&A DataFrame with columns question , ground_truth, answer

    Args:
        html (_type_): _description_
        question_count (_type_): _description_

    Returns:
        _type_: _description_
    """
    prompt = prompts._qa_prompt(html,count=cfg.question_count)
    df: DataFrame = generate_questions(prompt=prompt)
    print("QA GENERATED")
    return df


def _generate_answers(rows):
    question = rows["question"]
    context = retrieve_context(question) 
    
    prompt = prompts._qa_answer_prompt(question,context)
    answer = as_query(prompt)
    return answer
    
def generate_answers(df:DataFrame):
 
    df["answer"] = df.apply(_generate_answers,axis=1)
    return df 
    

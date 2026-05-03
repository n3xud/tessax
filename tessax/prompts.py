"""Set of prompts for pipeline."""

from bs4 import BeautifulSoup

def _qa_prompt(html:BeautifulSoup,count:int):
    """Prompt for generating question and ground truth

    Args:
        html (Beautifulsoup): _
        count (int): count of question,ground_truth pairs

    Returns:
        str: prompt
    """
    
    prompt =f"""You are an expert content analyst and educational content creator. Your task is to extract factual information from the provided HTML and generate a high-quality Q&A dataset.

        ### Input

        HTML Content:
        {html}

        ### Action

        Create exactly {count} question-ground_truth pairs based on the HTML content. Each pair should:
        * **Question**: Be clear, specific, and natural-sounding — written as a human would ask it for 
        * **Ground truth**: Be factually accurate and grounded directly in the HTML content; include only information present in the source; be concise but complete (1-3 sentences typically)
        * **Variety**: Cover different sections or key topics from the HTML; avoid repetitive questions
       
        ### Quality Expectations

        * All answers must be traceable back to the HTML source
        * Questions should sound natural and conversational, not robotic
        * Questions should be self-contained (readable without the original HTML)

        If the HTML contains fewer than {count} distinct factual topics, create variations on core topics with different question angles.
        
        ### MANDATORY LANGUAGE RULE
        You must detect the primary language of the {html} content. 
        All strings within the JSON ("question" and "ground_truth") MUST be written in that same language. 
        Do not use English unless the source HTML is in English. This is a strict constraint for the system's API processing.
        
        """
    return prompt


def _qa_answer_prompt(question:str,context:list[str]):
    
    context = " ".join(context)
    
    """Prompt for generating answers

    Args:
        question (str): _
        context (list[str]): _

    Returns:
       str: prompt
    """
    prompt = f"Answer the question:{question} with the given context:{context}. If u cant answer the question with the given context return None"
    return prompt

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
    
    prompt =f"""
    
        You are an expert content analyst. From the HTML below, generate exactly {count} question-ground_truth pairs as a Q&A dataset.

    HTML: {html}

    For each pair, provide:
    - **question**: A natural, conversational, self-contained question (understandable without the HTML).
    - **ground_truth_raw**: A concise, accurate answer grounded directly in the HTML.
    - **ground_truth_atomic**: The answer split into atomic, self-contained facts — one fact per statement, no "and/but/because" combining, all pronouns replaced with their actual referents.

    Rules:
    - Cover {count} distinct topics/sections from the HTML (no repeats). If fewer than {count} exist, vary the angle on core topics.
    - Every claim must be traceable to the HTML.
    - Detect the HTML's primary language and write ALL text (questions + answers) in that language — never default to English unless the source is English.

    Output as JSON.
        
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
    prompt = f"""Answer the user's question using only the information in the context that is directly relevant to it.

                Rules:
                - Do not include unrelated details from the context, even if present  unless the question asks for them.
                - Do not restructure the answer into steps, headers, or bold labels unless the question explicitly asks for instructions.
                - Keep the answer as concise as possible — only the useful, relevant context, nothing extra.
                - If the context doesn't contain enough information to answer, say so directly instead of guessing.

                Context:
                {context}

                Question:
                {question}
"""
    return prompt


def _atomic_prompt(text:str) -> str:
    
    prompt = f"""
        ### Task
        Break the input text into a list of atomic, standalone statements.


        1. Each statement expresses exactly one fact. Never join facts with "and", "but", "because", or a comma-splice — split them into separate statements instead.
        2. Replace all pronouns (he, she, it, they, this, that, these) with the specific noun they refer to. Every statement must be understandable with zero outside context.
        3. Only include facts explicitly stated in the text. Do not infer, extrapolate, or add outside knowledge.
        4. Each statement must be unique. Do not repeat the same fact in different wording. Do not restate a statement you have already produced.
        5. Do not pad the list. Produce exactly as many statements as there are distinct facts in the text — no more, no fewer. A short input text should produce a short list.
        6. Stop as soon as every distinct fact from the text has been captured once. Do not continue generating after that point.

        ### Output format
        Return ONLY a JSON array of strings. No explanation, no markdown, no repetition of these instructions.

        ### Input Text
        {text}"""
    return prompt
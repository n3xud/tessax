from llm_handler import _llm_instance
import prompts
import tools

def _generate_qa(html):
    prompt = prompts._qa_prompt(html)
    results = tools._as_query(prompt)
    return results
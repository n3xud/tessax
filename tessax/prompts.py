

def _qa_prompt(html):
    new_prompt =f"""You are an expert content analyst and educational content creator. Your task is to extract factual information from the provided HTML and generate a high-quality Q&A dataset.

### Input

HTML Content:
{html}

### Action

Create exactly {n} question-answer pairs based on the HTML content. Each pair should:

* **Question**: Be clear, specific, and natural-sounding — written as a human would ask it for [USE CASE]
* **Answer**: Be factually accurate and grounded directly in the HTML content; include only information present in the source; be concise but complete (1-3 sentences typically)
* **Variety**: Cover different sections or key topics from the HTML; avoid repetitive questions
* **Difficulty**: Range from straightforward recall to [QUESTION STYLE]

### Result Format

Output the Q&A pairs in a JSON object with this form:

               "question": "question",
                "answer": "answer",
               

                

... (continue through pair {n})

### Quality Expectations

* All answers must be traceable back to the HTML source
* Questions should sound natural and conversational, not robotic
* No made-up information or assumptions beyond what's stated
* Answers should be self-contained (readable without the original HTML)
* Prioritize factual, objective information over subjective interpretation

If the HTML contains fewer than 10 distinct factual topics, create variations on core topics with different question angles.
"""
    return new_prompt
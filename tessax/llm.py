import os
import json
from openai import OpenAI
os.environ["HF_HUB_OFFLINE"] = "0"
from vllm import LLM, SamplingParams
from vllm.sampling_params import StructuredOutputsParams
import pandas as pd
from pandas import DataFrame
from .models import Questions
from . import prompts
from .config import cfg
__all__ = [
            "generate_questions",
            "as_query"
        ]

# _model = LLM(
# model="Qwen/Qwen3-8B-AWQ",
# gpu_memory_utilization=0.85,
# enforce_eager=True,
# max_model_len=20000,
# quantization="awq_marlin",
# enable_chunked_prefill = True,
# )
client = OpenAI()
def generate_questions(prompt)-> DataFrame:
    
    if cfg.use_gpt:
        questions = askgpt_struct(systemprompt="You are a precise content analyst extracting atomic facts.",userprompt=prompt,structure=Questions)
    else:
        #returns a pandas dataframe with rows question, ground_truth
        messages = [
            {f"role": "user", "content": prompt}
                
        ]
        structured_outputs_params = StructuredOutputsParams(json={
        "type": "object",
        "properties": {
            "Questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string"},
                        "ground_truth": {"type": "array", "items":{
                "type":"string"
            }},
                    },
                    "required": ["question", "ground_truth"]
                }
            }
        },
        "required": ["Questions"]
    })
        # sampling_params = SamplingParams(temperature=0.8, top_p=0.95,max_tokens=16000, structured_outputs=structured_outputs_params , presence_penalty=0.5)
        # results = _model.chat(messages, sampling_params)
        
        #questions = Questions.model_validate_json(results[0].outputs[0].text)
    df = pd.DataFrame(questions.model_dump()["Questions"])
    return df



def as_query(text) -> str:
    
    if cfg.use_gpt:
        answer = askgpt(text)
    else:
        messages = [
            {f"role": "user", "content": text}
                
        ]
        sampling_params = SamplingParams(temperature=0.8, top_p=0.95,max_tokens=16000)
        # results = _model.chat(messages,sampling_params=sampling_params,chat_template_kwargs={"enable_thinking": False})
        # answer = results[0].outputs[0].text
    return answer

def as_query_json(text,structure) -> str:
    
    messages = [
        {f"role": "user", "content": text}
              
    ]
    structured_outputs_params = StructuredOutputsParams(json=structure)
    sampling_params = SamplingParams(temperature=0.8, top_p=0.95,max_tokens=20000,structured_outputs=structured_outputs_params,repetition_penalty=1.15)
    # results = _model.chat(messages,sampling_params=sampling_params,chat_template_kwargs={"enable_thinking": False})
    return #results[0].outputs[0].text

def generate_atomic(text:str) -> list:
    prompt = prompts._atomic_prompt(text)
    messages = [
        {f"role": "user", "content": prompt}          
    ]
    structure1 = {
        "type":"array",
        "items":{
            "type":"string"
        },
        "maxItems":20,
    }
    structured_outputs_params = StructuredOutputsParams(json=structure1)
    sampling_params = SamplingParams(temperature=0.8, top_p=0.95,max_tokens=16000,structured_outputs=structured_outputs_params)
    # results = _model.chat(messages,sampling_params=sampling_params,chat_template_kwargs={"enable_thinking": False})
    # json1 = results[0].outputs[0].text
    return #json.loads(json1)

    
    
    
    

def askgpt_struct(systemprompt,userprompt,structure):
    response = client.responses.parse(
        model="gpt-5-nano",
        reasoning={"effort": "minimal"},
        input=[
            {"role": "system", "content":f"{systemprompt}"},
            {
                "role": "user",
                "content":  f"{userprompt}",
            },
        ],
        text_format=structure,
    )
    return response.output_parsed
    
def askgpt(userprompt):
    response = client.responses.create(
    model="gpt-5-nano",
    input=f"{userprompt}",
    reasoning={"effort":"minimal"},
)

    return response.output_text
    


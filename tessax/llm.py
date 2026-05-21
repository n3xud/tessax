import os
os.environ["HF_HUB_OFFLINE"] = "1"
from vllm import LLM, SamplingParams
from vllm.sampling_params import StructuredOutputsParams
import pandas as pd
from pandas import DataFrame
from .models import Questions


__all__ = [
            "generate_questions",
            "as_query"
        ]

_model = LLM(
model="Qwen/Qwen3-8B-AWQ",
gpu_memory_utilization=0.77,
enforce_eager=True,
max_model_len=14000,
quantization="awq_marlin",
)

def generate_questions(prompt)-> DataFrame:
    #returns a pandas dataframe with rows question,answer
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
                    "ground_truth": {"type": "string"},
                },
                "required": ["question", "ground_truth"]
            }
        }
    },
    "required": ["Questions"]
})
    sampling_params = SamplingParams(temperature=0.8, top_p=0.95,max_tokens=14000, structured_outputs=structured_outputs_params)
    results = _model.chat(messages, sampling_params)
    
    questions = Questions.model_validate_json(results[0].outputs[0].text)
    df = pd.DataFrame(questions.model_dump()["Questions"])
    return df



def as_query(text) -> str:
    messages = [
        {f"role": "user", "content": text}
              
    ]
    sampling_params = SamplingParams(temperature=0.8, top_p=0.95,max_tokens=14000)
    results = _model.chat(messages,sampling_params=sampling_params,chat_template_kwargs={"enable_thinking": False})
    return results[0].outputs[0].text

def as_query_json(text,structure) -> str:
    print(text)
    messages = [
        {f"role": "user", "content": text}
              
    ]
    structured_outputs_params = StructuredOutputsParams(json=structure)
    sampling_params = SamplingParams(temperature=0.8, top_p=0.95,max_tokens=14000,structured_outputs=structured_outputs_params)
    results = _model.chat(messages,sampling_params=sampling_params,chat_template_kwargs={"enable_thinking": False})
    return results[0].outputs[0].text
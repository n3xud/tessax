from vllm import LLM, SamplingParams
from vllm.sampling_params import StructuredOutputsParams



_model = LLM(
model="Qwen/Qwen3-8B-AWQ",
gpu_memory_utilization=0.75,
enforce_eager=True,
max_model_len=4000,
quantization="awq_marlin",
)


         
def _generate_questions(prompt):

    messages = [
        {f"role": "user", "content": prompt}
              
    ]
    structured_outputs_params = StructuredOutputsParams(json={
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "question": {"type": "string"},
                "answer": {"type": "string"}
            },
            "required": ["question", "answer"]
        }
    })
    sampling_params = SamplingParams(temperature=0.8, top_p=0.95,max_tokens=8000, structured_outputs=structured_outputs_params)
    results = _model.chat(messages, sampling_params)
    return results


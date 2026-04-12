import nltk
from nltk.tokenize import sent_tokenize
from typing import List


nltk.download('punkt_tab')




def _get_sentences(text : str)-> List[str]:

    sentences = sent_tokenize(text)
 
    return sentences
    


# def deduplicate(embedded_content):
#         # score = 1
#         # vector_query = VectorizedQuery(vector = embedded_content, k_nearest_neighbors=3, fields="content_vector", exhaustive=True)

#         # results = config.SEARCH_CLIENT.search(
#         #     vector_queries=[vector_query],
#         #     top=1
#         # )
#         # results=list(results)
#         if len(results)!=0:
#             for result in results:

#                 score = float(list({result['@search.score']})[0])

#             if score <0.95:
#                 return False
#             else:
#                 return True
#         else:
#             return False
# def _as_query_llm(messages):

    
#     text = tokenizer.apply_chat_template(
#     messages,
#     tokenize=False,
#     add_generation_prompt=True,
#     enable_thinking=False, # Switches between thinking and non-thinking modes. Default is True.

#     )
    
#     model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

#     # conduct text completion
#     generated_ids = model.generate(
#         **model_inputs,
#         max_new_tokens=32768,
#         temperature=0.7,    # Recommended for Qwen 3.0
#         top_p=0.8,
#         top_k=20,
#     )
#     output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist() 
    
#     content = tokenizer.decode(output_ids[0:], skip_special_tokens=True).strip("\n")
    
#     return content

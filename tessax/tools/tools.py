from tessax import model, tokenizer


def get_token_length(text):

    output = tokenizer.encode(text)
    token_count = len(output.ids)

    return token_count


def embedding(queries):

    query_embeddings = model.encode(queries)

    return query_embeddings


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

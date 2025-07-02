from elastic_connection import ElasticsearchConnection
from datetime import datetime
import json
from synonyms import thai_synonyms
from sentence_transformers import SentenceTransformer
from tqdm import tqdm


CURRENTDATE = datetime.strftime(datetime.now(),"%Y%m%d")
INDEX_NAME = 'combine_new_model'
es = ElasticsearchConnection.get_instance()
model = SentenceTransformer('intfloat/multilingual-e5-base')
K = 20

if es.ping():
    print("Successfully connected to Elastic!")
else:
    print("Connection failed. Please check your connection information")

def lexical_search(query: str, top_k: int = K):
    lexical_result = es.search(
        index=INDEX_NAME,
        body={
            "query":{
                "multi_match": {
                    "query": query,
                    "fields": ["Name","Category"],
                    "fuzziness": "AUTO",
                }
            },"size": top_k
        },
        source_excludes=["text_vector"]
    )

    lexical_hits = lexical_result["hits"]["hits"]
    max_bm25_score = max([hit["_score"] for hit in lexical_hits], default=1.0)
    
    for hit in lexical_hits:
        hit["_normalized_score"] = hit["_score"] / max_bm25_score
    return lexical_hits

def semantic_search(query: str, top_k: int = K):
    query_vector = model.encode(query).tolist()
    
    script_query = {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                "source": "cosineSimilarity(params.query_vector, 'text_vector') + 1",
                "params": {"query_vector": query_vector},
            }
        }
    }

    semantic_result = es.search(
        index=INDEX_NAME,
        body= {
            "query": script_query,
            "size": top_k,
        },
        source_excludes=["text_vector"]
    )

    semantic_hits = semantic_result["hits"]["hits"]
    max_semantic_score = max([hit["_score"] for hit in semantic_hits], default=1.0)

    for hit in semantic_hits:
        hit["_normalized_score"] = hit["_score"] / max_semantic_score

    return semantic_hits

def reciprocal_rank_fusion(lexical_hits,semantic_hits,k=60):
    
    rrf_scores = {}
    for rank,hit in enumerate(lexical_hits,start=1):
        doc_id = hit["_id"]
        score = 1/ (k + rank)
        if doc_id in rrf_scores:
            rrf_scores[doc_id]["rrf_score"] += score
        else:
            rrf_scores[doc_id] = {
                "Category": hit["_source"]["Category"],
                "Name": hit["_source"]["Name"],
                "Unit": hit["_source"]["Unit"],
                "Factor": hit["_source"]["Factor"],
                "Reference": hit["_source"]["Reference"],
                "Last_Updated": hit["_source"]["Last_Updated"],
                "lexical_score": hit["_normalized_score"],
                "semantic_score": 0,
                "rrf_score": score
            }

    for rank,hit in enumerate(semantic_hits,start=1):
        doc_id = hit["_id"]
        score = 1/ (k + rank)
        if doc_id in rrf_scores:
            rrf_scores[doc_id]["rrf_score"] += score
            rrf_scores[doc_id]["semantic_score"] = hit["_normalized_score"]
        else:
            rrf_scores[doc_id] = {
                "Category": hit["_source"]["Category"],
                "Name": hit["_source"]["Name"],
                "Unit": hit["_source"]["Unit"],
                "Factor": hit["_source"]["Factor"],
                "Reference": hit["_source"]["Reference"],
                "Last_Updated": hit["_source"]["Last_Updated"],
                "lexical_score": 0,
                "semantic_score": hit["_normalized_score"],
                "rrf_score": score
            }


    sorted_result = sorted(
        rrf_scores.values(),key=lambda x: x["rrf_score"], reverse=True
    )

    return sorted_result

def hybrid_search(query: str, lexical_top_k , semactic_top_k):
    
    lexical_hits = lexical_search(query=query, top_k=lexical_top_k)
    semantic_hits = semantic_search(query=query, top_k=semactic_top_k)

    combined_results = reciprocal_rank_fusion(lexical_hits,semantic_hits, k=60)
    # for i in combined_results:
    #     print(i)
    return combined_results


if __name__ == "__main__":
    print(lexical_search(query="ก๊าซหุงต้ม",top_k=10))
    print(semantic_search(query="ก๊าซหุงต้ม",top_k=10))
    print(hybrid_search(query="ก๊าซหุงต้ม",lexical_top_k=10,semactic_top_k=10))
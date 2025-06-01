from fastapi import Query, APIRouter
from elastic_connection import ElasticsearchConnection
from sentence_transformers import SentenceTransformer

INDEX_NAME = 'combine'
BM25_WEIGHT = 0.6
VECTOR_WEIGHT = 1 - BM25_WEIGHT
SIZE = 100
es = ElasticsearchConnection.get_instance()
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
router = APIRouter()

@router.get("/search-combine")
async def search(query: str = Query(None, description="All Table Search")):
    try:
        #query
        if not query:
            response = es.search(index=INDEX_NAME, body={
                "query": {
                    "match_all": {}
                },
                "size": 10000
            })
        else:
            query_vector = model.encode(query).tolist()
            response = es.search(index=INDEX_NAME, body={
                "query": {
                    "bool": {
                        "should": [
                            {
                                "multi_match": {
                                    "query": query,
                                    "fields": ["Name^3","Category"],
                                    "boost": BM25_WEIGHT
                                }
                            },
                            {
                                "knn": {
                                    "field" : "text_vector",
                                    "query_vector": query_vector,
                                    "k": 20,
                                    "num_candidates": 200,
                                    "boost": VECTOR_WEIGHT
                                }
                            }
                        ]
                    }
                }
            })
        
        unique_results = []
        seen_ids = set()
        for hit in response['hits']['hits']:
            if hit["_id"] not in seen_ids:
                result = hit["_source"].copy()
                result["score"]= hit["_score"]

                unique_results.append(result)
                seen_ids.add(hit["_id"])
                
    except Exception as e:
        return {"error": str(e)}
    
    return unique_results



### rrf #####

# from fastapi import Query, APIRouter
# from elastic_connection import ElasticsearchConnection
# from sentence_transformers import SentenceTransformer

# INDEX_NAME = 'combine'
# BM25_WEIGHT = 0.6
# VECTOR_WEIGHT = 1 - BM25_WEIGHT
# SIZE = 100
# RRF_CONSTANT = 60
# es = ElasticsearchConnection.get_instance()
# model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
# router = APIRouter()

# def calculate_rrf_score(bm25_rank, vector_rank, k=60):
#     """
#     คำนวณ RRF score จาก ranking ของ BM25 และ vector search
#     RRF = 1/(k + rank_bm25) + 1/(k + rank_vector)
#     """
#     rrf_bm25 = 1 / (k + bm25_rank) if bm25_rank > 0 else 0
#     rrf_vector = 1 / (k + vector_rank) if vector_rank > 0 else 0
#     return rrf_bm25 + rrf_vector

# @router.get("/search-combine")
# async def search(query: str = Query(None, description="All Table Search")):
#     results = []
#     error_message = None
    
#     try:
#         # ตรวจสอบการเชื่อมต่อ Elasticsearch
#         if not es.ping():
#             error_message = "Cannot connect to Elasticsearch"
#         elif not query or query.strip() == "":
#             # กรณีไม่มี query ให้ดึงข้อมูลทั้งหมด
#             response = es.search(index=INDEX_NAME, body={
#                 "query": {
#                     "match_all": {}
#                 },
#                 "size": 10000
#             })
            
#             if response and 'hits' in response and response['hits']['hits']:
#                 for hit in response['hits']['hits']:
#                     if '_source' in hit:
#                         result = hit["_source"].copy()
#                         result["score"] = hit.get("_score", 0)
#                         results.append(result)
#         else:
#             # Hybrid search with RRF
#             query_vector = None
#             bm25_response = None
#             vector_response = None
            
#             # เข้ารหัส query เป็น vector
#             try:
#                 query_vector = model.encode(query.strip()).tolist()
#             except Exception as e:
#                 error_message = f"Failed to encode query: {str(e)}"
            
#             # ทำ BM25 search
#             if not error_message:
#                 try:
#                     bm25_response = es.search(index=INDEX_NAME, body={
#                         "query": {
#                             "multi_match": {
#                                 "query": query.strip(),
#                                 "fields": ["Name^3", "Category"]
#                             }
#                         },
#                         "size": SIZE
#                     })
#                 except Exception as e:
#                     error_message = f"BM25 search failed: {str(e)}"
            
#             # ทำ Vector search
#             if not error_message and query_vector:
#                 try:
#                     vector_response = es.search(index=INDEX_NAME, body={
#                         "query": {
#                             "knn": {
#                                 "field": "text_vector",
#                                 "query_vector": query_vector,
#                                 "k": SIZE,
#                                 "num_candidates": 200
#                             }
#                         }
#                     })
#                 except Exception as e:
#                     error_message = f"Vector search failed: {str(e)}"
            
#             # ประมวลผล RRF ถ้าไม่มี error
#             if not error_message and (
#                 (bm25_response and bm25_response.get('hits', {}).get('hits')) or 
#                 (vector_response and vector_response.get('hits', {}).get('hits'))
#             ):
#                 # สร้าง ranking dictionaries
#                 bm25_rankings = {}
#                 vector_rankings = {}
#                 all_docs = {}
                
#                 # เก็บ BM25 rankings และข้อมูลเอกสาร
#                 if bm25_response:
#                     for rank, hit in enumerate(bm25_response.get('hits', {}).get('hits', []), 1):
#                         if '_id' in hit and '_source' in hit:
#                             doc_id = hit["_id"]
#                             bm25_rankings[doc_id] = rank
#                             all_docs[doc_id] = hit["_source"].copy()
                
#                 # เก็บ Vector rankings และข้อมูลเอกสาร
#                 if vector_response:
#                     for rank, hit in enumerate(vector_response.get('hits', {}).get('hits', []), 1):
#                         if '_id' in hit and '_source' in hit:
#                             doc_id = hit["_id"]
#                             vector_rankings[doc_id] = rank
#                             if doc_id not in all_docs:
#                                 all_docs[doc_id] = hit["_source"].copy()
                
#                 # คำนวณ RRF scores
#                 if all_docs:
#                     rrf_results = []
#                     for doc_id, doc_data in all_docs.items():
#                         bm25_rank = bm25_rankings.get(doc_id, 0)
#                         vector_rank = vector_rankings.get(doc_id, 0)
                        
#                         # คำนวณ RRF score
#                         rrf_score = calculate_rrf_score(bm25_rank, vector_rank, RRF_CONSTANT)
                        
#                         result = doc_data.copy()
#                         result["score"] = rrf_score
#                         rrf_results.append(result)
                    

#                     results = sorted(rrf_results, key=lambda x: x["score"], reverse=True)
                    
#     except Exception as e:
#         error_message = str(e)
    
#     if error_message:
#         return {"error": error_message}
#     else:
#         return results
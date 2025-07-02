from fastapi import Query, APIRouter,HTTPException
# from elastic_connection import ElasticsearchConnection
from sentence_transformers import SentenceTransformer
import time
from searchtype import SearchType

INDEX_NAME = 'cfo' #ef2

# es = ElasticsearchConnection.get_instance()
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
router = APIRouter()

from elasticsearch import Elasticsearch
es = Elasticsearch(
  "https://14a823faf1c845b0a02f427056f7112c.asia-southeast1.gcp.elastic-cloud.com:443",
  api_key="YlRZaHlaY0JVRzZKbi1obUV0WnM6ZDlPTS13VS1Ja1E2S3M1eUpkSE56QQ==")

@router.get("/search-data_cfo/")
async def search_cfo(
    q: str = Query(None, description="Search query in Thai or English"),
    search_type: SearchType = Query(SearchType.hybrid, description="Search method:")
    ):
    try:
        if not q:
            response = es.search(index=INDEX_NAME, body={
                "query": {
                    "match_all": {}
                },
                "size": 1000
            })
        else:
            if search_type == SearchType.keyword:
                response = es.search(index=INDEX_NAME, body={
                    "query": {
                        "bool": {
                            "should": [
                                # {"term": {"ชื่อ.exact": q}},
                                # {"term": {"รายละเอียด.exact": q}}
                                {"match_phrase": {
                                    "ชื่อ.keyword_search": {
                                        "query": q,
                                        "boost": 2.0
                                    }
                                }},
                                {"match_phrase": {
                                    "รายละเอียด.keyword_search": {
                                        "query": q,
                                        "boost": 1.0
                                    }
                                }}                                
                            ]
                        }
                    }
                })
            elif search_type == SearchType.semantic:
                query_vector = model.encode(q).tolist()
                response = es.search(index=INDEX_NAME,body={
                    "query": {
                        "script_score": {
                            "query": {"match_all":{}},
                            "script":{
                                "source": "cosineSimilarity(params.query_vector, 'text_vector') + 1.0",
                                "params": {
                                    "query_vector": query_vector
                                }
                            }
                        }
                    }
                })
            elif search_type == SearchType.hybrid:
                query_vector = model.encode(q).tolist()
                keyword_query = {
                    "multi_match": {
                        "query":q,
                        "fields": ["ชื่อ.search","รายละเอียด.search"],
                        "operator": "and",
                        "boost": 0.4
                    }
                }

                semantic_search = {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'text_vector') + 1.0",
                            "params": {
                                "query_vector": query_vector
                            }
                        }
                    }
                }

                response = es.search(index=INDEX_NAME,body={
                    "query": {
                        "bool": {
                            "should": [
                                keyword_query,semantic_search
                            ]
                        }
                    }
                })

        unique_results = []
        seen_ids = set()
        for hit in response['hits']['hits']:
            if hit["_id"] not in seen_ids:
                unique_results.append(hit["_source"])
                seen_ids.add(hit["_id"])
                
    except Exception as e:
        return {"error": str(e)}
    
    return unique_results


# @router.get("/autocomplete_cfo/")
# async def autocomplete_cfo(q: str = Query(..., description="Autocomplete query")):
#     """
#     Autocomplete Fuzzy Search
#     """
#     try:
#         response = es.search(index=INDEX_NAME, body={
#             "query": {
#                 "bool": {
#                     "should": [
#                         {
#                             "match_phrase_prefix": {
#                                 "ชื่อ": {
#                                     "query": q
#                                 }
#                             }
#                         },
#                         {
#                             "match": {
#                                 "ชื่อ": {
#                                     "query": q,
#                                     "fuzziness": "AUTO"  #Fuzzy Search
#                                 }
#                             }
#                         },
#                         {
#                             "match_phrase_prefix": { 
#                                 "รายละเอียด": {
#                                     "query": q
#                                 }
#                             }
#                         },
#                         {
#                             "match": {
#                                 "รายละเอียด": {
#                                     "query": q,
#                                     "fuzziness": "AUTO"
#                                 }
#                             }
#                         }
#                     ]
#                 }
#             },
#             "_source": ["ชื่อ","รายละเอียด"],
#             "size": 10
#         })

#         suggestions = [hit["_source"].get("ชื่อ", "N/A") for hit in response['hits']['hits']]
#         return {"suggestions": suggestions}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

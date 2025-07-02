from fastapi import Query, APIRouter,HTTPException
from elastic_connection import ElasticsearchConnection
from sentence_transformers import SentenceTransformer
import time

INDEX_NAME = 'ef1' #cfp

# es = ElasticsearchConnection.get_instance()
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
router = APIRouter()

from elasticsearch import Elasticsearch
es = Elasticsearch(
  "https://14a823faf1c845b0a02f427056f7112c.asia-southeast1.gcp.elastic-cloud.com:443",
  api_key="YlRZaHlaY0JVRzZKbi1obUV0WnM6ZDlPTS13VS1Ja1E2S3M1eUpkSE56QQ==")

@router.get("/search-data_cfp/")
async def search_cfp(q: str = Query(None, description="Search query in Thai or English")):
    try:
        if not q:
            response = es.search(index=INDEX_NAME, body={
                "query": {
                    "match_all": {}
                },
                "size": 1000
            })
        else:
            query_vector = model.encode(q).tolist()
            response = es.search(index=INDEX_NAME, body={
                "query": {
                    "multi_match": {
                        "query": q,
                        "fields": ["ชื่อ^3", "รายละเอียด","กลุ่ม"],
                        # "type": "best_fields",
                        "operator": "and",
                        "analyzer": "thai_autocomplete_analyzer"
                        # "analyzer": "thai_autocomplete_search_analyzer"
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


@router.get("/autocomplete_cfp/")
async def autocomplete_cfp(q: str = Query(..., description="Autocomplete query")):
    """
    Autocomplete พร้อม Fuzzy Search
    """
    try:
        response = es.search(index="ef1", body={
            "query": {
                "bool": {
                    "should": [
                        {
                            "match_phrase_prefix": {
                                "ชื่อ": {
                                    "query": q
                                }
                            }
                        },
                        {
                            "match": {
                                "ชื่อ": {
                                    "query": q,
                                    "fuzziness": "AUTO"  #Fuzzy Search
                                }
                            }
                        },
                        {
                            "match_phrase_prefix": {
                                "รายละเอียด": {
                                    "query": q
                                }
                            }
                        },
                        {
                            "match": {
                                "รายละเอียด": {
                                    "query": q,
                                    "fuzziness": "AUTO"
                                }
                            }
                        }
                    ]
                }
            },
            "_source": ["ชื่อ","รายละเอียด"],
            "size": 10
        })

        suggestions = [hit["_source"].get("ชื่อ", "N/A") for hit in response['hits']['hits']]
        return {"suggestions": suggestions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
from fastapi import Query, APIRouter,HTTPException
from elastic_connection import ElasticsearchConnection
from sentence_transformers import SentenceTransformer
import time
from searchtype import SearchType

INDEX_NAME = 'ef2' #cfo

es = ElasticsearchConnection.get_instance()
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
router = APIRouter()

@router.get("/search-data_cfo/")
async def search_cfo(q: str = Query(None, description="Search query in Thai or English")):
    try:
        if not q:
            response = es.search(index=INDEX_NAME, body={
                "query": {
                    "match_all": {}
                },
                "size": 1000
            })
        else:
            response = es.search(index=INDEX_NAME, body={
                "query": {
                    "multi_match": {
                        "query": q,
                        "fields": ["ชื่อ", "รายละเอียด","กลุ่ม"],
                        # "type": "best_fields",
                        "operator": "and"
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


@router.get("/autocomplete_cfo/")
async def autocomplete_cfo(q: str = Query(..., description="Autocomplete query")):
    """
    Autocomplete Fuzzy Search
    """
    try:
        response = es.search(index=INDEX_NAME, body={
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

from fastapi import Query, APIRouter
from elastic_connection import ElasticsearchConnection
from sentence_transformers import SentenceTransformer


INDEX_NAME = 'keyword_combine_no_synonym'
SIZE = 1000
es = ElasticsearchConnection.get_instance()
router = APIRouter()

@router.get("/search-combine-key-no-synonyms")
async def search(query: str = Query(None, description="All Table Search")):
    try:
        if not query:
            response = es.search(index=INDEX_NAME, body={
                "query": {
                    "match_all": {}
                },
                "size": SIZE*10
            })
        else:
            response = es.search(index=INDEX_NAME, body={
                "query": {
                    "bool": {
                        "should": [
                            {
                                "multi_match": {
                                    "query": query,
                                    "fields": ["Name^2", "Category"],
                                    "type": "best_fields"
                                }
                            }
                        ]
                    }
                },
                "size": SIZE
            })
        
        unique_results = []
        seen_ids = set()
        for hit in response['hits']['hits']:
            if hit["_id"] not in seen_ids:
                result = hit["_source"].copy()
                result["score"] = hit["_score"]
                unique_results.append(result)
                seen_ids.add(hit["_id"])
                
    except Exception as e:
        return {"error": str(e)}
    
    return unique_results


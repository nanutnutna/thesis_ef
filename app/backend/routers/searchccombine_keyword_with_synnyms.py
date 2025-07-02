from fastapi import Query, APIRouter
from elastic_connection import ElasticsearchConnection
from sentence_transformers import SentenceTransformer


INDEX_NAME = 'keyword_combine_with_synonym'
SIZE = 1000
# es = ElasticsearchConnection.get_instance()
router = APIRouter()

from elasticsearch import Elasticsearch
es = Elasticsearch(
  "https://14a823faf1c845b0a02f427056f7112c.asia-southeast1.gcp.elastic-cloud.com:443",
  api_key="YlRZaHlaY0JVRzZKbi1obUV0WnM6ZDlPTS13VS1Ja1E2S3M1eUpkSE56QQ==")

@router.get("/search-combine-key-synonyms")
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


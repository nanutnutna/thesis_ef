from fastapi import Query, APIRouter
# from elastic_connection import ElasticsearchConnection
from sentence_transformers import SentenceTransformer

INDEX_NAME = 'cfp_label'
BM25_WEIGHT = 0.6
VECTOR_WEIGHT = 1 - BM25_WEIGHT

# es = ElasticsearchConnection.get_instance()
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')


from elasticsearch import Elasticsearch
es = Elasticsearch(
  "https://14a823faf1c845b0a02f427056f7112c.asia-southeast1.gcp.elastic-cloud.com:443",
  api_key="YlRZaHlaY0JVRzZKbi1obUV0WnM6ZDlPTS13VS1Ja1E2S3M1eUpkSE56QQ==")

router = APIRouter()
@router.get("/search-cfplabel")
async def search(query: str = Query(None, description="CFP-Label Search")):
    try:
        #query
        if not query:
            response = es.search(index=INDEX_NAME, body={
                "query": {
                    "match_all": {}
                },
                "size": 2000
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
                                    "fields": ["Name^3","Industrials"],
                                    "boost": BM25_WEIGHT
                                }
                            },
                            {
                                "knn": {
                                    "field" : "text_vector",
                                    "query_vector": query_vector,
                                    "k": 15,
                                    "num_candidates": 100,
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
                unique_results.append(hit["_source"])
                seen_ids.add(hit["_id"])
                
    except Exception as e:
        return {"error": str(e)}
    
    return unique_results
from fastapi import Query, APIRouter
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

INDEX_NAME = 'test_elastic_cloud'
model = SentenceTransformer('intfloat/multilingual-e5-base')
es = Elasticsearch(
  "https://17a1b0bc419b499eb33a40065d65170d.asia-southeast1.gcp.elastic-cloud.com:443",
  api_key="cm1kMmpKY0I4c1o0ckNSSzJmNjk6aVM5eE9iVUpuX25YRHhQbXNqd20xZw=="
)

router = APIRouter()

@router.get("/search-cloud")
async def search(query: str = Query(None, description="CFP-Label Search")):
    try:
        if not query:
            response = es.search(index=INDEX_NAME, body={
                "retriever": {
                    "standard": {
                        "query": {
                            "match_all": {}
                        }
                    }
                },
                "size": 2000
            })
        else:
            query_vector = model.encode(query).tolist()
            
            # ใช้ Retriever RRF
            response = es.search(index=INDEX_NAME, body={
                "retriever": {
                    "rrf": {
                        "retrievers": [
                            {
                                "standard": {
                                    "query": {
                                        "multi_match": {
                                            "query": query,
                                            "fields": ["Name^2", "Category"]
                                        }
                                    }
                                }
                            },
                            {
                                "knn": {
                                    "field": "text_vector",
                                    "query_vector": query_vector,
                                    "k": 50,
                                    "num_candidates": 100
                                }
                            }
                        ],
                        "rank_window_size": 100,  # จำนวน docs ที่นำมาคำนวณ RRF
                        "rank_constant": 60       # ค่า k ใน RRF formula
                    }
                },
                "size": 50
            })
        
        results = [hit["_source"] for hit in response['hits']['hits']]
        
    except Exception as e:
        return {"error": str(e)}
    
    return results
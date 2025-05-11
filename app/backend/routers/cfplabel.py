from fastapi import Query, APIRouter
from elastic_connection import ElasticsearchConnection


INDEX_NAME = 'cfp_label'

es = ElasticsearchConnection.get_instance()

router = APIRouter()
@router.get("/search-cfplabel")
async def search(query: str = Query(None, description="CFP-Label Search",example="ก๊าซหุงต้ม")):
    try:
        #query
        if not query:
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
                        "query": query,
                        "fields": ["License^3","Name^2", "Detail","Industrials"],
                        "operator": "and",
                        "analyzer": "thai_eng_analyzer"
                    }
                }
            })
        
        # จัดการผลลัพธ์
        unique_results = []
        seen_ids = set()
        for hit in response['hits']['hits']:
            if hit["_id"] not in seen_ids:
                unique_results.append(hit["_source"])
                seen_ids.add(hit["_id"])
                
    except Exception as e:
        return {"error": str(e)}
    
    return unique_results
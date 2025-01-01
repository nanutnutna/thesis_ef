from fastapi import APIRouter,HTTPException
from elasticsearch import Elasticsearch
from app.backend.schemas import Document

router = APIRouter()
es = Elasticsearch("https://localhost:9200",
                   basic_auth=("elastic","JODDaUKomoKuPHFM2zEc"),
                   ca_certs="C:/Users/Nattapot/Documents/elasticsearch-8.17.0/config/certs/http_ca.crt"
)

INDEX_NAME = "document"

@router.post("/index")
async def index_document(doc: Document):
    response = es.index(index=INDEX_NAME,document=doc.dict())
    return {"message": "Document indexed successfully", "id":response['_id']}

@router.get("/search")
async def search_document(q: str):
    response = es.search(index=INDEX_NAME,body={
        "query":{
            "multi_match": {
                "query":q,
                "fields": ["title","content"]
            }
        }
    })
    results = [
        {"id":hit['_id'],"title":hit["_source"]["title"],"content":hit["_source"]["content"]}
        for hit in response['hits']['hits']
    ]
    return results
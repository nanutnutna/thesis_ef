from fastapi import HTTPException,Query, APIRouter
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()
CLOUD_ID = os.getenv("ELASTIC_CLOUD_ID")
API_KEY = os.getenv("ELASTIC_API_KEY")
INDEX_NAME = 'thai_hybrid_search_ef'
INDEX_NAME2 = 'hybrid_search_ef'
es = Elasticsearch(cloud_id=CLOUD_ID,api_key=API_KEY)
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')


FIELDS = ["ชื่อ^3", "รายละเอียด^2"]
BM25_WEIGHT = 0.6
VECTOR_WEIGHT = 1 - BM25_WEIGHT
SEARCH_SIZE = 10

# class SearchRequest(BaseModel):
#     query: str
#     fields: Optional[List[str]] = ["ชื่อ^3", "รายละเอียด^2"]
#     bm25_weight: Optional[float] = 0.5
#     vector_weight: Optional[float] = 0.5
#     size: Optional[int] = 10

class SearchResponse(BaseModel):
    total: int
    took: float
    results: List[Dict[str, Any]]

class EncodeRequest(BaseModel):
    text: str

class EncodeResponse(BaseModel):
    vector: List[float]


router = APIRouter()
@router.get("/hybrid-search")
async def search(query: str = Query(...,description="Hybrid Search",example="ก๊าซหุงต้ม")):
    try:
        # สร้าง embedding สำหรับคำค้นหา
        query_vector = model.encode(query).tolist()
        
        # สร้าง query แบบ hybrid
        search_query = {
            "query": {
                "bool": {
                    "should": [
                        # BM25 search - จะใช้ synonyms จาก analyzer ที่กำหนดไว้
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["ชื่อ^3", "รายละเอียด^2"],
                                "boost": BM25_WEIGHT
                            }
                        },
                        # Vector search
                        # {
                        #     "script_score": {
                        #         "query": {"match_all": {}},
                        #         "script": {
                        #             "source": "cosineSimilarity(params.query_vector, 'text_vector') + 1.0",
                        #             "params": {
                        #                 "query_vector": query_vector
                        #             }
                        #         },
                        #         "boost": 0.5 #vector_weight
                        #     }
                        # }
                        
                        # Vector search ใช้ knn_vector แทน script_score
                        {
                            "knn": {
                                "field": "text_vector",
                                "query_vector": query_vector,
                                "k": 10,
                                "num_candidates": 100,
                                "boost": VECTOR_WEIGHT
                            }
                        }                        
                    ]
                }
            },
            "size": SEARCH_SIZE #size
        }
        
        # ส่งคำขอค้นหาไปยัง Elasticsearch
        start_time = time.time()
        response = es.search(index=INDEX_NAME, body=search_query)
        end_time = time.time()
        
        # แปลงผลลัพธ์ให้อยู่ในรูปแบบที่ต้องการ
        results = []
        for hit in response["hits"]["hits"]:
            no_vector = {k: v for k, v in hit["_source"].items() if k not in ["text_vector","context_vector"]}
            result = {
                "id": hit["_id"],
                "score": hit["_score"],
                **no_vector
                #**hit["_source"]  # แยกข้อมูลทั้งหมดจาก _source
            }
            results.append(result)
        
        # สร้าง response
        return {
            "total": response["hits"]["total"]["value"],
            "took": end_time - start_time,
            "results": results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")
    

@router.get("/hybrid-search-rrf") 
async def search_rrf(query: str = Query(..., description="Hybrid Search with RRF", example="ก๊าซหุงต้ม")):
    try:
        # สร้าง embedding สำหรับคำค้นหา
        query_vector = model.encode(query).tolist()
        
        # สร้าง query แบบ RRF ตามไวยากรณ์ของ Elasticsearch 8.x
        search_query = {
            "size": 5,
            "retriever": {
                "rrf": {
                    "retrievers": [
                        {
                            "standard": {
                                "query": {
                                    "multi_match": {
                                        "query": query,
                                        "fields": ["ชื่อ^3", "รายละเอียด^2"]
                                    }
                                }
                            }
                        },
                        {
                            "knn": {
                                "field": "text_vector",
                                "query_vector": query_vector,
                                "k": 10,
                                "num_candidates": 100
                            }
                        }
                    ],
                    "rank_window_size": 10,
                    "rank_constant": 20
                }
            }
        }
        
        # ส่งคำขอค้นหาไปยัง Elasticsearch
        start_time = time.time()
        response = es.search(index=INDEX_NAME2, body=search_query)
        end_time = time.time()
        
        # แปลงผลลัพธ์ให้อยู่ในรูปแบบที่ต้องการ
        results = []
        for hit in response["hits"]["hits"]:
            no_vector = {k: v for k, v in hit["_source"].items() if k != "text_vector"}
            result = {
                "id": hit["_id"],
                "score": hit["_score"],
                **no_vector
            }
            results.append(result)

        return {
            "total": response["hits"]["total"]["value"],
            "took": end_time - start_time,
            "results": results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.post("/encode", response_model=EncodeResponse)
async def encode_text(request: EncodeRequest):
    try:
        vector = model.encode(request.text).tolist()
        return {"vector": vector}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการสร้าง vector: {str(e)}")
    
@router.get("/health")
async def health_check():
    try:
        if es.ping():
            return {"status": "ok", "elasticsearch": "connected"}
        else:
            return {"status": "error", "elasticsearch": "disconnected"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
@router.get("/index-info")
async def get_index_info():
    try:
        index_exists = es.indices.exists(index=INDEX_NAME)
        if not index_exists:
            return {"status": "error", "message": f"Index {INDEX_NAME} ไม่มีอยู่"}
        
        index_stats = es.indices.stats(index=INDEX_NAME)
        index_settings = es.indices.get_settings(index=INDEX_NAME)
        index_mapping = es.indices.get_mapping(index=INDEX_NAME)
        
        return {
            "name": INDEX_NAME,
            "exists": True,
            "doc_count": index_stats["indices"][INDEX_NAME]["total"]["docs"]["count"],
            "size_in_bytes": index_stats["indices"][INDEX_NAME]["total"]["store"]["size_in_bytes"],
            "settings": index_settings[INDEX_NAME]["settings"],
            "mappings": index_mapping[INDEX_NAME]["mappings"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")
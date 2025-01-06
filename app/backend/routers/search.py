from fastapi import APIRouter,HTTPException,UploadFile,Query
from elasticsearch import Elasticsearch
import pandas as pd
from io import BytesIO
from schemas import Document
import numpy as np

router = APIRouter()
es = Elasticsearch("https://localhost:9200",
                   basic_auth=("elastic","JODDaUKomoKuPHFM2zEc"),
                   ca_certs="C:/Users/Nattapot/Documents/elasticsearch-8.17.0/config/certs/http_ca.crt"
)

INDEX_NAME = "document_data"

index_settings = {
    "settings": {
        "analysis": {
            "filter": {
                "thai_english_synonym_filter": {
                    "type": "synonym",
                    "synonyms_path": "analysis/synonyms.txt"
                }
            },
            "analyzer": {
                "thai_english_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "icu_folding",
                        "thai_english_synonym_filter"
                    ]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "ลำดับ": {
                "type": "float"
            },
            "ชื่อ": {
                "type": "text",
                "analyzer": "thai_english_analyzer"
            },
            "หน่วย": {
                "type": "text"
            },
            "Total [kg CO2eq/unit]": {
                "type": "float"
            },
            "ข้อมูลอ้างอิง": {
                "type": "text",
                "analyzer": "thai_english_analyzer"
            },
            "Description": {
                "type": "text",
                "analyzer": "thai_english_analyzer"
            }
        }
    }
}

if es.indices.exists(index=INDEX_NAME):
    print(f"Deleting existing index: {INDEX_NAME}")
    es.indices.delete(index=INDEX_NAME)

try:
    es.indices.create(index=INDEX_NAME, body=index_settings)
    print(f"Successfully created index: {INDEX_NAME}")
except Exception as e:
    print(f"Error creating index: {e}")



############# CFO #######
@router.post("/upload-data/")
async def upload_data(file: UploadFile):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    content = await file.read()
    try:
        df = pd.read_csv(BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV: {str(e)}")
    
    # Replace NaN with None for Elasticsearch compatibility
    df.replace({np.nan: None}, inplace=True)
    
    # Insert documents into Elasticsearch
    for _, row in df.iterrows():
        document = {
            "ลำดับ": row.get("ลำดับ"),
            "ชื่อ": row.get("ชื่อ"),
            "หน่วย": row.get("หน่วย"),
            "Total [kg CO2eq/unit]": row.get("Total [kg CO2eq/unit]"),
            "ข้อมูลอ้างอิง": row.get("ข้อมูลอ้างอิง"),
            "Description": row.get("Description")
        }
        es.index(index=INDEX_NAME, document=document)
    
    return {"message": "Data uploaded successfully"}


@router.post("/index/")
async def index_document(doc: dict):
    document = {
        "ลำดับ": doc.get("ลำดับ"),
        "ชื่อ": doc.get("ชื่อ"),
        "หน่วย": doc.get("หน่วย"),
        "Total [kg CO2eq/unit]": doc.get("Total [kg CO2eq/unit]"),
        "ข้อมูลอ้างอิง": doc.get("ข้อมูลอ้างอิง"),
        "Description": doc.get("Description")
    }
    response = es.index(index=INDEX_NAME, document=document)
    return {"message": "Document indexed successfully", "id": response['_id']}

@router.get("/search-data/")
async def search(q: str = Query(..., description="Search query in Thai or English")):
    try:
        response = es.search(index=INDEX_NAME, body={
            "query": {
                "multi_match": {
                    "query": q,
                    "fields": ["ชื่อ", "Description", "ข้อมูลอ้างอิง"],
                    "operator": "and"
                }
            }
        })

        unique_results = []
        seen_ids = set()
        for hit in response['hits']['hits']:
            if hit["_id"] not in seen_ids:
                unique_results.append({
                    "id": hit["_id"],
                    "ลำดับ": hit["_source"].get("ลำดับ", "N/A"),
                    "ชื่อ": hit["_source"].get("ชื่อ", "N/A"),
                    "หน่วย": hit["_source"].get("หน่วย", "N/A"),
                    "Total [kg CO2eq/unit]": hit["_source"].get("Total [kg CO2eq/unit]", "N/A"),
                    "ข้อมูลอ้างอิง": hit["_source"].get("ข้อมูลอ้างอิง", "N/A"),
                    "Description": hit["_source"].get("Description", "N/A")
                })
                seen_ids.add(hit["_id"])
    except Exception as e:
        return {"error": str(e)}
    
    return unique_results










############# CFP ########
# @router.post("/upload-data/")
# async def upload_data(file: UploadFile):
#     if not file.filename.endswith('.csv'):
#         raise HTTPException(status_code=400,detail="Only CSV file")

#     content = await file.read()
#     if file.filename.endswith(".csv"):
#         df = pd.read_csv(BytesIO(content))

#     df.replace({np.nan: None}, inplace=True)
    
#     for _,row in df.iterrows():
#         document = {
#             "กลุ่ม": row["กลุ่ม"],
#             "ลำดับ": row["ลำดับ"],
#             "ชื่อ": row["ชื่อ"],
#             "รายละเอียด": row["รายละเอียด"],
#             "หน่วย": row["หน่วย"],
#             "ค่าแฟคเตอร์ (kgCO2e)": row["ค่าแฟคเตอร์ (kgCO2e)"],
#             "ข้อมูลอ้างอิง": row["ข้อมูลอ้างอิง"],
#             "วันที่อัพเดท": row["วันที่อัพเดท"]           
#         }
#         es.index(index=INDEX_NAME,document=document)

#     return {"message":"Datas uploaded successfully"}

# @router.post("/index")
# async def index_document(doc: Document):
#     response = es.index(index=INDEX_NAME,document=doc.dict())
#     return {"message": "Document indexed successfully", "id":response['_id']}

# @router.get("/search-data/")
# async def search(q: str = Query(..., description="Search query in Thai or English")):
#     try:
#         response = es.search(index=INDEX_NAME,body={
#             "query":{
#                 "multi_match": {
#                     "query":q,
#                     "fields": ["ชื่อ", "รายละเอียด", "กลุ่ม","ข้อมูลอ้างอิง"],
#                     "operator": "and"
#                 }
#             }
#         })

#         unique_results = []
#         seen_ids = set()
#         for hit in response['hits']['hits']:
#             if hit["_id"] not in seen_ids:
#                 unique_results.append({
#                     "id": hit["_id"],
#                     "กลุ่ม": hit["_source"].get("กลุ่ม", "N/A"),
#                     "ลำดับ": hit["_source"].get("ลำดับ", "N/A"),
#                     "ชื่อ": hit["_source"].get("ชื่อ", "N/A"),
#                     "รายละเอียด": hit["_source"].get("รายละเอียด", "N/A"),
#                     "หน่วย": hit["_source"].get("หน่วย", "N/A"),
#                     "ค่าแฟคเตอร์ (kgCO2e)": hit["_source"].get("ค่าแฟคเตอร์ (kgCO2e)", "N/A"),
#                     "ข้อมูลอ้างอิง": hit["_source"].get("ข้อมูลอ้างอิง", "N/A"),
#                     "วันที่อัพเดท": hit["_source"].get("วันที่อัพเดท", "N/A")
#                 })
#                 seen_ids.add(hit["_id"])
#     except Exception as e:
#         return {"error":str(e)}
#     return unique_results
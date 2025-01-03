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

## creat mapping and index thai
if not es.indices.exists(index=INDEX_NAME):
    es.indices.create(index=INDEX_NAME,body={
        "mappings":{
            "properties":{
                "กลุ่ม":{"type":"text"},
                "ลำดับ":{"type":"float"},
                "ชื่อ":{"type":"text"},
                "รายละเอียด":{"type":"text"},
                "หน่วย":{"type":"text"},
                "ค่าแฟคเตอร์ (kgCO2e)":{"type":"float"},
                "ข้อมูลอ่างอิง":{"type":"text"},
                "วันที่อัพเดท":{"type":"text"}
            }
        }
    })

@router.post("/upload-data/")
async def upload_data(file: UploadFile):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400,detail="Only CSV file")

    content = await file.read()
    if file.filename.endswith(".csv"):
        df = pd.read_csv(BytesIO(content))

    df.replace({np.nan: None}, inplace=True)
    
    for _,row in df.iterrows():
        document = {
            "กลุ่ม": row["กลุ่ม"],
            "ลำดับ": row["ลำดับ"],
            "ชื่อ": row["ชื่อ"],
            "รายละเอียด": row["รายละเอียด"],
            "หน่วย": row["หน่วย"],
            "ค่าแฟคเตอร์ (kgCO2e)": row["ค่าแฟคเตอร์ (kgCO2e)"],
            "ข้อมูลอ้างอิง": row["ข้อมูลอ้างอิง"],
            "วันที่อัพเดท": row["วันที่อัพเดท"]           
        }
        es.index(index=INDEX_NAME,document=document)

    return {"message":"Datas uploaded successfully"}

@router.post("/index")
async def index_document(doc: Document):
    response = es.index(index=INDEX_NAME,document=doc.dict())
    return {"message": "Document indexed successfully", "id":response['_id']}

@router.get("/search-data/")
async def search(q: str = Query(..., description="Search query in Thai or English")):
    response = es.search(index=INDEX_NAME,body={
        "query":{
            "multi_match": {
                "query":q,
                "fields": ["ชื่อ", "รายละเอียด", "กลุ่ม"]
            }
        }
    })

    unique_results = []
    seen_ids = set()
    for hit in response['hits']['hits']:
        if hit["_id"] not in seen_ids:
            unique_results.append({
                "id": hit["_id"],
                "กลุ่ม": hit["_source"].get("กลุ่ม", "N/A"),
                "ลำดับ": hit["_source"].get("ลำดับ", "N/A"),
                "ชื่อ": hit["_source"].get("ชื่อ", "N/A"),
                "รายละเอียด": hit["_source"].get("รายละเอียด", "N/A"),
                "หน่วย": hit["_source"].get("หน่วย", "N/A"),
                "ค่าแฟคเตอร์ (kgCO2e)": hit["_source"].get("ค่าแฟคเตอร์ (kgCO2e)", "N/A"),
                "ข้อมูลอ้างอิง": hit["_source"].get("ข้อมูลอ้างอิง", "N/A"),
                "วันที่อัพเดท": hit["_source"].get("วันที่อัพเดท", "N/A")
            })
            seen_ids.add(hit["_id"])
    return unique_results
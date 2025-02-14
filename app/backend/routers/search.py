from fastapi import APIRouter,HTTPException,UploadFile,Query
from elasticsearch import Elasticsearch
import pandas as pd
from io import BytesIO
from schemas import Document
import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings
import datetime

router = APIRouter()
# es = Elasticsearch("https://localhost:9200",
#                    basic_auth=("elastic","JODDaUKomoKuPHFM2zEc"),
#                    ca_certs="C:/Users/Nattapot/Documents/elasticsearch-8.17.0/config/certs/http_ca.crt"
# )

es = Elasticsearch(
    "https://201b20f220fd4642a18ad35f13021fe5.asia-southeast1.gcp.elastic-cloud.com:443",
    api_key="Um5jU0FKVUJLcWtQQjJ6NzRNa2Q6MzhwRzNIaHVTdXVIOGZVSm16TElGQQ=="
)

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

INDEX_NAME = "ef1"


@router.get("/creation-date")
def get_creation_date():
    try:
        response = es.indices.get(index="emission_data")
        # ดึงค่า creation_date
        creation_date = int(response["emission_data"]["settings"]["index"]["creation_date"])
        
        # แปลง creation_date จาก epoch time (ms) เป็นวันที่
        creation_date_seconds = creation_date / 1000
        date = datetime.datetime.fromtimestamp(creation_date_seconds)

        return {"creation_date": date.strftime('%Y-%m-%d %H:%M:%S')}
    except Exception as e:
        return {"error": str(e)}



@router.get("/available-dates/")
async def available_dates():
    try:
        indices = es.cat.indices(index="emission_data_*", format="json")
        dates = [index["index"].split("_")[-1] for index in indices]
        return {"dates": dates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/upload-data/{index_name}")
async def upload_data(file: UploadFile,index_name: str):
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
    try:
        if index_name == "document_data":
            for _, row in df.iterrows():
                document = {
                    "ลำดับ": row.get("ลำดับ"),
                    "ชื่อ": row.get("ชื่อ"),
                    "หน่วย": row.get("หน่วย"),
                    "Total [kg CO2eq/unit]": row.get("Total [kg CO2eq/unit]"),
                    "ข้อมูลอ้างอิง": row.get("ข้อมูลอ้างอิง"),
                    "Description": row.get("Description")
                }
                es.index(index=index_name, document=document)
        elif index_name in ["ef1","ef2"]:
            for _,row in df.iterrows():
                document = {
                    "กลุ่ม": row.get("กลุ่ม"),
                    "ลำดับ": row.get("ลำดับ"),
                    "ชื่อ": row.get("ชื่อ"),
                    "รายละเอียด": row.get("รายละเอียด"),
                    "หน่วย": row.get("หน่วย"),
                    "ค่าแฟคเตอร์ (kgCO2e)": row.get("ค่าแฟคเตอร์ (kgCO2e)"),
                    "ข้อมูลอ้างอิง": row.get("ข้อมูลอ้างอิง"),
                    "วันที่อัพเดท": row.get("วันที่อัพเดท")
                }
                es.index(index=index_name,document=document)
        elif index_name == "ef3":
            for _,row in df.iterrows():
                document = {
                    "เลขที่ใบรับรอง": row.get("เลขที่ใบรับรอง"),
                    "ชื่อ": row.get("ชื่อ"),
                    "รายละเอียด": row.get("รายละเอียด"),
                    "กลุ่ม": row.get("กลุ่ม"),
                    "วันที่อนุมัติ": row.get("วันที่อนุมัติ"),
                    "CF": row.get("CF"),
                    "หน่วยการทำงาน": row.get("หน่วยการทำงาน"),
                    "ขอบเขต": row.get("ขอบเขต"),
                    "img_path": row.get("img_path")
                }
                es.index(index=index_name,document=document)
        elif index_name == "emission_data_upsert":
            for _, row in df.iterrows():
                document = {
                    "_op_type": "index",
                    "_index": index_name,
                    "_id": row["ลำดับ"],
                    "_source": {
                        "กลุ่ม": row["กลุ่ม"],
                        "ชื่อ": row["ชื่อ"],
                        "รายละเอียด": row["รายละเอียด"],
                        "หน่วย": row["หน่วย"],
                        "ค่าแฟคเตอร์ (kgCO2e)": row["ค่าแฟคเตอร์ (kgCO2e)"],
                        "ข้อมูลอ้างอิง": row["ข้อมูลอ้างอิง"],
                        "วันที่อัพเดท": row["วันที่อัพเดท"],
                        "ประเภทแฟคเตอร์": row["ประเภทแฟคเตอร์"],
                        "เปลี่ยนแปลง": row["เปลี่ยนแปลง"]
                    }
                }
                es.index(index=document["_index"], id=document["_id"], document=document["_source"])
        else:
            raise HTTPException(status_code=400,detail=f"Index {index_name} is not supported")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload data: {str(e)}")
        
    return {"message": "Data uploaded successfully"}


@router.post("/index/")
async def index_document(doc: dict):
    document = {
        "กลุ่ม": doc.get("กลุ่ม"),
        "ลำดับ": doc.get("ลำดับ"),
        "ชื่อ": doc.get("ชื่อ"),
        "รายละเอียด": doc.get("รายละเอียด"),
        "หน่วย": doc.get("หน่วย"),
        "ค่าแฟคเตอร์ (kgCO2e)": doc.get("ค่าแฟคเตอร์ (kgCO2e)"),
        "ข้อมูลอ้างอิง": doc.get("ข้อมูลอ้างอิง"),
        "วันที่อัพเดท": doc.get("วันที่อัพเดท")
    }
    response = es.index(index=INDEX_NAME, document=document)
    return {"message": "Document indexed successfully", "id": response['_id']}



######################################## ef1 CFP(Global) ####################################################
@router.get("/search-data_cfp/")
async def search_cfp(q: str = Query(None, description="Search query in Thai or English")):
    try:
        if not q:
            # กรณีไม่มีคำค้นหา แสดงข้อมูลทั้งหมด
            response = es.search(index="ef1", body={
                "query": {
                    "match_all": {}
                },
                "size": 1000
            })
        else:
            # กรณีมีคำค้นหา
            response = es.search(index="ef1", body={
                "query": {
                    "multi_match": {
                        "query": q,
                        "fields": ["ชื่อ^3", "รายละเอียด","กลุ่ม"],
                        # "type": "best_fields",
                        "operator": "and",
                        "analyzer": "thai_autocomplete_analyzer"
                        # "analyzer": "thai_autocomplete_search_analyzer"
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


@router.get("/autocomplete_cfp/")
async def autocomplete_cfp(q: str = Query(..., description="Autocomplete query")):
    """
    Autocomplete พร้อม Fuzzy Search
    """
    try:
        response = es.search(index="ef1", body={
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
                                    "fuzziness": "AUTO"  # เปิดใช้งาน Fuzzy Search
                                }
                            }
                        },
                        {
                            "match_phrase_prefix": { ### เพิ่มฟิลด์รายละเอียดด้วย
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
            "_source": ["ชื่อ","รายละเอียด"], ##เพิ่มรายละเอียด
            "size": 10
        })

        suggestions = [hit["_source"].get("ชื่อ", "N/A") for hit in response['hits']['hits']]
        return {"suggestions": suggestions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


######################################## ef2 CFO ########################################
@router.get("/search-data_cfo/")
async def search_cfo(q: str = Query(None, description="Search query in Thai or English")):
    try:
        if not q:
            # กรณีไม่มีคำค้นหา แสดงข้อมูลทั้งหมด
            response = es.search(index="ef2", body={
                "query": {
                    "match_all": {}
                },
                "size": 1000
            })
        else:
            # กรณีมีคำค้นหา
            response = es.search(index="ef2", body={
                "query": {
                    "multi_match": {
                        "query": q,
                        "fields": ["ชื่อ", "รายละเอียด","กลุ่ม"],
                        # "type": "best_fields",
                        "operator": "and"
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


@router.get("/autocomplete_cfo/")
async def autocomplete_cfo(q: str = Query(..., description="Autocomplete query")):
    """
    Autocomplete พร้อม Fuzzy Search
    """
    try:
        response = es.search(index="ef2", body={
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
                                    "fuzziness": "AUTO"  # เปิดใช้งาน Fuzzy Search
                                }
                            }
                        },
                        {
                            "match_phrase_prefix": { ### เพิ่มฟิลด์รายละเอียดด้วย
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
            "_source": ["ชื่อ","รายละเอียด"], ##เพิ่มรายละเอียด
            "size": 10
        })

        suggestions = [hit["_source"].get("ชื่อ", "N/A") for hit in response['hits']['hits']]
        return {"suggestions": suggestions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



######################################## ef3 Carbon label products ####################################################

@router.get("/search-data_clp/")
async def search_clp(q: str = Query(None, description="Search query in Thai or English")):
    try:
        if not q:
            # กรณีไม่มีคำค้นหา แสดงข้อมูลทั้งหมด
            response = es.search(index="ef3", body={
                "query": {
                    "match_all": {}
                },
                "size": 1000
            })
        else:
            # กรณีมีคำค้นหา
            response = es.search(index="ef3", body={
                "query": {
                    "multi_match": {
                        "query": q,
                        "fields": ["ชื่อ","กลุ่ม"],
                        "type": "best_fields",
                        "operator": "and"
                        #"analyzer": "thai_autocomplete_search_analyzer"
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


@router.get("/autocomplete_clp/")
async def autocomplete_clp(q: str = Query(..., description="Autocomplete query")):
    """
    Autocomplete พร้อม Fuzzy Search
    """
    try:
        response = es.search(index="ef3", body={
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
                                    "fuzziness": "AUTO"  # เปิดใช้งาน Fuzzy Search
                                }
                            }
                        },
                        {
                            "match_phrase_prefix": { ### เพิ่มฟิลด์รายละเอียดด้วย
                                "กลุ่ม": {
                                    "query": q
                                }
                            }
                        },
                        {
                            "match": {
                                "กลุ่ม": {
                                    "query": q,
                                    "fuzziness": "AUTO"
                                }
                            }
                        }
                    ]
                }
            },
            "_source": ["ชื่อ","รายละเอียด"], ##เพิ่มรายละเอียด
            "size": 10
        })

        suggestions = [hit["_source"].get("ชื่อ", "N/A") for hit in response['hits']['hits']]
        return {"suggestions": suggestions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


######################################## ef1+2####################################################
@router.get("/search-data_combine/")
async def search_cfp(q: str = Query(None, description="Search query in Thai or English")):
    try:
        if not q:
            # กรณีไม่มีคำค้นหา แสดงข้อมูลทั้งหมด
            response = es.search(index="emission_data_upsert", body={
                "query": {
                    "match_all": {}
                },
                "size": 1000
            })
        else:
            # กรณีมีคำค้นหา
            response = es.search(index="emission_data_upsert", body={
                "query": {
                    "multi_match": {
                        "query": q,
                        "fields": ["ชื่อ^3", "รายละเอียด","กลุ่ม"],
                        "type": "best_fields",
                        "operator": "and"
                        # "analyzer": "thai_autocomplete_analyzer"
                        # "analyzer": "thai_synonym_analyzer"
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


@router.get("/autocomplete_combine/")
async def autocomplete_cfp(q: str = Query(..., description="Autocomplete query")):
    """
    Autocomplete พร้อม Fuzzy Search
    """
    try:
        response = es.search(index="emission_data_upsert", body={
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
                                    "fuzziness": "AUTO"  # เปิดใช้งาน Fuzzy Search
                                }
                            }
                        },
                        {
                            "match_phrase_prefix": { ### เพิ่มฟิลด์รายละเอียดด้วย
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
            "_source": ["ชื่อ","รายละเอียด"], ##เพิ่มรายละเอียด
            "size": 10
        })

        suggestions = [hit["_source"].get("ชื่อ", "N/A") for hit in response['hits']['hits']]
        return {"suggestions": suggestions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



######################################## Embeddings ####################################################

@router.get("/search-embedding/")
async def search_with_embedding(q: str = Query(None, description="Search query in Thai or English")):
    try:
        if not q:
            # กรณีไม่มีคำค้นหา แสดงข้อมูลทั้งหมด
            response = es.search(
                index="emission_data_upsert",
                body={
                    "query": {"match_all": {}},
                    "size": 1000
                }
            )
        else:
            # กรณีมีคำค้นหา
            question_embedding = embedding_model.embed_query(q)

            response = es.search(
                index="emission_data_upsert_embedding",
                body={
                    "_source": ["ชื่อ", "รายละเอียด", "กลุ่ม", "ค่าแฟคเตอร์ (kgCO2e)"],
                    "query": {
                        "script_score": {
                            "query": {"match_all": {}},
                            "script": {
                                "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                                "params": {"query_vector": question_embedding}
                            }
                        }
                    },
                    "size": 100  # จำนวนผลลัพธ์ที่ต้องการ
                }
            )

        # จัดการผลลัพธ์
        unique_results = []
        seen_ids = set()
        for hit in response['hits']['hits']:
            if hit["_id"] not in seen_ids:
                unique_results.append(hit["_source"])
                seen_ids.add(hit["_id"])

        return unique_results

    except Exception as e:
        return {"error": str(e)}
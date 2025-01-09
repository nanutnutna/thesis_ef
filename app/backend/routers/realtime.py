from fastapi import APIRouter,WebSocket,WebSocketDisconnect
from elasticsearch import Elasticsearch

router = APIRouter()
es = Elasticsearch("https://localhost:9200",
                   basic_auth=("elastic","JODDaUKomoKuPHFM2zEc"),
                   ca_certs="C:/Users/Nattapot/Documents/elasticsearch-8.17.0/config/certs/http_ca.crt"
)

INDEX_NAME = "document_data"


@router.websocket("/ws/search")
async def websocket_search(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connected")
    try:
        while True:
            q = await websocket.receive_text()
            print(f"Query received: {q}")
            response = es.search(index=INDEX_NAME,body={
            "query":{
                "multi_match": {
                    "query":q,
                    "fields": ["ชื่อ", "รายละเอียด", "กลุ่ม","ข้อมูลอ้างอิง"],
                    "operator": "and"
                }
            }
        })
            results = [
                {
                    "id": hit["_id"],
                    "กลุ่ม": hit["_source"].get("กลุ่ม", "N/A"),
                    "ลำดับ": hit["_source"].get("ลำดับ", "N/A"),
                    "ชื่อ": hit["_source"].get("ชื่อ", "N/A"),
                    "รายละเอียด": hit["_source"].get("รายละเอียด", "N/A"),
                    "หน่วย": hit["_source"].get("หน่วย", "N/A"),
                    "ค่าแฟคเตอร์ (kgCO2e)": hit["_source"].get("ค่าแฟคเตอร์ (kgCO2e)", "N/A"),
                    "ข้อมูลอ้างอิง": hit["_source"].get("ข้อมูลอ้างอิง", "N/A"),
                    "วันที่อัพเดท": hit["_source"].get("วันที่อัพเดท", "N/A")
                }
                for hit in response['hits']['hits']
            ]
            await websocket.send_json({"results": results})
    except WebSocketDisconnect:
        print("WebSocket disconnected")
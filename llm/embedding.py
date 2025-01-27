import pandas as pd
from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

# ตั้งค่าโมเดล Embedding
embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

# ตั้งค่า Elasticsearch
es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", "JODDaUKomoKuPHFM2zEc"),
    ca_certs="C:/Users/Nattapot/Documents/elasticsearch-8.17.0/config/certs/http_ca.crt"
)


df = pd.read_csv('emission_factor_20250127.csv')
df['ชื่อ'] = df['ชื่อ'].fillna("").astype(str)
df['รายละเอียด'] = df['รายละเอียด'].fillna("").astype(str)
df['กลุ่ม'] = df['กลุ่ม'].fillna("").astype(str)
df['combined_text'] = df['ชื่อ'] + " " + df['รายละเอียด'] + " " + df['กลุ่ม']
df['embedding'] = df['combined_text'].apply(lambda x: embedding_model.encode(x).tolist())
df['ค่าแฟคเตอร์ (kgCO2e)'] = pd.to_numeric(df['ค่าแฟคเตอร์ (kgCO2e)'], errors='coerce').fillna(0)
df.drop('combined_text', axis=1, inplace=True)

def generate_documents(df):
    for _, row in df.iterrows():
        yield {
            "_index": "emission_data_upsert_embedding",
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
                        "เปลี่ยนแปลง": row["เปลี่ยนแปลง"],
                        "embedding": row["embedding"]
            }
        }
try:
    bulk(es, generate_documents(df))
    print("Data successfully inserted into Elasticsearch!")
except Exception as e:
    print(f"Failed to upload data: {e}")

from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv
import json
from synonyms import thai_synonyms

load_dotenv("../.env")
ELASTIC_ID = os.getenv("ELASTIC_ID")
ELASTIC_PW = os.getenv("ELASTIC_PW")
INDEX_NAME = "hybrid_search_ef"
es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=(ELASTIC_ID, ELASTIC_PW),
    ca_certs="C:/Users/Nattapot/Documents/elasticsearch-8.17.0/config/certs/http_ca.crt"
)

if es.ping():
    print("Successfully connected to Elastic!")
else:
    print("Connection failed. Please check your connection information")


# สร้าง index settings และ mappings
index_settings = {
    "settings": {
        "analysis": {
            "filter": {
                "synonym_filter": {
                    "type": "synonym_graph",  # ใช้ synonym_graph ให้ผลดีกว่า synonym ธรรมดา
                    # "synonyms": "analysis/synonyms.txt",
                    "synonyms":thai_synonyms,
                    "expand": True,
                    "updateable": True
                }
            },
            "analyzer": {
                "thai_eng_analyzer": {
                    "type":"custom",
                    "tokenizer": "icu_tokenizer",
                    "filter": [
                        "lowercase",
                        "icu_folding"
                    ]
                },
                "thai_eng_search_analyzer":{
                    "type": "custom",
                    "tokenizer": "icu_tokenizer",
                    "filter": [
                        "lowercase",
                        "icu_folding",
                        "synonym_filter"
                    ]
                }
            }
        }#,
        # "index": {
        #     "knn": True,  # เปิดใช้งานการค้นหาแบบ kNN
        #     "knn.space_type": "cosinesimil"  # ใช้ cosine similarity
        # }
    },
    "mappings": {
        "properties": {
            "กลุ่ม": {
                "type": "text"
            },
            "ชื่อ": {
                "type": "text",
                "analyzer": "thai_eng_analyzer",
                "search_analyzer": "thai_eng_search_analyzer"
            },
            "รายละเอียด": {
                "type": "text",
                "analyzer": "thai_eng_analyzer",
                "search_analyzer": "thai_eng_search_analyzer"
            },
            "หน่วย": {
                "type": "text"
            },
            "ค่าแฟคเตอร์ (kgCO2e)": {
                "type": "float"
            },
            "ข้อมูลอ้างอิง": {
                "type": "text"
            },
            "วันที่อัพเดท": {
                "type": "text"
            },
            "ประเภทแฟคเตอร์": {
                "type": "text"
            },
            "เปลี่ยนแปลง": {
                "type": "date",
                "format": "yyyy-MM-dd"
            },
            "text_vector": {
                "type": "dense_vector",
                "dims": 384,
                "index": True,
                "similarity": "cosine"
            },
            "context_vector":{
                "type": "dense_vector",
                "dims": 384,
                "index":True,
                "similarity": "cosine"
            }
        }
    }
}


if not es.indices.exists(index=INDEX_NAME):
    es.indices.create(index=INDEX_NAME, body=index_settings)
    print(f"Index '{INDEX_NAME}' created successfully")
else:
    print(f"Index '{INDEX_NAME}' already exists")



# model for thai lag
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
print(f"Model 'paraphrase-multilingual-MiniLM-L12-v2' loaded successfully")

# =========== 4. เตรียมข้อมูลตัวอย่างและเพิ่มเข้า Elasticsearch ===========

# load data
def load_json():
    f = open('results.json', 'r', encoding='utf-8')
    data = json.load(f)
    result =  [d for d in data]
    f.close()
    return result


# prepare index
def index_documents(documents):
    count = 0
    for i, doc in enumerate(documents):
        # รวมข้อความสำหรับสร้าง vector
        text_vector = doc["ชื่อ"]
        context_vector = doc["รายละเอียด"]
        # สร้าง embedding
        embedding_text = model.encode(text_vector)
        embedding_context = model.encode(context_vector)
        
        # เพิ่มข้อมูลพร้อม vector
        doc_with_vector = doc.copy()
        doc_with_vector["text_vector"] = embedding_text.tolist()
        doc_with_vector["context_vector"] = embedding_context.tolist()
        
        es.index(
            index=INDEX_NAME,
            id=i,
            document=doc_with_vector
        )
        count += 1
    
    # Refresh index
    es.indices.refresh(index=INDEX_NAME)
    return count


# insert dat
num_docs = index_documents(load_json())
print(f"Added {num_docs} data items successfully")


### # เพิ่มข้อมูลเข้า index
def index_documents_other(documents):
    count = 0
    for i, doc in enumerate(documents):
        # รวมข้อความสำหรับสร้าง vector
        text_vector = doc["ชื่อ"] + ' ' + doc["รายละเอียด"]
        # สร้าง embedding
        embedding_text = model.encode(text_vector)
        
        # เพิ่มข้อมูลพร้อม vector
        doc_with_vector = doc.copy()
        doc_with_vector["text_vector"] = embedding_text.tolist()
        
        es.index(
            index=INDEX_NAME,
            id=i,
            document=doc_with_vector
        )
        count += 1
    
    # Refresh index
    es.indices.refresh(index=INDEX_NAME)
    return count

# num_docs = index_documents_other(sample_data)
# print(f"เพิ่มข้อมูลตัวอย่าง {num_docs} รายการเรียบร้อย")

# =========== function for Hybrid Search ===========

def hybrid_search(query, index_name=INDEX_NAME, bm25_weight=0.5, vector_weight=0.5, size=5):
    """
    ค้นหาแบบ hybrid ด้วย BM25 และ vector search
    
    Parameters:
    - query: คำค้นหา
    - index_name: ชื่อ index
    - bm25_weight: น้ำหนักของคะแนน BM25 (0-1)
    - vector_weight: น้ำหนักของคะแนน vector search (0-1)
    - size: จำนวนผลลัพธ์ที่ต้องการ
    
    Returns:
    - ผลลัพธ์การค้นหา
    """

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
                            "fields": ["ชื่อ^3", "รายละเอียด^2"],  # ให้น้ำหนักตามลำดับความสำคัญ
                            "boost": bm25_weight  # น้ำหนักของ BM25
                        }
                    },
                    # Vector search
                    {
                        "script_score": {
                            "query": {"match_all": {}},
                            "script": {
                                # คำนวณ cosine similarity ระหว่าง query vector และ document vector
                                "source": "cosineSimilarity(params.query_vector, 'text_vector') + 1.0",
                                "params": {
                                    "query_vector": query_vector
                                }
                            },
                            "boost": vector_weight  # น้ำหนักของ vector search
                        }
                    }
                ]
            }
        },
        "_source": ["ชื่อ", "รายละเอียด", "หน่วย", "ค่าแฟคเตอร์ (kgCO2e)"],  # ข้อมูลที่ต้องการให้แสดงในผลลัพธ์
        "size": size  # จำนวนผลลัพธ์
    }
    
    # ส่งคำขอค้นหา
    response = es.search(index=index_name, body=search_query)
    
    return response["hits"]["hits"]

# ฟังก์ชันแสดงผลลัพธ์
def print_search_results(results, query):
    print(f"\nผลการค้นหาสำหรับ: '{query}'")
    print(f"พบ {len(results)} รายการ")
    print("-" * 80)
    
    for i, hit in enumerate(results):
        print(f"{i+1}. {hit['_source']['ชื่อ']} (คะแนน: {hit['_score']:.4f})")
        print(f"   รายละเอียด: {hit['_source']['รายละเอียด']}")
        print(f"   ค่าแฟคเตอร์:: {hit['_source']['ค่าแฟคเตอร์ (kgCO2e)']} {hit['_source']['หน่วย']}")

# =========== 6. ทดสอบการค้นหาแบบ Hybrid กับ Synonyms ===========

# ตัวอย่างคำค้นหาที่มี synonyms
test_queries = [
    "ก๊าซหุงต้ม",  
    "E85",
    "น้ำมันก๊าด",
    "Peanut",
    "รถพ่วง",
    "Lychee" 
]

# ทดสอบค้นหาแบบ hybrid - เน้น keyword matching มากกว่า (BM25)
print("\n=== ทดสอบการค้นหาแบบ Hybrid - เน้น BM25 (0.7) แทนที่ Vector (0.3) ===")
for query in test_queries:
    results = hybrid_search(query, bm25_weight=0.7, vector_weight=0.3)
    print_search_results(results, query)

# ทดสอบค้นหาแบบ hybrid - เน้น semantic search มากกว่า (Vector)
print("\n=== ทดสอบการค้นหาแบบ Hybrid - เน้น Vector (0.7) แทนที่ BM25 (0.3) ===")
for query in test_queries:
    results = hybrid_search(query, bm25_weight=0.3, vector_weight=0.7)
    print_search_results(results, query)

# ทดสอบการค้นหาด้วยข้อความที่มีความหมายคล้ายกัน (semantic search)
# semantic_query = "อยากได้อุปกรณ์อิเล็กทรอนิกส์ที่ไม่แพงมากสำหรับใช้งานประจำวัน"
semantic_query = "อยากรู้ค่าefของน้ำมันE85"
print("\n=== ทดสอบการค้นหาด้วยความหมาย (Semantic Search) ===")
results = hybrid_search(semantic_query, bm25_weight=0.2, vector_weight=0.8)
print_search_results(results, semantic_query)

# =========== 7. ฟังก์ชันอัพเดต Synonyms (ใช้กรณีต้องการอัพเดต) ===========

def update_synonyms(new_synonyms, filter_name="synonym_filter", index_name=INDEX_NAME):
    """
    อัพเดต synonym filter
    
    หมายเหตุ: ต้องใช้ reindex หลังจากอัพเดตถ้าต้องการให้มีผลกับข้อมูลเก่า
    """
    update_settings = {
        "analysis": {
            "filter": {
                filter_name: {
                    "type": "synonym_graph",
                    "synonyms": new_synonyms
                }
            }
        }
    }
    
    # Close index ก่อนอัพเดต settings
    es.indices.close(index=index_name)
    
    # อัพเดต settings
    es.indices.put_settings(body={"settings": update_settings}, index=index_name)
    
    # Open index หลังอัพเดต
    es.indices.open(index=index_name)
    
    return True

# ตัวอย่างการอัพเดต synonyms (ถ้าต้องการใช้)
# new_synonyms = thai_synonyms + ["แล็ปท็อป, โน๊ตบุ๊ค, laptop", "สินค้า, ผลิตภัณฑ์, โปรดักส์"]
# update_result = update_synonyms(new_synonyms)
# print(f"อัพเดต synonyms: {'สำเร็จ' if update_result else 'ไม่สำเร็จ'}")

# =========== 8. ฟังก์ชันสำหรับให้ผู้ใช้ค้นหาเอง ===========

def user_search():
    """ฟังก์ชันสำหรับให้ผู้ใช้ค้นหาด้วยตัวเอง"""
    print("\n=== ค้นหาด้วยตัวเอง ===")
    print("พิมพ์ 'exit' เพื่อออก")
    
    while True:
        query = input("\nพิมพ์คำค้นหา: ")
        if query.lower() == 'exit':
            break
            
        # เลือกสัดส่วนของ BM25 และ Vector
        bm25_ratio = float(input("สัดส่วน BM25 (0.0-1.0): ") or "0.5")
        vector_ratio = 1.0 - bm25_ratio
        
        # ค้นหา
        results = hybrid_search(query, bm25_weight=bm25_ratio, vector_weight=vector_ratio)
        
        # แสดงผล
        print_search_results(results, query)

# เรียกใช้งานค้นหาของผู้ใช้ (uncomment เพื่อใช้งาน)
# user_search()

print("\nเสร็จสมบูรณ์! คุณสามารถใช้ฟังก์ชัน hybrid_search() เพื่อค้นหาข้อมูล")
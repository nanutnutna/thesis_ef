from elasticsearch import Elasticsearch
import ssl
import certifi
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv

load_dotenv()
# รายละเอียดการเชื่อมต่อจาก Elastic Cloud
cloud_id = os.getenv("ELASTIC_CLOUD_ID")
api_key = os.getenv("ELASTIC_API_KEY")

# วิธีเชื่อมต่อแบบที่ 1: ใช้ API Key (แนะนำ)
es = Elasticsearch(
    cloud_id=cloud_id,
    api_key=api_key
)


# ตรวจสอบการเชื่อมต่อ
if es.ping():
    print("เชื่อมต่อกับ Elastic Cloud สำเร็จ!")
else:
    print("เชื่อมต่อไม่สำเร็จ กรุณาตรวจสอบข้อมูลการเชื่อมต่อ")



# กำหนด synonyms ภาษาไทย
thai_synonyms = [
    "รถยนต์, รถ, คาร์, ยานพาหนะ, ยานยนต์",
    "โทรศัพท์, มือถือ, โทรศัพท์มือถือ, สมาร์ทโฟน, โฟน",
    "คอมพิวเตอร์, คอม, พีซี, เครื่องคอมพิวเตอร์, โน๊ตบุ๊ค"
]


# กำหนด index name
INDEX_NAME = "thai_hybrid_search"

# สร้าง index settings และ mappings
index_settings = {
    "settings": {
        "analysis": {
            "filter": {
                "thai_synonym_filter": {
                    "type": "synonym_graph",  # ใช้ synonym_graph ให้ผลดีกว่า synonym ธรรมดา
                    "synonyms": thai_synonyms
                }
            },
            "analyzer": {
                "thai_analyzer": {
                    "tokenizer": "thai",
                    "filter": [
                        "lowercase",
                        "thai_synonym_filter"
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
            "title": {
                "type": "text",
                "analyzer": "thai_analyzer"
            },
            "content": {
                "type": "text",
                "analyzer": "thai_analyzer"
            },
            "category": {
                "type": "text",
                "analyzer": "thai_analyzer"
            },
            "price": {
                "type": "float"
            },
            "text_vector": {
                "type": "dense_vector",
                "dims": 384,  # ขนาดของ vector, ขึ้นอยู่กับ model ที่ใช้
                "index": True,
                "similarity": "cosine"
            }
        }
    }
}

# สร้าง index (เช็คก่อนว่ามีอยู่แล้วหรือไม่)
if not es.indices.exists(index=INDEX_NAME):
    es.indices.create(index=INDEX_NAME, body=index_settings)
    print(f"สร้าง index '{INDEX_NAME}' เรียบร้อย")
else:
    print(f"index '{INDEX_NAME}' มีอยู่แล้ว")

# =========== 3. โหลด Model สำหรับสร้าง Vector Embeddings ===========

# โหลด model สำหรับภาษาไทย
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
print(f"โหลด model 'paraphrase-multilingual-MiniLM-L12-v2' เรียบร้อย")

# =========== 4. เตรียมข้อมูลตัวอย่างและเพิ่มเข้า Elasticsearch ===========

# ข้อมูลตัวอย่าง
sample_data = [
    {
        "title": "รถยนต์ไฟฟ้ารุ่นใหม่",
        "content": "รถยนต์ไฟฟ้ารุ่นใหม่จากค่ายผู้ผลิตชั้นนำ มีระยะทางขับขี่มากกว่า 500 กิโลเมตร",
        "category": "ยานพาหนะ",
        "price": 1500000.00
    },
    {
        "title": "มือถือรุ่นล่าสุดเปิดตัวแล้ว",
        "content": "โทรศัพท์มือถือรุ่นใหม่ล่าสุดจากแบรนด์ดัง เปิดตัวแล้ววันนี้ พร้อมกล้องถ่ายรูปความละเอียดสูง",
        "category": "อิเล็กทรอนิกส์",
        "price": 39900.00
    },
    {
        "title": "ราคาน้ำมันวันนี้",
        "content": "ราคาน้ำมันวันนี้ปรับตัวขึ้นอีก 1 บาทต่อลิตร ส่งผลกระทบต่อค่าครองชีพ",
        "category": "ข่าวเศรษฐกิจ",
        "price": 0.00
    },
    {
        "title": "คอมพิวเตอร์สำหรับทำงานที่บ้าน",
        "content": "คอมพิวเตอร์สำหรับทำงานที่บ้านต้องมีประสิทธิภาพที่ดีและราคาไม่แพงจนเกินไป",
        "category": "อิเล็กทรอนิกส์",
        "price": 25000.00
    },
    {
        "title": "โน๊ตบุ๊คเล่นเกมรุ่นใหม่",
        "content": "โน๊ตบุ๊คสำหรับเล่นเกมรุ่นใหม่มาพร้อมกับการ์ดจอรุ่นล่าสุด ประสิทธิภาพสูง เล่นเกมลื่น",
        "category": "อิเล็กทรอนิกส์",
        "price": 45000.00
    },
    {
        "title": "สมาร์ทโฟนราคาประหยัด",
        "content": "สมาร์ทโฟนรุ่นใหม่ราคาไม่เกิน 10,000 บาท แต่มีฟีเจอร์ครบครัน คุ้มค่าน่าซื้อ",
        "category": "อิเล็กทรอนิกส์",
        "price": 9900.00
    }
]

# เพิ่มข้อมูลเข้า index
def index_documents(documents):
    count = 0
    for i, doc in enumerate(documents):
        # รวมข้อความสำหรับสร้าง vector
        combined_text = doc["title"] + " " + doc["content"]
        
        # สร้าง embedding
        embedding = model.encode(combined_text)
        
        # เพิ่มข้อมูลพร้อม vector
        doc_with_vector = doc.copy()
        doc_with_vector["text_vector"] = embedding.tolist()
        
        es.index(
            index=INDEX_NAME,
            id=i,
            document=doc_with_vector
        )
        count += 1
    
    # Refresh index
    es.indices.refresh(index=INDEX_NAME)
    return count

# เพิ่มข้อมูลตัวอย่าง
num_docs = index_documents(sample_data)
print(f"เพิ่มข้อมูลตัวอย่าง {num_docs} รายการเรียบร้อย")

# =========== 5. ฟังก์ชันสำหรับการทำ Hybrid Search ===========

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
                            "fields": ["title^3", "content^2", "category"],  # ให้น้ำหนักตามลำดับความสำคัญ
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
        "_source": ["title", "content", "category", "price"],  # ข้อมูลที่ต้องการให้แสดงในผลลัพธ์
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
        print(f"{i+1}. {hit['_source']['title']} (คะแนน: {hit['_score']:.4f})")
        print(f"   หมวดหมู่: {hit['_source']['category']}")
        print(f"   เนื้อหา: {hit['_source'].get('content', 'ไม่มีข้อมูล')}")
        print(f"   ราคา: {hit['_source'].get('price', 0):.2f} บาท")
        print("-" * 80)

# =========== 6. ทดสอบการค้นหาแบบ Hybrid กับ Synonyms ===========

# ตัวอย่างคำค้นหาที่มี synonyms
test_queries = [
    "รถไฟฟ้ารุ่นใหม่",        # ค้นหาด้วยคำว่า "รถ" แทน "รถยนต์"
    "มือถือกล้องดี",          # ค้นหาด้วยคำว่า "มือถือ" แทน "โทรศัพท์"
    "ค่าน้ำมัน",              # ค้นหาด้วยคำว่า "ค่า" แทน "ราคา"
    "คอมทำงานที่บ้าน",       # ค้นหาด้วยคำว่า "คอม" แทน "คอมพิวเตอร์"
    "สมาร์ทโฟนราคาถูก",       # ค้นหาด้วยความหมายที่ใกล้เคียง
    "ยานยนต์"
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
semantic_query = "อยากได้อุปกรณ์อิเล็กทรอนิกส์ที่ไม่แพงมากสำหรับใช้งานประจำวัน"
print("\n=== ทดสอบการค้นหาด้วยความหมาย (Semantic Search) ===")
results = hybrid_search(semantic_query, bm25_weight=0.2, vector_weight=0.8)
print_search_results(results, semantic_query)

# =========== 7. ฟังก์ชันอัพเดต Synonyms (ใช้กรณีต้องการอัพเดต) ===========

def update_synonyms(new_synonyms, filter_name="thai_synonym_filter", index_name=INDEX_NAME):
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
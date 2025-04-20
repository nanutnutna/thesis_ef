from elasticsearch import Elasticsearch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# เชื่อมต่อ Elasticsearch
es = Elasticsearch("http://localhost:9200")

# ข้อมูลทดสอบ
test_queries = [
    "machine learning techniques",
    "cloud computing security",
    "artificial intelligence applications in healthcare",
    "big data analytics tools",
    "blockchain technology examples"
]

# Ground truth (ตัวอย่างสำหรับคำค้นหาแรก)
ground_truth = {
    "machine learning techniques": [
        {"doc_id": "article123", "rating": 3},
        {"doc_id": "article456", "rating": 3},
        # ... อีก 18 เอกสาร ...
    ],
    # ... คำค้นหาอื่นๆ ...
}

# วิธี Hybrid Search ที่ต้องการทดสอบ
hybrid_methods = {
    "bool_script": {
        "query": {
            "bool": {
                "should": [
                    {"match": {"title": {"query": "{query}", "boost": 1.5}}},
                    {"match": {"content": {"query": "{query}", "boost": 1.0}}},
                    {
                        "script_score": {
                            "query": {"match_all": {}},
                            "script": {
                                "source": "cosineSimilarity(params.query_vector, 'content_vector') + 1.0",
                                "params": {"query_vector": None}  # จะถูกแทนที่ด้วยเวกเตอร์จริง
                            },
                            "boost": 2.0
                        }
                    }
                ]
            }
        }
    },
    "knn_filter": {
        "knn": {
            "field": "content_vector",
            "query_vector": None,  # จะถูกแทนที่ด้วยเวกเตอร์จริง
            "k": 20,
            "num_candidates": 100,
            "filter": {
                "bool": {
                    "should": [
                        {"match": {"title": "{query}"}},
                        {"match": {"content": "{query}"}}
                    ]
                }
            }
        }
    },
    # ... วิธีอื่นๆ ...
}

# ฟังก์ชั่นคำนวณ Precision, Recall และ F1
def calculate_precision_at_k(relevant_docs, retrieved_docs, k):
    retrieved_k = retrieved_docs[:k]
    relevant_retrieved = set(retrieved_k) & set(relevant_docs)
    return len(relevant_retrieved) / k if k > 0 else 0

def calculate_recall_at_k(relevant_docs, retrieved_docs, k):
    retrieved_k = retrieved_docs[:k]
    relevant_retrieved = set(retrieved_k) & set(relevant_docs)
    return len(relevant_retrieved) / len(relevant_docs) if len(relevant_docs) > 0 else 0

def calculate_f1_score(precision, recall):
    return 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

# ฟังก์ชั่นรับเวกเตอร์สำหรับคำค้นหา (สมมติว่ามี API ให้ดึงเวกเตอร์)
def get_embedding_vector(query):
    # ในสถานการณ์จริง คุณอาจใช้โมเดลเช่น Sentence-BERT หรือ OpenAI Embeddings API
    # สำหรับตัวอย่างนี้ เราจะสร้างเวกเตอร์สุ่ม
    return np.random.rand(384).tolist()  # เวกเตอร์ 384 มิติ

# ตาราง DataFrame สำหรับเก็บผลลัพธ์
results = pd.DataFrame(columns=[
    'query', 'method', 'precision@5', 'precision@10', 
    'recall@5', 'recall@10', 'f1@5', 'f1@10', 'ndcg@10'
])

# ทดสอบแต่ละคำค้นหา
for query in test_queries:
    # รายการเอกสารที่เกี่ยวข้องสำหรับคำค้นหานี้
    relevant_docs = [doc["doc_id"] for doc in ground_truth[query] if doc["rating"] >= 1]
    
    # รับเวกเตอร์สำหรับคำค้นหา
    query_vector = get_embedding_vector(query)
    
    # ทดสอบแต่ละวิธี
    for method_name, method_query in hybrid_methods.items():
        # สร้าง query ตามรูปแบบของแต่ละวิธี
        actual_query = method_query.copy()
        
        # แทนที่คำค้นหาและเวกเตอร์
        if method_name == "bool_script":
            actual_query["query"]["bool"]["should"][0]["match"]["title"]["query"] = query
            actual_query["query"]["bool"]["should"][1]["match"]["content"]["query"] = query
            actual_query["query"]["bool"]["should"][2]["script_score"]["script"]["params"]["query_vector"] = query_vector
        elif method_name == "knn_filter":
            actual_query["knn"]["query_vector"] = query_vector
            actual_query["knn"]["filter"]["bool"]["should"][0]["match"]["title"] = query
            actual_query["knn"]["filter"]["bool"]["should"][1]["match"]["content"] = query
        
        # ส่ง query ไปยัง Elasticsearch
        response = es.search(index="articles", body=actual_query, size=20)
        
        # รับรายการ IDs ของเอกสารที่ได้รับ
        retrieved_docs = [hit["_id"] for hit in response["hits"]["hits"]]
        
        # คำนวณตัวชี้วัด
        precision_5 = calculate_precision_at_k(relevant_docs, retrieved_docs, 5)
        precision_10 = calculate_precision_at_k(relevant_docs, retrieved_docs, 10)
        recall_5 = calculate_recall_at_k(relevant_docs, retrieved_docs, 5)
        recall_10 = calculate_recall_at_k(relevant_docs, retrieved_docs, 10)
        f1_5 = calculate_f1_score(precision_5, recall_5)
        f1_10 = calculate_f1_score(precision_10, recall_10)
        
        # คำนวณ NDCG (ต้องใช้ ratings)
        # ... (โค้ดคำนวณ NDCG) ...
        ndcg_10 = 0.83  # สมมติค่า
        
        # เพิ่มผลลัพธ์ลงในตาราง
        results = results.append({
            'query': query,
            'method': method_name,
            'precision@5': precision_5,
            'precision@10': precision_10,
            'recall@5': recall_5,
            'recall@10': recall_10,
            'f1@5': f1_5,
            'f1@10': f1_10,
            'ndcg@10': ndcg_10
        }, ignore_index=True)

# แสดงผลลัพธ์
print(results)

# คำนวณค่าเฉลี่ยของแต่ละวิธี
avg_results = results.groupby('method').mean()
print("\nค่าเฉลี่ยของแต่ละวิธี:")
print(avg_results)

# สร้างกราฟ
plt.figure(figsize=(12, 8))

# กราฟ Precision@10
plt.subplot(2, 2, 1)
avg_results['precision@10'].plot(kind='bar')
plt.title('Average Precision@10')
plt.ylim(0, 1)

# กราฟ Recall@10
plt.subplot(2, 2, 2)
avg_results['recall@10'].plot(kind='bar')
plt.title('Average Recall@10')
plt.ylim(0, 1)

# กราฟ F1@10
plt.subplot(2, 2, 3)
avg_results['f1@10'].plot(kind='bar')
plt.title('Average F1-Score@10')
plt.ylim(0, 1)

# กราฟ NDCG@10
plt.subplot(2, 2, 4)
avg_results['ndcg@10'].plot(kind='bar')
plt.title('Average NDCG@10')
plt.ylim(0, 1)

plt.tight_layout()
plt.savefig('hybrid_search_evaluation.png')
plt.show()
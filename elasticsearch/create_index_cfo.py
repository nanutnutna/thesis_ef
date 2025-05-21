from elasticsearch import Elasticsearch
import os
from datetime import datetime
from dotenv import load_dotenv
import json
from synonyms import thai_synonyms
from sentence_transformers import SentenceTransformer

currendate = datetime.now().strftime('%Y%m%d')


load_dotenv("../.env")
ELASTIC_ID = os.getenv("ELASTIC_ID")
ELASTIC_PW = os.getenv("ELASTIC_PW")
INDEX_NAME = 'cfo'
JSON_PATH = rf'C:\Users\Nattapot\Desktop\thesis_ef\extract_data\{INDEX_NAME}_{currendate}.json'

es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=(ELASTIC_ID, ELASTIC_PW),
    ca_certs="C:/Users/Nattapot/Documents/elasticsearch-8.17.0/config/certs/http_ca.crt"
)


if es.ping():
    print("Successfully connected to Elastic!")
else:
    print("Connection failed. Please check your connection information")


index_settings = {
  "settings": {
    "analysis": {
      "filter": {
        "synonym_filter": {
          "type": "synonym_graph",
          "synonyms": thai_synonyms,
          "expand": True,
          "updateable": True
        }
      },
      "analyzer": {
        "thai_eng_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": [
            "lowercase",
            "icu_folding"
          ]
        },
        "thai_synonym_analyzer": {
          "type": "custom",
          "tokenizer": "icu_tokenizer",
          "filter": [
            "lowercase",
            "icu_folding",
            "synonym_filter"
          ]
        },
        "keyword_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": [
            "lowercase",
            "icu_folding"
          ]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "กลุ่ม": {
        "type": "text"
      },
      "ลําดับ": {
        "type": "float"
      },
      "ชื่อ": {
        "type": "text",
        "fields": {
          "search": {
            "type": "text",
            "analyzer": "thai_eng_analyzer",
            "search_analyzer": "thai_synonym_analyzer"
          },
          "keyword_search": {
            "type": "text",
            "analyzer": "keyword_analyzer",
            "search_analyzer": "keyword_analyzer"
          }
        }
      },
      "รายละเอียด": {
        "type": "text",
        "analyzer": "thai_eng_analyzer",
        "search_analyzer": "thai_synonym_analyzer",
        "fields": {
          "keyword_search": {
            "type": "text",
            "analyzer": "keyword_analyzer",
            "search_analyzer": "keyword_analyzer"
          }
        }
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
      "text_vector": {
        "type": "dense_vector",
        "dims": 384,
        "index": True,
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


# call model 
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
print(f"Model 'paraphrase-multilingual-MiniLM-L12-v2' loaded successfully")


def load_json(path=JSON_PATH):
    f = open(path, 'r', encoding='utf-8')
    data = json.load(f)
    result =  [d for d in data]
    f.close()
    return result


def index_documents(documents):
    count = 0
    for i, doc in enumerate(documents):
        text_vector = doc['ชื่อ']
        embedding_text = model.encode(text_vector)

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


num_docs = index_documents(load_json())
print(f"Added {num_docs} data items successfully")
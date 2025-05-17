from elasticsearch import Elasticsearch
import os
from datetime import datetime
from dotenv import load_dotenv
import json
from synonyms import thai_synonyms
from sentence_transformers import SentenceTransformer



currentDate = datetime.now()
file_date = '20250517'
# file_date = datetime.strftime(currentDate,"%Y%m%d")

load_dotenv("../.env")
ELASTIC_ID = os.getenv("ELASTIC_ID")
ELASTIC_PW = os.getenv("ELASTIC_PW")
INDEX_NAME = 'cfp_label'
JSON_PATH = rf'C:\Users\Nattapot\Desktop\thesis_ef\extract_data\cfp_label_{file_date}.json'

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
        }
    },
    "mappings": {
        "properties": {
            "License": {
                "type": "text"
            },
            "Name": {
                "type": "text",
                "analyzer": "thai_eng_analyzer",
                "search_analyzer": "thai_eng_search_analyzer"
            },
            "Detail": {
                "type": "text",
                "analyzer": "thai_eng_analyzer",
                "search_analyzer": "thai_eng_search_analyzer"
            },
            "Industrials": {
                "type": "text"
            },
            "ApproveDate": {
                "type": "text"
            },
            "EF": {
                "type": "text"
            },
            "Unit": {
                "type": "text"
            },
            "Scope": {
                "type": "text"
            },
            "Company_name": {
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
        text_vector = doc['Name']
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
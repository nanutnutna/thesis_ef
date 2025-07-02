from elasticsearch import Elasticsearch
from synonyms import thai_synonyms
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import json

INDEX_NAME = 'test_elastic_cloud'
JSON_PATH = f'combine_20250602.json'

es = Elasticsearch(
  "https://17a1b0bc419b499eb33a40065d65170d.asia-southeast1.gcp.elastic-cloud.com:443",
  api_key="cm1kMmpKY0I4c1o0ckNSSzJmNjk6aVM5eE9iVUpuX25YRHhQbXNqd20xZw=="
)



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
                    "tokenizer": "icu_tokenizer", # "icu_tokenizer"
                    "filter": [
                        "lowercase",
                        "icu_folding"
                    ]
                },
                "thai_eng_search_analyzer":{
                    "type": "custom",
                    "tokenizer": "icu_tokenizer", # "thai"
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
            "Category": {
                "type": "text"
            },
            "Name": {
                "type": "text",
                "analyzer": "thai_eng_analyzer",
                "search_analyzer": "thai_eng_search_analyzer"
            },
            "Unit": {
                "type": "text"
            },
            "Factor": {
                "type": "text"
            },
            "Reference": {
                "type": "text"
            },
            "Last Updated": {
                "type": "text"
            }
            ,
            "text_vector": {
                "type": "dense_vector",
                "dims": 768, 
                "index": True,
                "similarity": "cosine"
            }
        }
    }
}


if es.ping():
    print("Successfully connected to Elastic!")
else:
    print("Connection failed. Please check your connection information")


if not es.indices.exists(index=INDEX_NAME):
    es.indices.create(index=INDEX_NAME, body=index_settings)
    print(f"Index '{INDEX_NAME}' created successfully")
else:
    print(f"Index '{INDEX_NAME}' already exists")


# call model 
model_name = f'multilingual-e5-base'
# model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
model = SentenceTransformer('intfloat/multilingual-e5-base')
print(f"Model '{model_name}' loaded successfully")

def load_json(path=JSON_PATH):
    f = open(path, 'r', encoding='utf-8')
    data = json.load(f)
    result =  [d for d in data]
    f.close()
    return result

# for hybird
def index_documents(documents):
    count = 0
    for i, doc in tqdm(enumerate(documents),total=len(documents),ncols=50):
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

# def index_documents(documents):
#     count = 0
#     for i, doc in tqdm(enumerate(documents), total=len(documents), ncols=50):
#         # No need to generate embeddings - just index the document as is
#         es.index(
#             index=INDEX_NAME,
#             id=i,
#             document=doc
#         )
#         count += 1
    
#     # Refresh index
#     es.indices.refresh(index=INDEX_NAME)
#     return count


num_docs = index_documents(load_json())
print(f"Added {num_docs} data items successfully")
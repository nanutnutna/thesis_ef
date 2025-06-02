from elastic_connection import ElasticsearchConnection
from datetime import datetime
import json
from synonyms import thai_synonyms
from sentence_transformers import SentenceTransformer

CURRENTDATE = datetime.strftime(datetime.now(),"%Y%m%d")
INDEX_NAME = 'combine'
# JSON_PATH = f'combine_{CURRENTDATE}.json'
JSON_PATH = f'combine_20250602.json'
es = ElasticsearchConnection.get_instance()

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
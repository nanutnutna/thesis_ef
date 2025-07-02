from elastic_connection import ElasticsearchConnection
from datetime import datetime
import json
from synonyms import thai_synonyms
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

CURRENTDATE = datetime.strftime(datetime.now(),"%Y%m%d")
# INDEX_NAME = 'combine_no_synonym'
# INDEX_NAME = 'thai_combine'
# INDEX_NAME = 'combine'
INDEX_NAME = 'keyword_combine_with_synonym'
# INDEX_NAME = 'keyword_combine_no_synonym'
# JSON_PATH = f'combine_{CURRENTDATE}.json'
# JSON_PATH = f'combine_20250602.json'
JSON_PATH = f'combine_20250701.json'
# es = ElasticsearchConnection.get_instance()



from elasticsearch import Elasticsearch
es = Elasticsearch(
  "https://14a823faf1c845b0a02f427056f7112c.asia-southeast1.gcp.elastic-cloud.com:443",
  api_key="YlRZaHlaY0JVRzZKbi1obUV0WnM6ZDlPTS13VS1Ja1E2S3M1eUpkSE56QQ==")

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
            "Detail": {
                "type": "text"
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
        }
    }
}

# index_settings = {
#     "settings": {
#         "analysis": {
#             "analyzer": {
#                 "thai_eng_analyzer": {
#                     "type":"custom",
#                     "tokenizer": "icu_tokenizer",
#                     "filter": [
#                         "lowercase",
#                         "icu_folding"
#                     ]
#                 }
#             }
#         }
#     },
#     "mappings": {
#         "properties": {
#             "Category": {
#                 "type": "text"
#             },
#             "Name": {
#                 "type": "text",
#                 "analyzer": "thai_eng_analyzer"
#             },
#             "Unit": {
#                 "type": "text"
#             },
#             "Factor": {
#                 "type": "text"
#             },
#             "Reference": {
#                 "type": "text"
#             },
#             "Last Updated": {
#                 "type": "text"
#             }
#         }
#     }
# }


if not es.indices.exists(index=INDEX_NAME):
    es.indices.create(index=INDEX_NAME, body=index_settings)
    print(f"Index '{INDEX_NAME}' created successfully")
else:
    print(f"Index '{INDEX_NAME}' already exists")


def load_json(path=JSON_PATH):
    f = open(path, 'r', encoding='utf-8')
    data = json.load(f)
    result =  [d for d in data]
    f.close()
    return result


def index_documents(documents):
    count = 0
    for i, doc in tqdm(enumerate(documents), total=len(documents), ncols=50):
        # No need to generate embeddings - just index the document as is
        es.index(
            index=INDEX_NAME,
            id=i,
            document=doc
        )
        count += 1
    
    # Refresh index
    es.indices.refresh(index=INDEX_NAME)
    return count


num_docs = index_documents(load_json())
print(f"Added {num_docs} data items successfully")
from elasticsearch import Elasticsearch
import os
import time
from dotenv import load_dotenv
import json


env = r'C:\Users\Nattapot\Desktop\thesis_ef\.env'
load_dotenv(env)
ELASTIC_ID = os.getenv("ELASTIC_ID")
ELASTIC_PW = os.getenv("ELASTIC_PW")
INDEX_NAME = "hybrid_search_ef"
es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=(ELASTIC_ID, ELASTIC_PW),
    ca_certs="C:/Users/Nattapot/Documents/elasticsearch-8.17.0/config/certs/http_ca.crt"
)


print(es.info())
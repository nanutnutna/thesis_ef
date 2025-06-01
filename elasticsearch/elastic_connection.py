from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv

env = r'C:\Users\Nattapot\Desktop\thesis_ef\.env'
load_dotenv(env)

class ElasticsearchConnection:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            ELASTIC_ID = os.getenv("ELASTIC_ID")
            ELASTIC_PW = os.getenv("ELASTIC_PW")
        
            cls._instance = Elasticsearch(
                ["https://localhost:9200"],
                basic_auth=(ELASTIC_ID, ELASTIC_PW),
                ca_certs="C:/Users/Nattapot/Documents/elasticsearch-8.17.0/config/certs/http_ca.crt"
            )
        return cls._instance

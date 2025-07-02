from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import urllib3
import pandas as pd
from io import StringIO
from config.elastic_connection import ElasticsearchConnection
from elasticsearch.helpers import bulk
import numpy as np


OUTPUT_PATH = r"/opt/airflow/output"
current_date = datetime.strftime(datetime.now(),"%Y%m%d")

def extract_cfp():
    pass

def extract_cfo():
    pass

def extract_carbon_label():
    pass

def merge_table(**kwargs):
    pass

def elasticsearch_upsert(**kwargs):
    pass




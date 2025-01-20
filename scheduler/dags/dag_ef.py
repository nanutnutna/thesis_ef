from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import urllib3
import pandas as pd
from io import StringIO
from elasticsearch import Elasticsearch
import numpy as np


URL_CFP = "https://thaicarbonlabel.tgo.or.th/index.php?lang=TH&mod=Y0hKdlpIVmpkSE5mWlcxcGMzTnBiMjQ9"
URL_CFO = "https://thaicarbonlabel.tgo.or.th/index.php?lang=TH&mod=YjNKbllXNXBlbUYwYVc5dVgyVnRhWE56YVc5dQ"
OUTPUT_PATH = r"/opt/airflow/output"
ELASTICSEARCH_HOST = "https://host.docker.internal:9200"
ELASTICSEARCH_USER = "elastic"
ELASTICSEARCH_PASSWORD = "JODDaUKomoKuPHFM2zEc"
INDEX_NAME = "emission_data"


current_date = datetime.now()
last_date = current_date - timedelta(days=1)
current_date_str = current_date.strftime("%Y%m%d")
last_date_str = last_date.strftime("%Y%m%d")
current_date_str_h = current_date.strftime("%Y%m%d_%H%M%S")


def extract_cfp(**kwargs):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    url = URL_CFP

    response = requests.get(url, verify=False)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'lxml')
        table = soup.find("table", {"class": "table table-striped table-bordered table-hover table-full-width table-customize"})
        df = pd.read_html(StringIO(str(table)))[0]

        df = df[['ลำดับ', 'กลุ่ม', 'ชื่อ', 'รายละเอียด', 'หน่วย', 'ค่าแฟคเตอร์ (kgCO2e)', 'ข้อมูลอ้างอิง', 'วันที่อัพเดท']]
        df['ประเภทแฟคเตอร์'] = "CFP"
        output = f"{OUTPUT_PATH}/emission_factor_cfp_{current_date_str}.csv"
        df.to_csv(output, index=False, encoding='utf-8-sig')
        return df
    else:
        raise Exception(f"Failed to fetch CFP data, status code: {response.status_code}")


def extract_cfo(**kwargs):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    url = URL_CFO

    response = requests.get(url, verify=False)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'lxml')
        table = soup.find("table")
        df = pd.read_html(StringIO(str(table)), header=[1, 2])[0]
        df.columns = [" ".join(col).strip() if "unit" in col[1] else col[0] for col in df.columns]

        ## modify table 
        df['รายละเอียด'] = df['ลำดับ']
        df['รายละเอียด'] = df['รายละเอียด'].fillna(df['ชื่อ'])
        df['กลุ่ม'] = df['รายละเอียด']
        df.loc[1:23, 'รายละเอียด'] = 'Stationary Combustion'
        df.loc[24:31, 'รายละเอียด'] = 'Mobile Combustion (On road)'
        df.loc[31:37, 'รายละเอียด'] = 'Mobile Combustion (Off road), Diesel'
        df.loc[38:42, 'รายละเอียด'] = 'Mobile Combustion (On road), Motor Gasoline 4 stroke'
        df.loc[43:47, 'รายละเอียด'] = 'Mobile Combustion (On road), Motor Gasoline 2 stroke'
        df.loc[48, 'รายละเอียด'] = 'Electricity, grid mix (ไฟฟ้า)'
        df.loc[50:, 'รายละเอียด'] = 'Refrigerants (สารทำความเย็น)'
        df['ลำดับ'] = pd.to_numeric(df['ลำดับ'], errors='coerce')
        df = df.rename(columns={'Total [kg CO2eq/unit]':'ค่าแฟคเตอร์ (kgCO2e)'})
        df = df.dropna(subset=['ลำดับ'])
        df = df.drop(columns=['CO2 [kg CO2/unit]','Fossil CH4 [kg CH4/unit]','CH4 [kg CH4/unit]','N2O [kg N2O/unit]'])
        df['วันที่อัพเดท'] = 'Update_Apr2022'
        #re-order column name 
        df = df[['ลำดับ','ชื่อ','รายละเอียด','หน่วย','ค่าแฟคเตอร์ (kgCO2e)','ข้อมูลอ้างอิง','วันที่อัพเดท']]
        df['ประเภทแฟคเตอร์'] = "CFO"
        output = f"{OUTPUT_PATH}/emission_factor_cfo_{current_date_str}.csv"
        df.to_csv(output, index=False, encoding='utf-8-sig')
        return df
    else:
        raise Exception(f"Failed to fetch CFO data, status code: {response.status_code}")


def merge_table(**kwargs):
    cfp = kwargs['ti'].xcom_pull(task_ids='extract_cfp')
    cfo = kwargs['ti'].xcom_pull(task_ids='extract_cfo')
    table = pd.concat([cfp, cfo], ignore_index=True)
    output = f"{OUTPUT_PATH}/emission_factor_{current_date_str}.csv"
    table.to_csv(output, index=False, encoding='utf-8-sig')


def compare_table(**kwargs):
    current_table = f"{OUTPUT_PATH}/emission_factor_{current_date_str}.csv"
    previous_table = f"{OUTPUT_PATH}/emission_factor_{last_date_str}.csv"
    try:
        table1 = pd.read_csv(previous_table)
        table2 = pd.read_csv(current_table)
        if table1.equals(table2):
            print("No differences found between tables.")
            kwargs['ti'].xcom_push(key='diff_flag', value=False)
        else:
            differences = table1.compare(table2)
            diff_output = f"{OUTPUT_PATH}/differences_{current_date_str_h}.csv"
            differences.to_csv(diff_output, index=False, encoding='utf-8-sig')
            print(f"Differences saved to {diff_output}")
            kwargs['ti'].xcom_push(key='diff_flag', value=True) 
    except FileNotFoundError:
        print("Previous file not found. Skipping comparison.")
        kwargs['ti'].xcom_push(key='flag', value=True)


def create_elasticsearch_index(**kwargs):
    diff_flag = kwargs['ti'].xcom_pull(key='diff_flag', task_ids='compare_tables')
    if not diff_flag:
        print("No differences. Skipping Elasticsearch index creation.")
        return

    # อ่านข้อมูลจาก CSV
    current_table = f"{OUTPUT_PATH}/emission_factor_{current_date_str}.csv"
    df = pd.read_csv(current_table)
    df.replace({np.nan: None}, inplace=True)

    es = Elasticsearch(ELASTICSEARCH_HOST,basic_auth=(ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD),verify_certs=False)

    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
        print(f"Deleted existing index: {INDEX_NAME}")

    index_settings = {
        "settings": {
            "analysis": {
                "filter": {
                    "thai_edge_ngram_filter": {
                        "type": "edge_ngram",
                        "min_gram": 1,
                        "max_gram": 20,
                        "token_chars": ["letter", "digit", "whitespace"]
                    },
                    "thai_english_synonym_filter": {
                        "type": "synonym_graph",
                        "synonyms_path": "analysis/synonyms.txt",
                        "expand": True
                    }
                },
                "analyzer": {
                    "thai_autocomplete_analyzer": {
                        "type": "custom",
                        "tokenizer": "icu_tokenizer",
                        "filter": [
                            "lowercase",
                            "icu_folding",
                            "thai_edge_ngram_filter"
                        ]
                    },
                    "thai_synonym_analyzer": {
                        "type": "custom",
                        "tokenizer": "icu_tokenizer",
                        "filter": [
                            "lowercase",
                            "icu_folding",
                            "thai_english_synonym_filter"
                        ]
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "กลุ่ม": {
                    "type": "text",
                    "analyzer": "thai_autocomplete_analyzer",
                    "search_analyzer": "thai_synonym_analyzer"
                },
                "ลำดับ": {"type": "float"},
                "ชื่อ": {
                    "type": "text",
                    "analyzer": "thai_autocomplete_analyzer",
                    "search_analyzer": "thai_synonym_analyzer"
                },
                "รายละเอียด": {
                    "type": "text",
                    "analyzer": "thai_autocomplete_analyzer",
                    "search_analyzer": "thai_synonym_analyzer"
                },
                "หน่วย": {"type": "text"},
                "ค่าแฟคเตอร์ (kgCO2e)": {"type": "float"},
                "ข้อมูลอ้างอิง": {
                    "type": "text",
                    "analyzer": "thai_autocomplete_analyzer",
                    "search_analyzer": "thai_synonym_analyzer"
                },
                "วันที่อัพเดท": {"type": "text"},
                "ประเภทแฟคเตอร์": {"type": "text"}
            }
        }
    }

    es.indices.create(index=INDEX_NAME, body=index_settings)
    print(f"Created new index: {INDEX_NAME}")

    for _, row in df.iterrows():
        document = row.to_dict()
        es.index(index=INDEX_NAME, document=document)


# กำหนด DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'extract_emission_data',
    default_args=default_args,
    description='DAG for extracting carbon emission data',
    schedule_interval='0 * * * *',
    start_date=datetime(2025, 1, 1), 
    catchup=False,
) as dag:
    task_extract_cfp = PythonOperator(
        task_id='extract_cfp',
        python_callable=extract_cfp,
        provide_context=True,
    )

    task_extract_cfo = PythonOperator(
        task_id='extract_cfo',
        python_callable=extract_cfo,
        provide_context=True,
    )

    task_merge = PythonOperator(
        task_id='merge_tables',
        python_callable=merge_table,
        provide_context=True,
    )

    task_compare = PythonOperator(
        task_id='compare_tables',
        python_callable=compare_table,
        provide_context=True,
    )

    task_create_index = PythonOperator(
        task_id='create_elasticsearch_index',
        python_callable=create_elasticsearch_index,
        provide_context=True,
    )

    [task_extract_cfp , task_extract_cfo] >> task_merge >> task_compare >> task_create_index

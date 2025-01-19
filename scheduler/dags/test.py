from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch

ELASTICSEARCH_HOST = "https://host.docker.internal:9200"
ELASTICSEARCH_USER = "elastic"
ELASTICSEARCH_PASSWORD = "JODDaUKomoKuPHFM2zEc"


def test_elasticsearch_connection(**kwargs):
    # สร้างการเชื่อมต่อ Elasticsearch
    es = Elasticsearch(
        ELASTICSEARCH_HOST,
        basic_auth=(ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD),
        verify_certs=False  # ข้ามการตรวจสอบ SSL Certificate
    )

    # ตรวจสอบการเชื่อมต่อ
    if es.ping():
        print("Connected to Elasticsearch successfully!")
    else:
        raise Exception("Unable to connect to Elasticsearch")

# การตั้งค่า DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'test_elasticsearch_connection',
    default_args=default_args,
    description='DAG สำหรับทดสอบการเชื่อมต่อ Elasticsearch',
    schedule_interval=None,  # รันเมื่อเรียกใช้เท่านั้น
    start_date=datetime(2025, 1, 1),
    catchup=False,
) as dag:
    task_test_connection = PythonOperator(
        task_id='test_connection',
        python_callable=test_elasticsearch_connection,
        provide_context=True,
    )

    task_test_connection

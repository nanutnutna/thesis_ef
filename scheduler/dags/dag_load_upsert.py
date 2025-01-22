from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import urllib3
import pandas as pd
from io import StringIO
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import numpy as np


URL_CFP = "https://thaicarbonlabel.tgo.or.th/index.php?lang=TH&mod=Y0hKdlpIVmpkSE5mWlcxcGMzTnBiMjQ9"
URL_CFO = "https://thaicarbonlabel.tgo.or.th/index.php?lang=TH&mod=YjNKbllXNXBlbUYwYVc5dVgyVnRhWE56YVc5dQ"
OUTPUT_PATH = r"/opt/airflow/output"
ELASTICSEARCH_HOST = "https://host.docker.internal:9200"
ELASTICSEARCH_USER = "elastic"
ELASTICSEARCH_PASSWORD = "JODDaUKomoKuPHFM2zEc"
INDEX_NAME = "emission_data_upsert"

es = Elasticsearch(ELASTICSEARCH_HOST,basic_auth=(ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD),verify_certs=False)
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
    table = table.drop(columns=['ลำดับ'])
    table['ลำดับ'] = range(1,len(table)+1)
    table['เปลี่ยนแปลง'] = current_date.strftime("%Y-%m-%d")
    output = f"{OUTPUT_PATH}/emission_factor_{current_date_str}.csv"
    table.to_csv(output, index=False, encoding='utf-8-sig')


def elasticsearch_upsert(**kwargs):
    current_table = f"{OUTPUT_PATH}/emission_factor_{current_date_str}.csv"
    previous_table = f"{OUTPUT_PATH}/emission_factor_{last_date_str}.csv"
    try:
        table1 = pd.read_csv(previous_table)
        table1.replace({np.nan: None}, inplace=True)
        table2 = pd.read_csv(current_table)
        table2.replace({np.nan: None}, inplace=True)
        if table1.equals(table2):
            print("No differences found between tables.")
            return
        else:
            differences = table1.compare(table2)
            diff_output = f"{OUTPUT_PATH}/differences_{current_date_str}.csv"
            differences.to_csv(diff_output, index=False, encoding='utf-8-sig')
            print(f"Differences saved to {diff_output}")
            merged = pd.merge(table1, table2, on="ลำดับ", suffixes=('_df1', '_df2'))

            merged['Difference'] = merged.apply(
                lambda row: 'Changed' if any(
                    row[f"{col}_df1"] != row[f"{col}_df2"]
                    for col in ["กลุ่ม", "ชื่อ", "รายละเอียด", "หน่วย", "ค่าแฟคเตอร์ (kgCO2e)", "ข้อมูลอ้างอิง", "วันที่อัพเดท", "ประเภทแฟคเตอร์"]
                ) else 'Unchanged',
                axis=1)
            changed_rows = merged[merged['Difference'] == 'Changed']
            print(changed_rows)
            update_docs = changed_rows.apply(
                lambda row: {
                    "_op_type": "update",
                    "_id": row["ลำดับ"],
                    "_index": f"{INDEX_NAME}", 
                    "doc": {
                        "กลุ่ม": row["กลุ่ม_df2"],
                        "ชื่อ": row["ชื่อ_df2"],
                        "รายละเอียด": row["รายละเอียด_df2"],
                        "หน่วย": row["หน่วย_df2"],
                        "ค่าแฟคเตอร์ (kgCO2e)": row["ค่าแฟคเตอร์ (kgCO2e)_df2"],
                        "ข้อมูลอ้างอิง": row["ข้อมูลอ้างอิง_df2"],
                        "วันที่อัพเดท": row["วันที่อัพเดท_df2"],
                        "ประเภทแฟคเตอร์": row["ประเภทแฟคเตอร์_df2"],
                        "เปลี่ยนแปลง": row["เปลี่ยนแปลง_df2"]
                    }
                },
                axis=1
            ).tolist()
            bulk(es, update_docs)
            print("Updated successfully!")

    except Exception as e:
        print(f"Error during upsert: {e}")


def elasticsearch_insert(**kwargs):
    current_table = f"{OUTPUT_PATH}/emission_factor_{current_date_str}.csv"

    try:
        table = pd.read_csv(current_table)
        table.replace({np.nan: None}, inplace=True)

        documents = table.apply(
            lambda row: {
                "_op_type": "index",
                "_index": INDEX_NAME,
                "_id": row["ลำดับ"],
                "_source": {
                    "กลุ่ม": row["กลุ่ม"],
                    "ชื่อ": row["ชื่อ"],
                    "รายละเอียด": row["รายละเอียด"],
                    "หน่วย": row["หน่วย"],
                    "ค่าแฟคเตอร์ (kgCO2e)": row["ค่าแฟคเตอร์ (kgCO2e)"],
                    "ข้อมูลอ้างอิง": row["ข้อมูลอ้างอิง"],
                    "วันที่อัพเดท": row["วันที่อัพเดท"],
                    "ประเภทแฟคเตอร์": row["ประเภทแฟคเตอร์"],
                    "เปลี่ยนแปลง": row["เปลี่ยนแปลง"]
                }
            },
            axis=1
        ).tolist()

        bulk(es, documents)
        print(f"Inserted {len(documents)} records successfully into {INDEX_NAME}.")
    
    except Exception as e:
        print(f"Error during Elasticsearch insert: {e}")


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'extract_emission_data_upsert',
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

    # task_upsert_index = PythonOperator(
    #     task_id='elasticsearch_upsert',
    #     python_callable=elasticsearch_upsert,
    #     provide_context=True,
    # )

    task_insert_index = PythonOperator(
        task_id='elasticsearch_insert',
        python_callable=elasticsearch_insert,
        provide_context=True,
    )

    # task_insert_index 



    [task_extract_cfp , task_extract_cfo] >> task_merge >> task_insert_index

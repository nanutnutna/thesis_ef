from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import urllib3
import pandas as pd
from io import StringIO
from elasticsearch.helpers import bulk
import pandasql as ps
import numpy as np
import re
import os
import math
from tqdm import tqdm


OUTPUT_PATH = r"/opt/airflow/output"
CURRENT_DATE = datetime.strftime(datetime.now(),"%Y%m%d")
INPUT_PATH = r"/opt/airflow/input"
ELASTICSEARCH_HOST = "https://host.docker.internal:9200"
ELASTICSEARCH_USER = "elastic"
ELASTICSEARCH_PASSWORD = "JODDaUKomoKuPHFM2zEc"


import re

def convert_to_thai_date(date_string):
    """
    แปลงวันที่เป็นรูปแบบ MMM yyyy (พ.ศ.) เช่น Dec 2562, Jul 2565
    """
    if pd.isna(date_string) or not isinstance(date_string, str):
        return date_string
    
    # Dictionary สำหรับแปลงเดือน (3 ตัวอักษร)
    month_mapping = {
        'Jan': 'Jan', 'January': 'Jan',
        'Feb': 'Feb', 'February': 'Feb',
        'Mar': 'Mar', 'March': 'Mar',
        'Apr': 'Apr', 'April': 'Apr',
        'May': 'May',
        'Jun': 'Jun', 'June': 'Jun',
        'Jul': 'Jul', 'July': 'Jul',
        'Aug': 'Aug', 'August': 'Aug',
        'Sep': 'Sep', 'September': 'Sep',
        'Oct': 'Oct', 'October': 'Oct',
        'Nov': 'Nov', 'November': 'Nov',
        'Dec': 'Dec', 'December': 'Dec'
    }
    
    # Dictionary สำหรับแปลงจากตัวเลขเป็นเดือน
    number_to_month = {
        '01': 'Jan', '1': 'Jan',
        '02': 'Feb', '2': 'Feb',
        '03': 'Mar', '3': 'Mar',
        '04': 'Apr', '4': 'Apr',
        '05': 'May', '5': 'May',
        '06': 'Jun', '6': 'Jun',
        '07': 'Jul', '7': 'Jul',
        '08': 'Aug', '8': 'Aug',
        '09': 'Sep', '9': 'Sep',
        '10': 'Oct',
        '11': 'Nov',
        '12': 'Dec'
    }
    
    # กรณี 1: รูปแบบ "Dec 2019", "July 2022" - ไม่ต้องทำอะไร
    match = re.search(r'([A-Za-z]+)\s+(\d{4})', date_string)
    if match:
        month_name, year = match.groups()
        month_short = month_mapping.get(month_name, month_name[:3])
        
        # ถ้าเป็น format Dec 2019 อยู่แล้ว ไม่ต้องทำอะไร
        return f"{month_short} {year}"
    
    # กรณี 2: รูปแบบ "29/11/2565", "24/02/2568" - ลบ 543
    match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', date_string)
    if match:
        day, month, year = match.groups()
        year_int = int(year)
        month_name = number_to_month.get(month, 'Jan')
        
        # ลบ 543 เฉพาะปี พ.ศ. (> 2500)
        if year_int > 2500:
            thai_year = year_int - 543
        else:
            thai_year = year_int
            
        return f"{month_name} {thai_year}"
    
    # กรณี 3: มีแค่ปี เช่น "2565", "2568" - ลบ 543
    match = re.search(r'(\d{4})', date_string)
    if match:
        year = match.group(1)
        year_int = int(year)
        
        # ลบ 543 เฉพาะปี พ.ศ. (> 2500)
        if year_int > 2500:
            thai_year = year_int - 543
        else:
            thai_year = year_int
            
        return f"Jan {thai_year}"
    
    # ถ้าไม่ตรงกับรูปแบบไหน ส่งกลับเหมือนเดิม
    return date_string


def extract_cfp_cfo():
    pass

def extract_cfo():
    pass

def extract_carbon_label():
    lst_license = []
    lst_imgs_url,lst_img_details = [],[]
    lst_company = []

    url = f'https://thaicarbonlabel.tgo.or.th/index.php?lang=TH&mod=Y0hKdlpIVmpkSE5mWVhCd2NtOTJZV3c9&page=1'
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.content, 'html.parser')
    product = int(soup.find_all(class_='p-caption')[0].text.split()[-2].replace(',',''))
    display = len(soup.find_all(class_='row-fluid approval-block') + soup.find_all(class_='row-fluid approval-block block-hilight'))
    t_page = math.ceil(product/display)
    for num in tqdm(range(1,t_page+1)):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        # URL of the webpage
        url = f'https://thaicarbonlabel.tgo.or.th/index.php?lang=TH&mod=Y0hKdlpIVmpkSE5mWVhCd2NtOTJZV3c9&page={num}'
        response = requests.get(url, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')

        # License
        license_p = soup.find_all(class_='approval-text-info')
        for i, element in enumerate(license_p, start=1):
            h4_tags = element.find_all('h4')  # Find all <h4> inside the current element
            if h4_tags:
                for h4 in h4_tags:
                    lst_license.append(h4.text)
            else:
                print(f"Section {i}: No <h4> found inside this element.")

        # Images
        approval_text_elements = soup.find_all(class_='span9 approval-text')
        for i, element in enumerate(approval_text_elements, start=1):
            img_tags = element.find_all('img')  # Find all <img> inside the current element
            if img_tags:
                for img in img_tags:
                    img_src = img.get('src')
                    img_alt = img.get('alt', 'No alt attribute')
                    lst_imgs_url.append(img_src)
                    lst_img_details.append(img_alt)
            else:
                print(f"Section {i}: No <img> found inside this element.")
        # Company name
        approval_company = soup.find_all(class_='approval-company')
        for i, element in enumerate(approval_company, start=1):
            company_tags = element.text
            # print(company_tags)
            lst_company.append(company_tags)


    df = pd.DataFrame({'License':lst_license,'img_URL':lst_imgs_url,'Detail':lst_img_details,'Company_name':lst_company})
    df.to_csv(f'{OUTPUT_PATH}/url_imges_detail_{CURRENT_DATE}.csv',index=False,encoding='utf-8-sig')

    df = pd.read_csv(f"{OUTPUT_PATH}/url_imges_detail_{CURRENT_DATE}.csv")

    label = r"https://thaicarbonlabel.tgo.or.th/index.php?lang=TH&mod=WTJGMFlXeHZadz09&action=Y0c5emRBPT0&section=0&industry=0&style=_TABLE&sorting=_ASC&year=0&quarter=0"
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    response = requests.get(label, verify=False)
    soup = BeautifulSoup(response.content, 'html.parser')
    seq, lin, name, detail, industry, ap_date, ef, unit, limit, contract, phone, mail =[], [], [], [], [], [], [], [], [], [], [], []
    tot = []
    ## tag table
    tr = soup.find_all(class_='odd')
    for i, element in enumerate(tr, start=1):
        data = element.text
        tot.append(data.replace('\n','|'))


    for data in tot:
        raw_data = data.split('|')
        seq.append(str(raw_data[1]))
        lin.append(raw_data[2])
        name.append(raw_data[3])
        detail.append(raw_data[4])
        industry.append(raw_data[5])
        ap_date.append(raw_data[6])
        ef.append(raw_data[7])
        unit.append(raw_data[8])
        limit.append(raw_data[9])
        contract.append(raw_data[10])
        phone.append(raw_data[11])
        mail.append(raw_data[12])

    df = pd.DataFrame({'Seq':seq,'License':lin,'Name':name,'Detail':detail,'Industrials':industry,'ApproveDate':ap_date,'EF':ef,'Unit':unit,'Scope':limit,'Contract':contract,'Phone':phone,'Mail':mail})
    df.to_csv(f'{OUTPUT_PATH}/CFP_Label_{CURRENT_DATE}.csv',index=False,encoding='utf-8-sig')

    join_type = "inner"

    df1 = pd.read_csv(f"{OUTPUT_PATH}/CFP_Label_{CURRENT_DATE}.csv")
    df2 = pd.read_csv(f"{OUTPUT_PATH}/url_imges_detail_{CURRENT_DATE}.csv")

    if join_type == "left":
        q = """ select Seq,df1.License,df1.Name,df1.Detail,Industrials,ApproveDate,EF,Unit,Scope,Contract,Phone,Mail,df2.Company_name from df1
        left join df2 on df1.License = df2.License or df1.Name = df2.Detail"""
    elif join_type == "inner":
        q = """ select Seq,df1.License,df1.Name,df1.Detail,Industrials,ApproveDate,EF,Unit,Scope,Contract,Phone,Mail,df2.Company_name from df1
        inner join df2 on df1.License = df2.License and df1.Name = df2.Detail and df1.EF is not null"""

    new_df = ps.sqldf(q)
    new_df.fillna('NULL',inplace=True)
    new_df.to_csv(f'{OUTPUT_PATH}/{join_type}_join_{CURRENT_DATE}.csv',index=False,encoding='utf-8-sig') 

def merge_table(**kwargs):   

    t1t2 = pd.read_csv(f'{INPUT_PATH}/CFP_CFO_Init.csv')
    t3 = pd.read_csv(f'{OUTPUT_PATH}/inner_join_{CURRENT_DATE}.csv')

    category = pd.concat([t1t2['กลุ่ม'],t3['Industrials']],axis=0,ignore_index=True)
    name = pd.concat([t1t2['ชื่อ'],t3['Name']],axis=0,ignore_index=True)
    details = pd.concat([t1t2['รายละเอียด'],t3['Detail']],axis=0,ignore_index=True)
    unit = pd.concat([t1t2['หน่วย'],t3['Unit']],axis=0,ignore_index=True)
    ef = pd.concat([t1t2['ค่าแฟคเตอร์ (kgCO2e/หน่วย)'],t3['EF']],axis=0,ignore_index=True)
    reference = pd.concat([t1t2['แหล่งข้อมูลอ้างอิง'],t3['Company_name']],axis=0,ignore_index=True)
    last_updated = pd.concat([t1t2['วันที่อัพเดท'],t3['ApproveDate']],axis=0,ignore_index=True)

    # new table
    table = pd.DataFrame({
        'Category': category,
        'Name': name,
        'Detail': details,
        'Unit': unit,
        'Factor': ef,
        'Reference': reference,
        'Last_Updated': last_updated
    })

    table.to_json(f'{OUTPUT_PATH}/combine_{CURRENT_DATE}.json',orient='records',indent=4,force_ascii=False)
    with open(f'{OUTPUT_PATH}/combine_{CURRENT_DATE}.json', 'r', encoding='utf-8') as f:
        json_str = f.read()
    json_str = json_str.replace('\\/', '/')
    json_str = json_str.replace('null','"NULL"')

    with open(f'{OUTPUT_PATH}/combine_{CURRENT_DATE}.json', 'w', encoding='utf-8') as f:
        f.write(json_str)


    destination_file = os.path.join(OUTPUT_PATH, f'combine_{CURRENT_DATE}.json')
    with open(destination_file, 'w', encoding='utf-8') as f:
        f.write(json_str)

def elasticsearch_upsert(**kwargs):
    pass


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'thai_carbon_label_etl',
    default_args=default_args,
    description='Thai Carbon Label ETL Pipeline',
    schedule_interval=timedelta(days=1),  # รันทุกวัน
    catchup=False,
) as dag:

# สร้าง Tasks
    task_extract_cfp_cfo = PythonOperator(
        task_id='extract_cfp_cfo',
        python_callable=extract_cfp_cfo,
        dag=dag,
    )

    task_extract_cfo = PythonOperator(
        task_id='extract_cfo',
        python_callable=extract_cfo,
        dag=dag,
    )

    task_extract_carbon_label = PythonOperator(
        task_id='extract_carbon_label',
        python_callable=extract_carbon_label,
        dag=dag,
    )

    task_merge_table = PythonOperator(
        task_id='merge_table',
        python_callable=merge_table,
        dag=dag,
    )

    task_elasticsearch_upsert = PythonOperator(
        task_id='elasticsearch_upsert',
        python_callable=elasticsearch_upsert,
        dag=dag,
    )


    [task_extract_cfp_cfo, task_extract_cfo, task_extract_carbon_label] >> task_merge_table >> task_elasticsearch_upsert
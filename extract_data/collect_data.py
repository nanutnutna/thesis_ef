import requests
from bs4 import BeautifulSoup
import urllib3
import pandas as pd
from datetime import datetime
from io import StringIO

URL_CFP = "https://thaicarbonlabel.tgo.or.th/index.php?lang=TH&mod=Y0hKdlpIVmpkSE5mWlcxcGMzTnBiMjQ9"
URL_CFO = "https://thaicarbonlabel.tgo.or.th/index.php?lang=TH&mod=YjNKbllXNXBlbUYwYVc5dVgyVnRhWE56YVc5dQ"
OUTPUT_PATH = r"C:\Users\Nattapot\Desktop\thesis_ef\extract_data\source"

current_date = datetime.now().strftime("%Y%m%d")

# URL to scrape
def extract_cfp(url=URL_CFP):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    url = "https://thaicarbonlabel.tgo.or.th/index.php?lang=TH&mod=Y0hKdlpIVmpkSE5mWlcxcGMzTnBiMjQ9"

    # Send a GET request
    response = requests.get(url, verify=False)

    # Check if the request was successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'lxml')
        table = soup.find("table",{"class":"table table-striped table-bordered table-hover table-full-width table-customize"})
        df = pd.read_html(StringIO(str(table)))[0]
        
        #re-order
        df = df[['ลำดับ','กลุ่ม','ชื่อ','รายละเอียด','หน่วย','ค่าแฟคเตอร์ (kgCO2e)','ข้อมูลอ้างอิง','วันที่อัพเดท']]
        df['ประเภทแฟคเตอร์'] = "CFP"
    else:
        print(f"Failed to fetch page, status code: {response.status_code}")

    output = f"{OUTPUT_PATH}/emission_factor_cfp_{current_date}.csv"
    df.to_csv(output,index=False,encoding='utf-8-sig')
    return df

def extract_cfo(url=URL_CFO):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    url = "https://thaicarbonlabel.tgo.or.th/index.php?lang=TH&mod=YjNKbllXNXBlbUYwYVc5dVgyVnRhWE56YVc5dQ"


    response = requests.get(url, verify=False)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'lxml')
        table = soup.find("table")
        df = pd.read_html(StringIO(str(table)),header=[1,2])[0]
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
    else:
        print(f"Failed to fetch page, status code: {response.status_code}")

    #save table
    output = f"{OUTPUT_PATH}/emission_factor_cfo_{current_date}.csv"
    df.to_csv(output,index=False,encoding='utf-8-sig')
    return df

def mergetable(t1,t2):
    table = pd.concat([t1,t2],ignore_index=True,)
    output = f"{OUTPUT_PATH}/emission_factor_{current_date}.csv"

    #save table
    table.to_csv(output,index=False,encoding='utf-8-sig')
    return


if __name__ == "__main__":
    print("Extract data from TGO")
    table_cfp = extract_cfp(url=URL_CFP)
    print("Extract table CFP")
    table_cfo = extract_cfo(url=URL_CFO)
    print("Extact table CF")

    print("concat talbe")
    mergetable(table_cfp,table_cfo)
    print("Extract data suscessfully")
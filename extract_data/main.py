import requests
from bs4 import BeautifulSoup
import urllib3
import pandas as pd
from io import StringIO

def extract_data(url:str, output:str):
    """
    Extracts table data from a given URL and saves it as a CSV file.
    """

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    response = requests.get(url, verify=False)
    try:
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
            # table = soup.find("table",{"class":"table table-striped table-bordered table-hover table-full-width table-customize"})
            table = soup.find("table")
            table_str = str(table)
            df = pd.read_html(StringIO(table_str))[0]

            # column_mapping = {
            #     "กลุ่ม": "Group",
            #     "ลำดับ": "Index",
            #     "ชื่อ": "Name",
            #     "รายละเอียด": "Description",
            #     "หน่วย": "Unit",
            #     "ค่าแฟคเตอร์ (kgCO2e)": "Emission_Factor_kgCO2e",
            #     "ข้อมูลอ้างอิง": "Reference",
            #     "วันที่อัพเดท": "Update_Date"
            # }

            # df.rename(columns=column_mapping, inplace=True)
            # # print("Renamed Columns:", df.columns)
            print(f"Table data saved to {output}")
        else:
            print(f"Failed to fetch page, status code: {response.status_code}")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")

    df.to_csv(f'{output}.csv',index=False,encoding='utf-8-sig')
    df.to_json(f'{output}.json',orient='records',indent=4,force_ascii=False)
    return


if __name__ == "__main__":
    url = {"url_CFP":"https://thaicarbonlabel.tgo.or.th/index.php?lang=TH&mod=Y0hKdlpIVmpkSE5mWlcxcGMzTnBiMjQ9",
            "url_CFO":"https://thaicarbonlabel.tgo.or.th/index.php?lang=TH&mod=YjNKbllXNXBlbUYwYVc5dVgyVnRhWE56YVc5dQ",
            "url_approval":"https://thaicarbonlabel.tgo.or.th/index.php?lang=TH&mod=WTJGMFlXeHZadz09&action=Y0c5emRBPT0&section=0&industry=0&style=_TABLE&sorting=_ASC&year=0&quarter=0"}
    for idx,val in enumerate(url.values()):
        file_name='emission_factor'
        extract_data(url=val,output=f"{file_name}_{idx+1}")

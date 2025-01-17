import requests
from bs4 import BeautifulSoup
import urllib3
import pandas as pd
from datetime import datetime

URL_CFP = "https://thaicarbonlabel.tgo.or.th/index.php?lang=TH&mod=Y0hKdlpIVmpkSE5mWlcxcGMzTnBiMjQ9"
URL_CFO = "https://thaicarbonlabel.tgo.or.th/index.php?lang=TH&mod=YjNKbllXNXBlbUYwYVc5dVgyVnRhWE56YVc5dQ"
OUTPUT_PATH = "source"

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
        df = pd.read_html(str(table))[0]
    else:
        print(f"Failed to fetch page, status code: {response.status_code}")

    output = f"{OUTPUT_PATH}/emission_factor_{current_date}.csv"
    df.to_csv(output,index=False,encoding='utf-8-sig')
    return 

def extract_cfo(url=URL_CFO):
    pass
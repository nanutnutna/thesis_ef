import pandas as pd
from datetime import datetime,timedelta

INPUT_PATH = r"C:\Users\Nattapot\Desktop\thesis_ef\extract_data\source"
FILE_NAME_CFO = "emission_factor_cfo"
FILE_NAME_CFP = "emission_factor_cfp"
CONCAT_CFP_CFO = "emission_factor"

current_date = datetime.now()
last_date = datetime.now() - timedelta(days=1)
current_date_str = current_date.strftime("%Y%m%d")
last_date_str = last_date.strftime("%Y%m%d")

# print(current_date_str,last_date_str)


def read_table_csv(filename,date):
    name = f'{INPUT_PATH}\{filename}_{date}.csv'
    return pd.read_csv(name)

def compare_table(table1,table2):
    t1 = read_table_csv(table1)
    t2 = read_table_csv(table2)
    if t1.equals(t2):
        return True
    return 


if __name__ == "__main__":
    table1 = read_table_csv(filename=CONCAT_CFP_CFO,date=current_date_str)
    table2 = read_table_csv(filename=CONCAT_CFP_CFO,date=last_date_str)
    if compare_table(table1,table2):
        print("nothing diff")
    else:
        table1.compare(table2)

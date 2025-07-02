import pandas as pd

df = pd.read_excel('CFP_Init.xlsx')

# columns_name = ['ลำดับที่','ชื่อ','รายละเอียด','หน่วย','ค่าแฟคเตอร์ (kgCO2e/หน่วย)','แหล่งข้อมูลอ้างอิง','วันที่อัพเดท','กลุ่ม']

df = df.apply(lambda x: x.str.replace('\n', ' ').str.replace(r'\s+', ' ', regex=True).str.strip() if x.dtype == 'object' else x)


df.to_csv('CFP_Init.csv', encoding='utf-8-sig')
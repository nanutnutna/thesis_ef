import pandas as pd
thai_synonyms = []
csv_file = r'C:\Users\Nattapot\Desktop\synonyms\synonyms2.csv'
df = pd.read_csv(csv_file,header=None)
for i in range(len(df)):
    row_data = df.iloc[i].dropna().tolist()
    result = ", ".join([str(item) for item in row_data])
    if i == len(df)-1:
        last_result = f'"{result}"'
        # print(result)
    else:
        last_result = f'"{result}",'
        # print(result)
    thai_synonyms.append(result)
# print(thai_synonyms)
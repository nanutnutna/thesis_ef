import json

f = open('results.json', 'r', encoding='utf-8')
data = json.load(f)
t =[i for i in data]
f.close()


for i, doc in enumerate(t):
    print(doc['ชื่อ'])
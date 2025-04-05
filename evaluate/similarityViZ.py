import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import matplotlib as mpl
from matplotlib.font_manager import FontProperties

# ตั้งค่า font Tahoma สำหรับภาษาไทย
plt.rcParams['font.family'] = 'Tahoma'
plt.rcParams['font.sans-serif'] = ['Tahoma'] + plt.rcParams.get('font.sans-serif', [])
plt.rcParams['axes.unicode_minus'] = False

# สร้าง FontProperties object สำหรับ Tahoma
thai_font = FontProperties(family='Tahoma')

english_synonyms = {
    # "agriculture": [" agricultural", " farming", "agronomy"],
    # "anthracite": ["Hard coal", "Black coal", "Heating coal"],
    "diesel": ["diesel fuel", "Diesel oil", "B5", "B10", "B20"],
    "LPG": ["Liquefied Petroleum Gas", "Cooking gas"],
    "Gasoline": ["Petrol", "E10", "E20","Premium gasoline"],
    "Sulfur": ["S", "Pure sulfur", "Elemental sulfur"]
}

thai_synonyms = {
    # "การเกษตร": ["เกษตร", "เกษตรกรรม", "กสิกรรม", "การเพาะปลูก"],
    # "แอนทราไซต์": ["ถ่านหินชนิดแข็ง", "ถ่านหินคุณภาพสูง"],
    "น้ำมันดีเซล": ["ดีเซล", "น้ำมันโซล่า"],
    "แอลพีจี": ["ก๊าซปิโตรเลียมเหลว", "ก๊าซหุงต้มแอลพีจี","ก๊าซแอลพีจี","ก๊าซหุงต้ม"],
    "น้ำมันเบนซิน": ["เบนซิน","แก๊สโซลีน"],
    "ซัลเฟอร์": ["กำมะถัน", "ซัลเฟอร์บริสุทธิ์"]
}

english_words = list(english_synonyms.keys())
thai_words = list(thai_synonyms.keys())
bilingual_dict = {
    # "การเกษตร": "agriculture",
    # "แอนทราไซต์": "anthracite",
    "น้ำมันดีเซล": "diesel",
    "แอลพีจี": "LPG",
    "น้ำมันเบนซิน": "Gasoline",
    "ซัลเฟอร์": "Sulfur"
}

# สร้าง similarity matrix
similarity_matrix = np.zeros((len(thai_words), len(english_words)))

for i, thai_word in enumerate(thai_words):
    for j, english_word in enumerate(english_words):
        # ถ้าอยู่ใน bilingual dictionary จะมีความสัมพันธ์ 1:1
        if bilingual_dict.get(thai_word) == english_word:
            similarity_matrix[i, j] = 1.0
        # อีกวิธีคือเช็คความคล้ายของ synonym sets
        else:
            # ถ้าแปลเป็นภาษาอังกฤษแล้ว คำนั้นเป็น synonym ของคำภาษาอังกฤษที่กำลังเทียบอยู่หรือไม่
            thai_eng_equivalent = bilingual_dict.get(thai_word, "")
            if thai_eng_equivalent in english_synonyms.get(english_word, []):
                similarity_matrix[i, j] = 0.7  # กำหนดค่าความคล้ายคลึงเอง

# สร้าง network graph
G = nx.Graph()

# เพิ่มโหนดสำหรับแต่ละคำ
for word in english_words:
    G.add_node(word, lang='english')
    # เพิ่ม synonyms เป็นโหนดด้วย
    for syn in english_synonyms[word]:
        G.add_node(syn, lang='english')
        G.add_edge(word, syn, weight=0.9)  # เชื่อมคำกับ synonym

for word in thai_words:
    G.add_node(word, lang='thai')
    # เพิ่ม synonyms เป็นโหนดด้วย
    for syn in thai_synonyms[word]:
        G.add_node(syn, lang='thai')
        G.add_edge(word, syn, weight=0.9)  # เชื่อมคำกับ synonym

# เชื่อมคำข้ามภาษาตาม bilingual dictionary
for thai, english in bilingual_dict.items():
    if thai in G.nodes and english in G.nodes:
        G.add_edge(thai, english, weight=1.0, style='dashed')

# กำหนดสี
node_colors = ['#ff9999' if G.nodes[node].get('lang') == 'english' else '#9999ff' for node in G.nodes()]

# วาดกราฟ
plt.figure(figsize=(8, 8))
pos = nx.spring_layout(G, seed=42)
nx.draw_networkx_nodes(G, pos, node_size=300, node_color=node_colors, alpha=0.8)

# แยกการวาด labels ระหว่างภาษาไทยและอังกฤษ
labels = {}
for node in G.nodes():
    labels[node] = node

thai_labels = {n: labels[n] for n in G.nodes() if G.nodes[n].get('lang') == 'thai'}
eng_labels = {n: labels[n] for n in G.nodes() if G.nodes[n].get('lang') == 'english'}

# วาด labels แยกตามภาษา
nx.draw_networkx_labels(G, pos, labels=eng_labels, font_size=10,font_color='black')
nx.draw_networkx_labels(G, pos, labels=thai_labels, font_size=10, font_family='Tahoma',font_color='black')

# แบ่งประเภทเส้นตามน้ำหนัก
solid_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('style') != 'dashed']
dashed_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('style') == 'dashed']

# วาด edge แบบเส้นทึบสำหรับ synonym ในภาษาเดียวกัน
nx.draw_networkx_edges(G, pos, edgelist=solid_edges, width=1.0, alpha=0.5)
# วาด edge แบบเส้นประสำหรับคำข้ามภาษา
nx.draw_networkx_edges(G, pos, edgelist=dashed_edges, width=1.5, alpha=0.7, style='dashed', edge_color='green')


plt.title('Word Synonym Network (Red: English, Blue: Thai)', fontsize=14)
plt.axis('off')
plt.tight_layout()
plt.show()
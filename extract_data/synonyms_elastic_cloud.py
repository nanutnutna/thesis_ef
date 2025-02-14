
from elasticsearch import Elasticsearch
import pandas as pd
import numpy as np

file_path = r"C:\Users\Nattapot\Desktop\thesis_ef\extract_data\synonyms.txt"

client = Elasticsearch(
    "https://201b20f220fd4642a18ad35f13021fe5.asia-southeast1.gcp.elastic-cloud.com:443",
    api_key="Um5jU0FKVUJLcWtQQjJ6NzRNa2Q6MzhwRzNIaHVTdXVIOGZVSm16TElGQQ=="
)


index_name = "emission_data_upsert"
# Python
try:
    info = client.info()
    print("Connected successfully!")
    print(info)
except Exception as e:
    print(f"Connection failed: {e}")

def read_synonyms_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file.readlines() if line.strip()]

# อ่าน synonyms จากไฟล์
synonyms_path = r"C:\Users\Nattapot\Desktop\thesis_ef\extract_data\synonyms.txt"
# ตั้งค่า index
index_settings = {
    "settings": {
        "analysis": {
            "filter": {
                "thai_edge_ngram_filter": {
                    "type": "edge_ngram",
                    "min_gram": 1,
                    "max_gram": 20,
                    "token_chars": ["letter", "digit", "whitespace"]
                },
                "thai_english_synonym_filter": {
                    "type": "synonym_graph",
                    "synonyms": ["Agriculture, agricultural, farming, เกษตร, เกษตรกรรม, กสิกรรม, การเพาะปลูก, การทำไร่ทำนา, การทำการเกษตร",
                        "Anthracite, แอนทราไซต์, ถ่านหินชนิดแข็ง, ถ่านหินคุณภาพสูง",
                        "Bagasse, ชานอ้อย, กากอ้อย",
                        "Benzene, เบนซีน",
                        "Biogas, ไบโอแก๊ส, ก๊าซชีวภาพ, แก๊สชีวภาพ",
                        "Caprolactam, คาโพรแลคแทม, แคปโรแลคแตม",
                        "Carbon dioxide, CO2, คาร์บอนไดออกไซด์, ก๊าซคาร์บอนไดออกไซด์",
                        "Cob, ฝักข้าวโพด, แกนข้าวโพด, ซังข้าวโพด",
                        "Compressed Natural Gas, CNG, NGV, ก๊าซธรรมชาติอัด, ก๊าซเอ็นจีวี, ก๊าซธรรมชาติสำหรับยานยนต์",
                        "Cyclohexane, ไซโคลเฮกเซน",
                        "Diesel, Diesel oil, น้ำมันดีเซล, ดีเซล",
                        "Ethane, อีเทน, ก๊าซอีเทน",
                        "Ethylene, C2H4, เอทิลีน, ก๊าซเอทิลีน",
                        "FUEL WOOD, ฟืน, เชื้อเพลิงไม้, ไม้ฟืน",
                        "Forestry, ป่าไม้, วนศาสตร์, การป่าไม้, การทำป่าไม้",
                        "Fuel oil, น้ำมันเตา, เชื้อเพลิงน้ำมัน",
                        "Gas, ก๊าซ, แก๊ส",
                        "Gasoline, น้ำมันเบนซิน, เบนซิน, แก๊สโซลีน",
                        "Household, ครัวเรือน, บ้านเรือน, ที่อยู่อาศัย",
                        "Industry, อุตสาหกรรม, โรงงาน, โรงงานอุตสาหกรรม",
                        "Jet Kerosene, น้ำมันเครื่องบิน, น้ำมันอากาศยาน, เชื้อเพลิงอากาศยาน, เจ็ทฟูเอล",
                        "LPG, Liquefied Petroleum Gas, ก๊าซปิโตรเลียมเหลว, ก๊าซแอลพีจี, ก๊าซหุงต้ม, แอลพีจี, ก๊าซหุงต้มแอลพีจี, Cooking gas",
                        "Lignite, ลิกไนต์, ถ่านหินลิกไนต์, ถ่านหินสีน้ำตาล",
                        "Methane, CH4, มีเทน, ก๊าซมีเทน",
                        "Mixed C4, มิกซ์ซีโฟร์, ไฮโดรคาร์บอนผสม C4",
                        "Naphtha, แนฟทา, น้ำมันแนฟทา",
                        "Natural gas, ก๊าซธรรมชาติ",
                        "P-xylene, พาราไซลีน, พี-ไซลีน",
                        "Ployvinyl Chloride, PVC, พีวีซี, พอลิไวนิลคลอไรด์",
                        "Polypropylene, PP, พอลิโพรพิลีน, โพลีโพรพิลีน",
                        "Propane, โพรเพน, ก๊าซโพรเพน",
                        "Propylene, โพรพิลีน, โพรพีน",
                        "Styrene Acrylonitrile, SAN, สไตรีนอะคริโลไนไตรล์",
                        "Styrene Monomer, สไตรีนโมโนเมอร์",
                        "Sub-bituminous coal, ถ่านหินซับบิทูมินัส, ถ่านหินกึ่งแข็ง",
                        "Sulfur, กำมะถัน, ซัลเฟอร์, ซัลเฟอร์บริสุทธิ์, Pure sulfur, Elemental sulfur",
                        "Toluene, โทลูอีน, เมทิลเบนซีน",
                        "กระจกนิรภัย, Safety Glass, Tempered Glass, Laminated Glass, กระจกเทมเปอร์, กระจกลามิเนต",
                        "กระจกแผ่นเรียบ, Flat Glass, Float Glass, Sheet Glass, Plate Glass",
                        "กระดาษกล่อง, กระดาษลัง, กล่องกระดาษ, กระดาษสำหรับทำกล่อง, Boxboard, Cardboard, Packaging paper",
                        "กระดาษคราฟท์, กระดาษสีน้ำตาล, กระดาษห่อของ, กระดาษรีไซเคิล, Kraft paper, Brown paper, Recycled paper",
                        "กระดาษพิมพ์เขียน, กระดาษเขียน, กระดาษสำหรับเขียน, กระดาษพิมพ์, Writing paper, Printing paper",
                        "กระดาษหนังสือพิมพ์, กระดาษพิมพ์หนังสือพิมพ์, กระดาษสำหรับหนังสือพิมพ์, กระดาษข่าว, Newsprint, Newspaper paper",
                        "กระถินสดอินทรีย์, กระถินสด, กระถินออร์แกนิก, กระถินเกษตรอินทรีย์, Fresh Leucaena, Organic Leucaena, Organic Fresh Leucaena",
                        "กระเจี๊ยบเขียว, กระเจี๊ยบ, กระเจี๊ยบเขียวสด, Okra, Fresh okra",
                        "กระเทียม, หัวกระเทียม, กระเทียมสด, Garlic, Fresh garlic, Garlic bulb",
                        "กลีเซอรีน, กลีเซอรอล, กลีเซอรีนบริสุทธิ์, Glycerin, Glycerol, Pure glycerin",
                        "น้ำประปา, น้ำใช้งาน, น้ำสะอาด, Tap water, Clean water, Drinking water",
                        "ปศุสัตว์, สัตว์เลี้ยงในฟาร์ม, การเลี้ยงสัตว์, Livestock, Farm animals",
                        "ปิโตรเคมี, อุตสาหกรรมปิโตรเคมี, เคมีภัณฑ์จากปิโตรเลียม, Petrochemicals, Petrochemical industry",
                        "ผลิตภัณฑ์จากก๊าซธรรมชาติ, ผลิตภัณฑ์ก๊าซธรรมชาติ, ก๊าซธรรมชาติแปรรูป, Natural gas products, Processed natural gas",
                        "อาหารสัตว์, อาหารเลี้ยงสัตว์, อาหารสำหรับสัตว์, Animal feed, Livestock feed",
                        "อุตสาหกรรมยางธรรมชาติ, ยางธรรมชาติ, อุตสาหกรรมยาง, Natural rubber industry, Rubber industry, Natural rubber",
                        "กอุตสาหกรรมโรงเลื่อยและโรงอบไม้ยางพารา, โรงเลื่อย, โรงอบไม้, โรงงานไม้ยางพารา, Rubberwood sawmill, Rubberwood drying factory",
                        "เคมีภัณฑ์, สารเคมี, เคมีภัณฑ์อุตสาหกรรม, Chemicals, Chemical products, Industrial chemicals",
                        "เยื่อกระดาษ, เยื่อ, กระดาษเยื่อ, Pulp, Paper pulp, Cellulose pulp",
                        "ไฟฟ้า, พลังงานไฟฟ้า, กระแสไฟฟ้า, Electricity, Electric power, Electrical energy",
                        "ไหมหัตถกรรม, ผ้าไหม, ไหมพื้นเมือง, Handicraft silk, Silk, Traditional silk",
                        "กล้วยหอม, กล้วยหอมทอง, Cavendish banana, Banana, Golden banana",
                        "กล้วยไข่, กล้วยพื้นเมือง, Egg banana, Native banana",
                        "กล้ายางชำถุง, ต้นกล้ายางพารา, ยางพาราชำถุง, Rubber sapling in bag, Rubber tree seedling, Bagged rubber sapling",
                        "กะลาปาล์ม, กะลามะพร้าวปาล์ม, กะลาปาล์มดิบ, Palm kernel shell, PKS, Raw palm shell",
                        "กะหล่ำดอก, ดอกกะหล่ำ, กะหล่ำ, Cauliflower, Flowering cabbage",
                        "กะหล่ำปลี, กะหล่ำหัว, Cabbage, Head cabbage",
                        "กะเพรา, โหระพากะเพรา, กะเพราไทย, Holy basil, Thai basil, Ocimum sanctum",
                        "กากถั่วเหลือง, ถั่วเหลืองบด, กากโปรตีนถั่วเหลือง, Soybean meal, Soybean protein residue, Ground soybean",
                        "กาแฟอราบิกา, อราบิกา, Arabica coffee, Arabica",
                        "กาแฟอราบิก้าคั่วบด, กาแฟคั่วบด, อราบิก้าคั่วบด, Arabica coffee roasted, Roasted coffee, Roasted Arabica",
                        "กาแฟโรบัสตา, โรบัสตา, Robusta coffee, Robusta",
                        "กิ่งไม้ ต้นหญ้าจากสวน, กิ่งไม้, ต้นหญ้า, กิ่งไม้จากสวน, ต้นหญ้าจากสวน, Branches and grass from garden, Garden branches, Garden grass",
                        "กิ่งไม้ยางพารา, กิ่งไม้ยาง, กิ่งยางพารา, Rubber tree branches, Rubberwood branches, Rubber branches",
                        "ก๊าซธรรมชาติแบบผสม, ก๊าซผสม, Mixed natural gas, Natural gas blend, Gas mixture",
                        "ขวดแก้วสีชา, ขวดสีชา, Brown glass bottle, Amber glass bottle",
                        "ขวดแก้วใส, ขวดใส, Clear glass bottle, Transparent glass bottle",
                        "ขิง, ขิงสด, ขิงแห้ง, Ginger, Fresh ginger, Dried ginger",
                        "ขี้เลื่อยไม้, ขี้เลื่อย, ขี้เลื่อยไม้แปรรูป, Sawdust, Wood sawdust, Processed sawdust",
                        "ข่า, ข่าสด, ข่าแห้ง, Galangal, Fresh galangal, Dried galangal",
                        "ข้าวฟ่างหวาน, ข้าวฟ่างสำหรับน้ำตาล, Sweet sorghum, Sorghum for sugar, Sorghum",
                        "ข้าวฟ่างเลี้ยงสัตว์, ข้าวฟ่างอาหารสัตว์, Forage sorghum, Sorghum for feed, Animal feed sorghum",
                        "ข้าวโพดฝักอ่อน, ฝักอ่อนข้าวโพด, Baby corn, Young corn, Corn shoot",
                        "ข้าวโพดหวาน, ข้าวโพดสำหรับบริโภค, Sweet corn, Edible corn, Corn",
                        "คาร์บอนไฟเบอร์, ไฟเบอร์คาร์บอน, เส้นใยคาร์บอน, Carbon fiber, Carbon fibre, Reinforced carbon fiber",
                        "งา, เมล็ดงา, งาดำ, งาขาว, Sesame, Sesame seeds, Black sesame, White sesame",
                        "ฉนวนใยแก้ว, ฉนวน, ใยแก้ว, Glass wool, Fiberglass insulation, Glass fiber insulation",
                        "ชาอูหลง, ชา, อูหลง, Oolong tea, Tea, Wulong tea",
                        "ตะไคร้, ตะไคร้สด, ตะไคร้แห้ง, Lemongrass, Fresh lemongrass, Dried lemongrass",
                        "ต้นกล้าหม่อนชำถุง, ต้นหม่อน, หม่อนชำถุง, Mulberry sapling in bag, Bagged mulberry, Mulberry seedling",
                        "ถั่วดำ, เมล็ดถั่วดำ, ถั่วดำอินทรีย์, Black bean, Organic black bean, Black gram",
                        "ถั่วฝักยาว, ถั่ว, ฝักยาว, Yardlong bean, Long bean, Asparagus bean",
                        "ถั่วลิสง, เมล็ดถั่วลิสง, ถั่วดิน, Peanut, Groundnut, Shelled peanut",
                        "ถั่วฮามาต้าสดอินทรีย์, ถั่วฮามาต้า, ฮามาต้าอินทรีย์, Organic Hamata bean, Fresh Hamata bean, Hamata legume",
                        "ถั่วเขียว, เมล็ดถั่วเขียว, ถั่วเขียวอินทรีย์, Mung bean, Green gram, Organic mung bean",
                        "ถั่วเหลือง, เมล็ดถั่วเหลือง, ถั่วเหลืองแห้ง, Soybean, Soya bean, Dried soybean",
                        "ถั่วเหลืองฝักสด, ถั่วเหลืองสด, ฝักถั่วเหลือง, Fresh soybean pod, Fresh soybean, Green soybean",
                        "ถั่วเหลืองอินทรีย์, ถั่วเหลืองออร์แกนิก, เมล็ดถั่วเหลืองอินทรีย์, Organic soybean, Organic soya bean",
                        "ถั่วแขก, ถั่วฝักสด, แขกถั่ว, Snap bean, Fresh snap bean, Green bean",
                        "ทุเรียน, ทุเรียนสด, ทุเรียนหมอนทอง, Durian, Fresh durian, Monthong durian",
                        "นมผึ้ง, รอยัลเยลลี่, อาหารผึ้ง, Royal jelly, Bee jelly, Apiculture jelly",
                        "น้ำกะทิ, กะทิ, น้ำกะทิสด, Coconut milk, Fresh coconut milk, Creamed coconut",
                        "น้ำตาล, น้ำตาลทราย, น้ำตาลอ้อย, Sugar, Cane sugar, Granulated sugar",
                        "น้ำนมดิบ, นมดิบ, น้ำนม, Raw milk, Fresh milk, Unprocessed milk",
                        "น้ำผึ้งกรอง, น้ำผึ้ง, น้ำผึ้งแท้, Filtered honey, Pure honey, Honey",
                        "น้ำมันงาสกัดเย็น, น้ำมันงา, งาสกัดเย็น, Cold-pressed sesame oil, Sesame oil, Virgin sesame oil",
                        "น้ำมันปาล์มดิบ, น้ำมันปาล์ม, ปาล์มน้ำมันดิบ, Crude palm oil, Palm oil, Unrefined palm oil",
                        "น้ำยางข้น, ยางพาราข้น, น้ำยางพารา, Concentrated latex, Thickened rubber latex, Rubber concentrate",
                        "น้ำยางสด, น้ำยางดิบ, ยางพาราสด, Fresh latex, Raw latex, Natural rubber latex",
                        "น้ำอ่อน, น้ำสำหรับซักล้าง, น้ำบริสุทธิ์, Soft water, Purified water, Washing water",
                        "ปลาดุก, ปลาดุกสด, Catfish, Fresh catfish, Farmed catfish",
                        "ปลาทับทิม, Red tilapia",
                        "ปลานิล, Nile tilapia, Tilapia, Fresh tilapia",
                        "ปลาป่น, โปรตีนปลาป่น, ปลาบด, Fishmeal, Ground fish, Fish protein",
                        "ปลาเป็ด, ปลาเนื้อเป็ด, ปลาสำหรับอาหารสัตว์, Duck fish, Fish for feed, Feed fish",
                        "ปาล์มน้ำมัน, ผลปาล์มน้ำมัน, Palm oil fruit, Oil palm, Palm kernel fruit",
                        "ปีกไม้ยางพารา, ปีกไม้, Rubberwood wings, Rubberwood offcuts",
                        "ผลมะกรูด, มะกรูดสด, มะกรูดผล, Kaffir lime fruit, Fresh kaffir lime, Lime fruit",
                        "ผักกาดหอม, ผักกาด, ผักสลัด, Lettuce, Salad lettuce, Green lettuce",
                        "ผักกาดหัว, หัวไชเท้า, ผักกาดไชเท้า, Daikon, Radish, White radish",
                        "ผักกาดเขียวกวางตุ้ง, ผักกวางตุ้ง, กวางตุ้ง, Bok choy, Chinese mustard, Green mustard",
                        "ผักคะน้า, คะน้า, คะน้าสด, Chinese kale, Kale, Fresh kale",
                        "ผิวมะกรูด, เปลือกมะกรูด, ผิวมะกรูดสด, Kaffir lime peel, Lime skin, Fresh kaffir lime peel",
                        "ผ้า, ผ้าผืน, Cloth, Textile",
                        "ผ้าถัก, ผ้าทอถัก, สิ่งทอถัก, Knitted fabric, Knitwear, Knitted textile",
                        "ผ้าถักจากเส้นด้ายฝ้าย, ผ้าถักฝ้าย, สิ่งทอถักฝ้าย, Cotton knitted fabric, Knitted cotton, Cotton textile",
                        "ผ้าถักจากเส้นด้ายโพลีเอสเตอร์, ผ้าถักโพลิเอสเตอร์, สิ่งทอถักโพลีเอสเตอร์, Polyester knitted fabric, Knitted polyester, Polyester textile",
                        "ผ้าทอ, สิ่งทอทอ, ผ้าผืนทอ, Woven fabric, Woven textile",
                        "ผ้าทอจากเส้นด้ายฝ้าย, ผ้าฝ้ายทอ, Cotton woven fabric, Woven cotton",
                        "ผ้าทอโพลิเอสเทอร์, ผ้าโพลิเอสเทอร์ทอ, สิ่งทอโพลิเอสเทอร์, Polyester woven fabric, Woven polyester, Polyester fabric",
                        "ผ้าอ้อมเด็กทำด้วยกระดาษ, ผ้าอ้อมกระดาษ, ผ้าอ้อมใช้แล้วทิ้ง, Disposable baby diaper, Paper baby diaper, Baby nappy",
                        "ฝรั่ง, ฝรั่งสด, ฝรั่งผลไม้, Guava, Fresh guava, Tropical guava",
                        "พริกขี้หนู, พริกเล็ก, พริกเผ็ด, Bird's eye chili, Thai chili, Small chili",
                        "พริกชี้ฟ้า, พริกเม็ดใหญ่, พริกเขียวชี้ฟ้า, Long chili, Green chili, Large chili",
                        "พริกชี้ฟ้าแดง, พริกแดงชี้ฟ้า, พริกแดงเม็ดใหญ่, Red long chili, Red chili, Large red chili",
                        "พริกหวาน, พริกหยวกหวาน, พริกสลัด, Bell pepper, Sweet pepper, Capsicum",
                        "พริกไทย, เมล็ดพริกไทย, พริกไทยสด, Pepper, Fresh pepper, Peppercorn",
                        "มะนาว, มะนาวสด, มะนาวผล, Lime, Fresh lime, Citrus lime",
                        "มะพร้าว, มะพร้าวผล, มะพร้าวแก่, Coconut, Mature coconut, Tropical coconut",
                        "มะพร้าวน้ำหอม, มะพร้าวสด, มะพร้าวน้ำหอมผล, Aromatic coconut, Fragrant coconut, Fresh aromatic coconut",
                        "มะม่วง, มะม่วงสุก, มะม่วงดิบ, Mango, Ripe mango, Green mango",
                        "มะเขือพวง, มะเขือพวงสด, มะเขือป่า, Pea eggplant, Turkey berry, Fresh pea eggplant",
                        "มะเขือเทศ, มะเขือเทศสด, มะเขือเทศผล, Tomato, Fresh tomato, Ripe tomato",
                        "มังคุด, มังคุดสด, ราชินีผลไม้, Mangosteen, Fresh mangosteen, Queen of fruits",
                        "มันฝรั่ง, มันฝรั่งสด, มันฝรั่งหัว, Potato, Fresh potato, Potato tuber",
                        "มันสำปะหลัง, มันสำปะหลังสด, มันสำปะหลังหัว, Cassava, Fresh cassava, Tapioca root",
                        "ยางก้อนถ้วย, ยางก้อน, ยางพาราก้อนถ้วย, Cup lump rubber, Rubber lump, Natural rubber cup",
                        "ยางสกิม, ยางพาราสกิม, ยางสกิมมิ่ง, Skim rubber, Rubber skim, Skimmed rubber",
                        "รังไหม, รังไหมสด, รังไหมแห้ง, Silk cocoon, Fresh cocoon, Dried cocoon",
                        "รากผักชี, ผักชีราก, รากสดผักชี, Coriander root, Fresh coriander root, Cilantro root",
                        "ลองกอง, ลองกองสด, ผลลองกอง, Longkong, Fresh longkong, Langsat",
                        "ลำไย, Longan",
                        "ลิ้นจี่, Lychee",
                        "สตรอเบอรี่, สตรอเบอร์รี่สด, สตรอเบอร์รี่ผล, Strawberry, Fresh strawberry, Berry",
                        "สับปะรดผลสด, สับปะรด, สับปะรดสด, Fresh pineapple, Pineapple, Tropical pineapple",
                        "สับปะรดโรงงาน, สับปะรดแปรรูป, สับปะรดสำหรับโรงงาน, Processed pineapple, Factory-grade pineapple, Pineapple for industry",
                        "สิ่งทอ, ผ้าทอ, อุตสาหกรรมสิ่งทอ, Fabric, Textile industry",
                        "สีธรรมชาติ, สีจากธรรมชาติ, สีธรรมชาติสำหรับผ้า, Natural dye, Plant-based dye, Eco-friendly dye",
                        "สุกรขุนชำแหละ, สุกรชำแหละ, เนื้อหมูขุนชำแหละ, Slaughtered pig, Pork carcass, Pig carcass",
                        "สุกรขุนชำแหละอื่นๆ, สุกรแปรรูป, เนื้อสุกรแปรรูป, Processed pig, Processed pork, Pork product",
                        "สุกรขุนมีชีวิต, หมูขุน, สุกรขุนฟาร์ม, Live fattened pig, Live pig, Farm-raised pig",
                        "ส้มเขียวหวาน, ส้มเขียวหวานสด, ส้มผลสด, Tangerine, Fresh tangerine, Mandarin orange",
                        "ส้มโอ, ส้มโอสด, ส้มโอผล, Pomelo, Fresh pomelo, Shaddock",
                        "หญ้ากินนีสดอินทรีย์, หญ้ากินนี, หญ้าอินทรีย์, Organic guinea grass, Fresh guinea grass, Guinea grass",
                        "หญ้ากินนีอินทรีย์ หมักด้วยไซโล, หญ้ากินนีหมักไซโล, หญ้าอินทรีย์หมักไซโล, Silage guinea grass, Organic silage grass, Guinea grass silage",
                        "หญ้ารูซี่สดอินทรีย์, หญ้ารูซี่, หญ้าอินทรีย์รูซี่, Organic ruzigrass, Fresh ruzigrass, Ruzigrass",
                        "หญ้าเนเปียร์สดอินทรีย์, หญ้าเนเปียร์, หญ้าอินทรีย์เนเปียร์, Organic napier grass, Fresh napier grass, Napier grass",
                        "หญ้าแพงโกล่าสดอินทรีย์, หญ้าแพงโกล่า, หญ้าอินทรีย์แพงโกล่า, Organic pangola grass, Fresh pangola grass, Pangola grass",
                        "หนังโคสด, หนังวัว, หนังโค, Fresh cowhide, Cow leather, Fresh cattle hide",
                        "หน่อไม้, หน่อไม้สด, Bamboo shoot, Fresh bamboo shoot, Edible bamboo shoot",
                        "หน่อไม้ฝรั่ง, หน่อฝรั่ง, หน่อไม้สดฝรั่ง, Asparagus, Fresh asparagus, Asparagus spear",
                        "หม่อนผลสด ปลูกแบบทั่วไป, หม่อนผลสด, ผลหม่อน, Fresh mulberry, Mulberry fruit, General mulberry",
                        "หอมหัวใหญ่, หอมใหญ่, หัวหอมใหญ่, Onion, Big onion, Bulb onion",
                        "หอมแดง, หอมเล็ก, หัวหอมแดง, Shallot, Red onion, Small onion",
                        "หอยหลอด, หลอดหอย, Razor clam, Bamboo clam, Fresh razor clam",
                        "หอยหวาน, หอยน้ำเค็มหวาน, Sweet snail, Sweet sea snail, Fresh sweet snail",
                        "หอยแครง, หอยน้ำเค็มแครง, Cockle, Fresh cockle, Blood cockle",
                        "หอยแมลงภู่, หอยน้ำเค็มแมลงภู่, Mussel, Fresh mussel, Green mussel",
                        "องุ่น, องุ่นสด, Grapes, Fresh grapes, Table grapes",
                        "อาหารข้นโคนมอินทรีย์, อาหารโคนม, อาหารอินทรีย์, Organic dairy feed, Concentrated dairy feed, Dairy cattle feed",
                        "อาหารสุกรขุน, อาหารหมูขุน, อาหารสำหรับหมู, Pig fattening feed, Hog feed, Pork feed",
                        "อาหารไก่, อาหารสำหรับไก่, Chicken feed, Poultry feed, Bird feed",
                        "อาหารไก่ไข่, อาหารไก่, อาหารไก่เลี้ยงไข่, Layer chicken feed, Egg chicken feed, Layer feed",
                        "อ้อยคั้นน้ำ, อ้อยสด, อ้อยคั้น, Sugarcane, Fresh sugarcane, Juicing cane",
                        "อ้อยโรงงาน, อ้อยแปรรูป, อ้อยสำหรับโรงงาน, Factory-grade sugarcane, Processed sugarcane, Industrial sugarcane",
                        "เกลือทะเล, เกลือสมุทร, เกลือเม็ดทะเล, Sea salt, Solar salt, Coarse salt",
                        "เกลือสินเธาว์แบบตากลานดิน, เกลือสินเธาว์, เกลือตากลานดิน, Rock salt, Natural salt, Earth-dried salt",
                        "เกสรผึ้ง, เกสรดอกไม้ผึ้ง, Bee pollen, Pollen, Apiculture pollen",
                        "เงาะ, เงาะสด, Rambutan, Fresh rambutan, Tropical rambutan",
                        "เนื้อโคชำแหละ, เนื้อวัวชำแหละ, ชิ้นส่วนเนื้อโค, Slaughtered beef, Processed beef, Beef carcass",
                        "เนื้อโคชำแหละอื่นๆ, เนื้อวัวแปรรูป, ชิ้นส่วนเนื้อวัว, Processed cattle meat, Beef product, Processed beef cuts",
                        "เป็ดเนื้อ, เป็ดสด, เป็ดเลี้ยงเนื้อ, Duck meat, Fresh duck, Farm-raised duck",
                        "เมล็ดข้าวโพดเลี้ยงสัตว์, ข้าวโพดอาหารสัตว์, เมล็ดข้าวโพด, Animal feed corn, Corn for feed, Feed corn",
                        "เมล็ดในปาล์ม, เมล็ดปาล์ม, Palm kernel, Kernel seed, Palm seed",
                        "เยื่อกระดาษชนิดฟอกขาวจากชานอ้อย, เยื่อกระดาษชานอ้อย, เยื่อฟอกขาวชานอ้อย, Bleached bagasse pulp, Sugarcane pulp, Bleached pulp",
                        "เยื่อกระดาษชนิดฟอกขาวจากยูคาลิปตัส, เยื่อกระดาษยูคาลิปตัส, เยื่อฟอกขาวยูคาลิปตัส, Bleached eucalyptus pulp, Eucalyptus pulp",
                        "เยื่อกึ่งเคมี, เยื่อกระดาษกึ่งเคมี, Semi-chemical pulp, Semi-processed pulp",
                        "เศษปลาจากซูริมิ, เศษปลาซูริมิ, Surimi fish scrap, Fish by-product",
                        "เศษปลาจากทูน่า, เศษปลาทูน่า, Tuna fish scrap, Tuna by-product",
                        "เศษยาง, ยางเศษ, เศษยางพารา, Rubber scrap, Rubber waste, Rubber residue",
                        "เศษอาหาร, อาหารเศษ, ขยะอาหาร, Food scrap, Food waste, Food residue",
                        "เศษไม้, ไม้เศษ, ขี้เลื่อยไม้, Wood scrap, Wood residue",
                        "เส้นด้าย, ด้าย, เส้นใย, Yarn, Thread, Fiber",
                        "เส้นด้ายปอกระเจา, ด้ายปอกระเจา, เส้นใยปอกระเจา, Jute yarn, Jute thread, Jute fiber",
                        "เส้นด้ายฝ้าย, ด้ายฝ้าย, เส้นใยฝ้าย, Cotton yarn, Cotton thread, Cotton fiber",
                        "เส้นด้ายฝ้ายสาง, ด้ายฝ้ายสาง, เส้นใยฝ้ายสาง, Carded cotton yarn, Carded cotton thread, Carded cotton",
                        "เส้นด้ายฝ้ายหวี, ด้ายฝ้ายหวี, เส้นใยฝ้ายหวี, Combed cotton yarn, Combed cotton thread, Combed cotton",
                        "เส้นด้ายโพลิเอสเทอร์, ด้ายโพลิเอสเทอร์, เส้นใยโพลิเอสเทอร์, Polyester yarn, Polyester thread",
                        "เส้นใยขนแกะ, ขนแกะ, เส้นใยจากแกะ, Wool fiber, Sheep wool, Wool",
                        "เส้นใยอะคริลิคใยสั้น, ใยอะคริลิค, เส้นใยอะคริลิค, Short acrylic fiber, Acrylic fiber, Synthetic fiber",
                        "เส้นใยเรยอนใยสั้น, ใยเรยอน, เส้นใยเรยอน, Short rayon fiber, Rayon fiber, Synthetic rayon",
                        "เส้นใยโพลีเอสเตอร์, Polyester fiber",
                        "เส้นไหม ย้อมสีธรรมชาติ, ไหมย้อมสีธรรมชาติ, Natural dyed silk, Naturally dyed silk",
                        "เส้นไหม ย้อมสีเคมี, ไหมย้อมสีเคมี, Chemically dyed silk, Chemically processed silk",
                        "เห็ดฟาง, เห็ดสดฟาง, เห็ดฟางสด, Straw mushroom, Fresh straw mushroom, Edible mushroom",
                        "แครอท, แครอทสด, หัวแครอท, Carrot, Fresh carrot, Root carrot",
                        "แตงกวา, แตงกวาสด, ผลแตงกวา, Cucumber, Fresh cucumber, Garden cucumber",
                        "แตงโม, แตงโมสด, ผลแตงโม, Watermelon, Fresh watermelon, Melon",
                        "แร่ธาตุพรีมิกซ์, ธาตุอาหารพรีมิกซ์, แร่ธาตุเสริมอาหาร, Mineral premix, Nutrient premix, Food additive premix",
                        "แร่ธาตุและวิตามินพรีมิกซ์, วิตามินพรีมิกซ์, แร่ธาตุพรีมิกซ์, Mineral and vitamin premix, Premix nutrient, Vitamin premix",
                        "ใบมะกรูด, ใบสดมะกรูด, ใบมะกรูดสด, Kaffir lime leaf, Fresh lime leaf, Lime leaf",
                        "ใบโหระพา, ใบสดโหระพา, โหระพา, Sweet basil leaf, Fresh basil leaf, Basil leaf",
                        "ไก่สดชำแหละ, ไก่ชำแหละ, เนื้อไก่ชำแหละ, Slaughtered chicken, Processed chicken, Chicken carcass",
                        "ไก่สดชำแหละอื่นๆ, ไก่ชำแหละแปรรูป, เนื้อไก่แปรรูป, Processed chicken cuts, Chicken product, Processed poultry",
                        "ไก่สดทั้งตัว, ไก่สด, เนื้อไก่ทั้งตัว, Whole chicken, Fresh whole chicken, Entire chicken",
                        "ไก่เนื้อมีชีวิตจากฟาร์ม, ไก่เนื้อสด, ไก่เนื้อฟาร์ม, Live broiler chicken, Farm-raised chicken, Live poultry",
                        "ไขผึ้ง, ขี้ผึ้ง, ไขจากผึ้ง, Beeswax, Natural beeswax, Wax from bee",
                        "ไข่ไก่, ไข่สด, ไข่สดไก่, Chicken egg, Fresh egg, Hen egg",
                        "ไข่ไหม, ไข่ของไหม, ไหมไข่, Silkworm egg, Silk egg, Egg of silkworm",
                        "ไบโอดีเซล, น้ำมันไบโอดีเซล, เชื้อเพลิงไบโอดีเซล, Biodiesel, Biodiesel fuel, Renewable diesel",
                        "ไม้ยางพาราท่อนสด, ไม้ยางพาราสด, ท่อนไม้ยางพารา, Fresh rubberwood log, Rubberwood log, Fresh timber",
                        "ไม้ยางพาราอัดประสาน, ไม้อัดประสาน, Laminated rubberwood, Engineered timber",
                        "ไม้ยางพาราแปรรูป, ไม้แปรรูป, ยางพาราแปรรูป, Processed rubberwood, Rubberwood lumber, Timber produc"
                        ],
                    "updateable": True
                }
            },
            "analyzer": {
                "thai_autocomplete_analyzer": {
                    "type": "custom",
                    "tokenizer": "icu_tokenizer",
                    "filter": [
                        "lowercase",
                        "icu_folding",
                        "thai_edge_ngram_filter"
                    ]
                },
                "thai_synonym_analyzer": {
                    "type": "custom",
                    "tokenizer": "icu_tokenizer",
                    "filter": [
                        "lowercase",
                        "icu_folding",
                        "thai_english_synonym_filter"
                    ]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "กลุ่ม": {
                "type": "text",
                "analyzer": "thai_autocomplete_analyzer",
                "search_analyzer": "thai_synonym_analyzer"
            },
            "ชื่อ": {
                "type": "text",
                "analyzer": "thai_autocomplete_analyzer",
                "search_analyzer": "thai_synonym_analyzer"
            },
            "รายละเอียด": {
                "type": "text",
                "analyzer": "thai_autocomplete_analyzer",
                "search_analyzer": "thai_synonym_analyzer"
            },
            "หน่วย": {
                "type": "text"
            },
            "ค่าแฟคเตอร์ (kgCO2e)": {
                "type": "float"
            },
            "ข้อมูลอ้างอิง": {
                "type": "text",
                "analyzer": "thai_autocomplete_analyzer",
                "search_analyzer": "thai_synonym_analyzer"
            },
            "วันที่อัพเดท": {
                "type": "text"
            },
            "ประเภทแฟคเตอร์": {
                "type": "text"
            },
            "เปลี่ยนแปลง": {
                "type": "date",
                "format": "yyyy-MM-dd"
            }
        }
    }
}

try:
    # สร้าง index
    response = client.indices.create(
        index=index_name,
        body=index_settings
    )
    print("สร้าง index สำเร็จ:", response)
except Exception as e:
    print("เกิดข้อผิดพลาด:", e)



df = pd.read_csv(r"C:\Users\Nattapot\Desktop\thesis_ef\evaluate\emission_factor_20250210.csv")
df.replace({np.nan: None}, inplace=True)
for _, row in df.iterrows():
    # แยก document content ออกจาก metadata
    document = {
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
    
    try:
        # ส่ง index_name และ id แยกจาก document
        response = client.index(
            index=index_name,
            id=str(row["ลำดับ"]),
            document=document
        )
        print(f"Successfully indexed document {row['ลำดับ']}")
    except Exception as e:
        print(f"Error indexing document {row['ลำดับ']}: {str(e)}")
import pandas as pd

def evaluate_and_save_results(ground_truth, synonym_dict, hybrid_search_function, 
                             bm25_weight=0.5, vector_weight=0.5, output_file="hybrid_evaluation_results.csv"):
    """
    ประเมินผลการค้นหาด้วย hybrid search และบันทึกผลลัพธ์ลงไฟล์ CSV
    
    Args:
        ground_truth: พจนานุกรมของคำค้นหาและ ID ของเอกสารที่เกี่ยวข้อง
        synonym_dict: พจนานุกรม synonym
        hybrid_search_function: ฟังก์ชันที่ใช้ในการค้นหาแบบ hybrid
        bm25_weight: น้ำหนักของการค้นหาแบบ BM25
        vector_weight: น้ำหนักของการค้นหาแบบ Vector
        output_file: ชื่อไฟล์ผลลัพธ์
    """
    results_list = []
    ap_values = []  # เก็บค่า AP ทั้งหมด
    reciprocal_ranks = []  # เก็บค่า Reciprocal Rank ทั้งหมด

    # ค้นหาและประเมินผลสำหรับแต่ละ query
    for key in ground_truth.keys():
        result = hybrid_search_function(
            key, 
            synonym_dict, 
            ground_truth, 
            bm25_weight=bm25_weight, 
            vector_weight=vector_weight
        )
        
        # เก็บผลลัพธ์
        results_list.append({
            "Query": result["query"],
            "Expanded Queries": ", ".join(result["expanded_queries"]),
            "Precision": result["precision"],
            "Recall": result["recall"],
            "F1 Score": result["f1_score"],
            "AP": result["AP"],
            "Reciprocal Rank": result["reciprocal_rank"],
            "Retrieved IDs": ", ".join(result["retrieved_ids"]),
            "Relevant IDs": ", ".join(result["relevant_ids"]),
            "True Positives": result["true_positives"],
            "False Positives": result["false_positives"],
            "False Negatives": result["false_negatives"],
            "BM25 Weight": result["bm25_weight"],
            "Vector Weight": result["vector_weight"]
        })
        
        # เก็บค่า AP และ Reciprocal Rank เพื่อคำนวณค่าเฉลี่ย
        ap_values.append(result["AP"])
        reciprocal_ranks.append(result["reciprocal_rank"])

    # คำนวณค่า MAP (Mean Average Precision) และ MRR (Mean Reciprocal Rank)
    map_score = sum(ap_values) / len(ap_values) if ap_values else 0
    mrr_score = sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0
    
    # คำนวณค่าเฉลี่ยของ Precision และ Recall
    avg_precision = sum(item["Precision"] for item in results_list) / len(results_list) if results_list else 0
    avg_recall = sum(item["Recall"] for item in results_list) / len(results_list) if results_list else 0
    avg_f1 = sum(item["F1 Score"] for item in results_list) / len(results_list) if results_list else 0

    # สร้าง DataFrame จากผลลัพธ์
    df_results = pd.DataFrame(results_list)
    
    # เพิ่มคอลัมน์แสดงค่าเฉลี่ย
    for item in results_list:
        item["MAP"] = map_score
        item["MRR"] = mrr_score
        item["Avg Precision"] = avg_precision
        item["Avg Recall"] = avg_recall
        item["Avg F1"] = avg_f1
    
    # อัพเดท DataFrame
    df_results = pd.DataFrame(results_list)
    
    # บันทึกผลลัพธ์ลงไฟล์ CSV
    df_results.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    # คืนค่า DataFrame และค่าเฉลี่ย
    return {
        "dataframe": df_results,
        "map": map_score,
        "mrr": mrr_score,
        "avg_precision": avg_precision,
        "avg_recall": avg_recall,
        "avg_f1": avg_f1
    }

def evaluate_multiple_weight_combinations(ground_truth, synonym_dict, hybrid_search_function, output_prefix="weight_evaluation"):
    """
    ประเมินผลการค้นหาด้วยหลายค่าน้ำหนักที่แตกต่างกัน และบันทึกผลลัพธ์
    
    Args:
        ground_truth: พจนานุกรมของคำค้นหาและ ID ของเอกสารที่เกี่ยวข้อง
        synonym_dict: พจนานุกรม synonym
        hybrid_search_function: ฟังก์ชันที่ใช้ในการค้นหาแบบ hybrid
        output_prefix: คำนำหน้าชื่อไฟล์ผลลัพธ์
    
    Returns:
        DataFrame สรุปผลการประเมินของแต่ละค่าน้ำหนัก
    """
    # กำหนดค่าน้ำหนักที่ต้องการทดสอบ
    weight_combinations = [
        (1.0, 0.0),  # BM25 เท่านั้น
        (0.8, 0.2),
        (0.6, 0.4),
        (0.5, 0.5),  # น้ำหนักเท่ากัน
        (0.4, 0.6),
        (0.2, 0.8),
        (0.0, 1.0)   # Vector เท่านั้น
    ]
    
    summary_results = []
    
    # ทดสอบแต่ละค่าน้ำหนัก
    for bm25_w, vector_w in weight_combinations:
        # สร้างชื่อไฟล์ผลลัพธ์สำหรับน้ำหนักนี้
        output_file = f"{output_prefix}_bm25_{bm25_w}_vector_{vector_w}.csv"
        
        # ประเมินผลด้วยค่าน้ำหนักนี้
        result = evaluate_and_save_results(
            ground_truth,
            synonym_dict,
            hybrid_search_function,
            bm25_weight=bm25_w,
            vector_weight=vector_w,
            output_file=output_file
        )
        
        # เก็บผลลัพธ์สรุป
        summary_results.append({
            "BM25 Weight": bm25_w,
            "Vector Weight": vector_w,
            "MAP": result["map"],
            "MRR": result["mrr"],
            "Avg Precision": result["avg_precision"],
            "Avg Recall": result["avg_recall"],
            "Avg F1": result["avg_f1"],
            "Result File": output_file
        })
    
    # สร้าง DataFrame สรุป
    summary_df = pd.DataFrame(summary_results)
    
    # บันทึกผลลัพธ์สรุป
    summary_df.to_csv(f"{output_prefix}_summary.csv", index=False, encoding='utf-8-sig')
    
    # หาค่าน้ำหนักที่ให้ผลลัพธ์ดีที่สุด (ตาม MAP)
    best_idx = summary_df["MAP"].idxmax()
    best_weights = summary_df.iloc[best_idx]
    
    print(f"ค่าน้ำหนักที่ให้ผลลัพธ์ดีที่สุด (ตาม MAP):")
    print(f"BM25 Weight: {best_weights['BM25 Weight']}, Vector Weight: {best_weights['Vector Weight']}")
    print(f"MAP: {best_weights['MAP']}, MRR: {best_weights['MRR']}")
    print(f"Avg Precision: {best_weights['Avg Precision']}, Avg Recall: {best_weights['Avg Recall']}, Avg F1: {best_weights['Avg F1']}")
    
    return summary_df

# ตัวอย่างการใช้งาน:
"""
# นำเข้าฟังก์ชัน hybrid_search_and_evaluate ที่สร้างไว้
from hybrid_search import hybrid_search_and_evaluate

# กำหนด ground truth และ synonym dict
ground_truth = {
    "แก๊สโซฮอล์": ["1", "4", "7"],
    "ก๊าซเรือนกระจก": ["2", "3", "5"],
    "carbon dioxide": ["2", "3"],
}

synonym_dict = {
    "แก๊สโซฮอล์": ["แก๊สโซฮอล์", "gasohol", "น้ำมันแก๊สโซฮอล์"],
    "ก๊าซเรือนกระจก": ["ก๊าซเรือนกระจก", "greenhouse gas", "GHG"],
    "carbon dioxide": ["carbon dioxide", "คาร์บอนไดออกไซด์", "CO2"],
}

# ประเมินผลด้วยค่าน้ำหนักเดียว
result = evaluate_and_save_results(
    ground_truth, 
    synonym_dict, 
    hybrid_search_and_evaluate,
    bm25_weight=0.6, 
    vector_weight=0.4
)

print(f"MAP: {result['map']}, MRR: {result['mrr']}")

# ประเมินผลด้วยหลายค่าน้ำหนัก
summary = evaluate_multiple_weight_combinations(
    ground_truth, 
    synonym_dict, 
    hybrid_search_and_evaluate
)
"""
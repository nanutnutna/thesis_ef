from elasticsearch import Elasticsearch
import numpy as np
from dotenv import load_dotenv
import os
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()
CLOUD_ID = os.getenv("ELASTIC_CLOUD_ID")
API_KEY = os.getenv("ELASTIC_API_KEY")
es = Elasticsearch(cloud_id=CLOUD_ID, api_key=API_KEY)

# Define the index and search parameters
INDEX_NAME = "thai_hybrid_search_ef"
BM25_WEIGHT = 0.5
VECTOR_WEIGHT = 0.5
SEARCH_SIZE = 20

# Load model for embedding creation
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# Query set and ground truth
q = [
    {"query": "ก๊าซเรือนกระจก", "relevant_docs": ["1", "2", "5"]},
    {"query": "greenhouse gas", "relevant_docs": ["1", "2", "5"]},
    {"query": "carbon dioxide", "relevant_docs": ["2", "3"]},
]

def evaluate_hybrid_query(es, query, relevant_docs, bm25_weight=BM25_WEIGHT, vector_weight=VECTOR_WEIGHT, size=SEARCH_SIZE):
    """
    Evaluate a single query against Elasticsearch using hybrid search and calculate Precision, Recall, and Rank.
    """
    # Create embedding for query
    query_vector = model.encode(query).tolist()
    
    # Create hybrid search query
    search_query = {
        "query": {
            "bool": {
                "should": [
                    # BM25 search - using synonyms from defined analyzer
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ["ชื่อ^3", "รายละเอียด^2"],
                            "boost": bm25_weight
                        }
                    },
                    # Vector search using knn
                    {
                        "knn": {
                            "field": "text_vector",
                            "query_vector": query_vector,
                            "k": 10,
                            "num_candidates": 100,
                            "boost": vector_weight
                        }
                    }
                ]
            }
        },
        "size": size
    }
    
    # Send query to Elasticsearch
    response = es.search(index=INDEX_NAME, body=search_query)

    # Extract retrieved document IDs
    retrieved_docs = [hit["_id"] for hit in response["hits"]["hits"]]

    # Calculate Precision
    relevant_retrieved = set(retrieved_docs) & set(relevant_docs)
    precision = len(relevant_retrieved) / len(retrieved_docs) if retrieved_docs else 0

    # Calculate Recall
    recall = len(relevant_retrieved) / len(relevant_docs) if relevant_docs else 0

    # Calculate Reciprocal Rank
    reciprocal_rank = 0
    for rank, doc_id in enumerate(retrieved_docs, start=1):
        if doc_id in relevant_docs:
            reciprocal_rank = 1 / rank
            break

    # Calculate Average Precision
    average_precision = 0
    relevant_retrieved_count = 0
    for rank, doc_id in enumerate(retrieved_docs, start=1):
        if doc_id in relevant_docs:
            relevant_retrieved_count += 1
            average_precision += relevant_retrieved_count / rank
    average_precision /= len(relevant_docs) if relevant_docs else 1

    return {
        "precision": precision, 
        "recall": recall, 
        "reciprocal_rank": reciprocal_rank,
        "average_precision": average_precision
    }

def calculate_hybrid_metrics(es, queries, bm25_weight=BM25_WEIGHT, vector_weight=VECTOR_WEIGHT, size=SEARCH_SIZE):
    """
    Evaluate all queries and calculate MAP, MRR, Precision, and Recall.
    """
    precisions = []
    recalls = []
    reciprocal_ranks = []
    average_precisions = []

    for query_data in queries:
        query = query_data["query"]
        relevant_docs = query_data["relevant_docs"]

        # Evaluate the query
        metrics = evaluate_hybrid_query(es, query, relevant_docs, bm25_weight, vector_weight, size)
        
        precisions.append(metrics["precision"])
        recalls.append(metrics["recall"])
        reciprocal_ranks.append(metrics["reciprocal_rank"])
        average_precisions.append(metrics["average_precision"])

    # Calculate Mean Average Precision (MAP) and Mean Reciprocal Rank (MRR)
    map_score = np.mean(average_precisions)
    mrr_score = np.mean(reciprocal_ranks)

    return {
        "Precision": np.mean(precisions),
        "Recall": np.mean(recalls),
        "MAP": map_score,
        "MRR": mrr_score
    }

def evaluate_with_different_weights():
    """
    Evaluate the performance with different weight configurations.
    """
    weight_combinations = [
        {"bm25": 1.0, "vector": 0.0},  # BM25 only
        {"bm25": 0.0, "vector": 1.0},  # Vector only
        {"bm25": 0.7, "vector": 0.3},
        {"bm25": 0.5, "vector": 0.5},
        {"bm25": 0.3, "vector": 0.7}
    ]
    
    results = {}
    
    for weights in weight_combinations:
        bm25_weight = weights["bm25"]
        vector_weight = weights["vector"]
        
        metrics = calculate_hybrid_metrics(es, q, bm25_weight, vector_weight)
        
        weight_key = f"BM25_{bm25_weight:.1f}_VECTOR_{vector_weight:.1f}"
        results[weight_key] = metrics
    
    return results

# Calculate metrics for the default weights
default_metrics = calculate_hybrid_metrics(es, q)
print("\nDefault Weights Evaluation:")
print(f"BM25 Weight: {BM25_WEIGHT}, Vector Weight: {VECTOR_WEIGHT}")
print(f"Precision: {default_metrics['Precision']:.4f}")
print(f"Recall: {default_metrics['Recall']:.4f}")
print(f"Mean Average Precision (MAP): {default_metrics['MAP']:.4f}")
print(f"Mean Reciprocal Rank (MRR): {default_metrics['MRR']:.4f}")

# Evaluate with different weight combinations
print("\nEvaluating different weight combinations...")
weight_results = evaluate_with_different_weights()

print("\nWeight Combination Results:")
for weight_key, metrics in weight_results.items():
    print(f"\n{weight_key}:")
    print(f"Precision: {metrics['Precision']:.4f}")
    print(f"Recall: {metrics['Recall']:.4f}")
    print(f"MAP: {metrics['MAP']:.4f}")
    print(f"MRR: {metrics['MRR']:.4f}")
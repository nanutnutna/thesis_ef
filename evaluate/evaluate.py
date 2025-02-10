from elasticsearch import Elasticsearch
import numpy as np

# Connect to Elasticsearch
es = Elasticsearch("https://localhost:9200",
                   basic_auth=("elastic","JODDaUKomoKuPHFM2zEc"),
                   ca_certs="C:/Users/Nattapot/Documents/elasticsearch-8.17.0/config/certs/http_ca.crt"
)

# Define the index and sample query set
INDEX_NAME = "emission_factors"

# Query set and ground truth
q = [
    {"query": "ก๊าซเรือนกระจก", "relevant_docs": ["1", "2", "5"]},
    {"query": "greenhouse gas", "relevant_docs": ["1", "2", "5"]},
    {"query": "carbon dioxide", "relevant_docs": ["2", "3"]},
]

def evaluate_query(es, q, relevant_docs):
    """
    Evaluate a single query against Elasticsearch and calculate Precision, Recall, and Rank.
    """
    # Send query to Elasticsearch
    response = es.search(index=INDEX_NAME, body={
        "query": {
            "multi_match": {
                "query": q,
                "fields": ["ชื่อ", "Description", "ข้อมูลอ้างอิง"]
            }
        }
    })

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

    return precision, recall, reciprocal_rank

def calculate_metrics(es, queries):
    """
    Evaluate all queries and calculate MAP and MRR.
    """
    precisions = []
    recalls = []
    reciprocal_ranks = []
    average_precisions = []

    for query_data in queries:
        query = query_data["query"]
        relevant_docs = query_data["relevant_docs"]

        precision, recall, reciprocal_rank = evaluate_query(es, query, relevant_docs)
        precisions.append(precision)
        recalls.append(recall)
        reciprocal_ranks.append(reciprocal_rank)

        # Calculate Average Precision for the query
        response = es.search(index=INDEX_NAME, body={
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["ชื่อ", "Description", "ข้อมูลอ้างอิง"]
                }
            }
        })
        retrieved_docs = [hit["_id"] for hit in response["hits"]["hits"]]
        average_precision = 0
        relevant_retrieved_count = 0
        for rank, doc_id in enumerate(retrieved_docs, start=1):
            if doc_id in relevant_docs:
                relevant_retrieved_count += 1
                average_precision += relevant_retrieved_count / rank
        average_precision /= len(relevant_docs) if relevant_docs else 1
        average_precisions.append(average_precision)

    # Calculate Mean Average Precision (MAP) and Mean Reciprocal Rank (MRR)
    map_score = np.mean(average_precisions)
    mrr_score = np.mean(reciprocal_ranks)

    return {
        "Precision": np.mean(precisions),
        "Recall": np.mean(recalls),
        "MAP": map_score,
        "MRR": mrr_score
    }

# Calculate and display metrics
metrics = calculate_metrics(es, q)
print("Evaluation Metrics:")
print(f"Precision: {metrics['Precision']:.2f}")
print(f"Recall: {metrics['Recall']:.2f}")
print(f"Mean Average Precision (MAP): {metrics['MAP']:.2f}")
print(f"Mean Reciprocal Rank (MRR): {metrics['MRR']:.2f}")

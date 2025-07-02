from elasticsearch import Elasticsearch
import numpy as np
from dotenv import load_dotenv
import os
from sentence_transformers import SentenceTransformer
from elastic_connection import ElasticsearchConnection


es = ElasticsearchConnection.get_instance()
INDEX_NAME = "combine"
BM25_WEIGHT = 0.6
VECTOR_WEIGHT = 1 - BM25_WEIGHT
SEARCH_SIZE = 50
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')



def evaluate_query(es, query, relevant_docs, bm25_weight=BM25_WEIGHT, vector_weight=VECTOR_WEIGHT, size=SEARCH_SIZE):
    """
    Evaluate a single query against Elasticsearch using hybrid search and calculate MRR.
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
                            "fields": ["Name^2", "Category"],
                            "boost": bm25_weight
                        }
                    },
                    # Vector search using knn
                    {
                        "script_score": {
                                    "query": {"match_all": {}},
                                    "script": {
                                        "source": "cosineSimilarity(params.query_vector, 'text_vector') + 1.0",
                                        "params": {"query_vector": query_vector}
                                    },
                                    "boost": vector_weight
                        }
                    }
                ]
            }
        },
        "size": size
    }
    
    # Execute search
    response = es.search(index="your_index_name", body=search_query)  # แก้ชื่อ index
    search_results = response['hits']['hits']
    
    # Calculate Reciprocal Rank
    reciprocal_rank = 0
    for rank, hit in enumerate(search_results, 1):  # rank starts from 1
        doc_id = hit['_id']  # หรือ hit['_source']['id'] ตามโครงสร้างข้อมูล
        
        if doc_id in relevant_docs:
            reciprocal_rank = 1.0 / rank
            break
    
    return reciprocal_rank


def calculate_mrr(es, queries_and_relevant_docs, bm25_weight=BM25_WEIGHT, vector_weight=VECTOR_WEIGHT, size=SEARCH_SIZE):
    """
    Calculate Mean Reciprocal Rank (MRR) for multiple queries.
    
    Args:
        es: Elasticsearch client
        queries_and_relevant_docs: List of tuples [(query, relevant_docs_list), ...]
        
    Returns:
        float: MRR score
    """
    reciprocal_ranks = []
    
    for query, relevant_docs in queries_and_relevant_docs:
        rr = evaluate_query(es, query, relevant_docs, bm25_weight, vector_weight, size)
        reciprocal_ranks.append(rr)
        print(f"Query: '{query}' -> RR: {rr:.4f}")
    
    # Calculate MRR
    mrr = sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0
    
    print(f"\nMean Reciprocal Rank (MRR): {mrr:.4f}")
    return mrr


# Example usage
if __name__ == "__main__":
    # Test queries with expected relevant documents
    test_queries = [
        ("สมาร์ทโฟน", ["phone_001", "phone_002", "phone_003"]),
        ("แล็ปท็อป", ["laptop_001", "laptop_002"]),
        ("หูฟังไร้สาย", ["headphone_001", "headphone_002"])
    ]
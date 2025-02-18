from langchain.chains import RetrievalQA
from langchain.vectorstores import ElasticVectorSearch
from langchain_ollama import OllamaLLM
from langchain_huggingface import HuggingFaceEmbeddings
from elasticsearch import Elasticsearch

# ตั้งค่า Elasticsearch
es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", "JODDaUKomoKuPHFM2zEc"),
    ca_certs="C:/Users/Nattapot/Documents/elasticsearch-8.17.0/config/certs/http_ca.crt"
)

# ตั้งค่า Embedding และ LLM
embedding_model = HuggingFaceEmbeddings(model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
llm = OllamaLLM(model="gemma2", base_url="http://localhost:11434")

# สร้าง Vector Search
vector_search = ElasticVectorSearch(
    elasticsearch_url="https://localhost:9200",
    index_name="emission_data_upsert",
    embedding=embedding_model
)

# ตั้งคำถาม
question = "ค่าแฟคเตอร์ของกลุ่มปิโตรเคมี"

# ดึงข้อมูลด้วย Vector Search
retrieved_docs = vector_search.as_retriever(search_kwargs={"k": 5}).invoke({"query": question})
print("Retrieved Documents:", retrieved_docs)

# สร้าง QA Chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vector_search.as_retriever(search_kwargs={"k": 5}),
    return_source_documents=True
)

# ตอบคำถามด้วย LLM
result = qa_chain.invoke({"query": question})
print("Answer:", result["result"])
print("Source Documents:", result["source_documents"])




question = "ค่าแฟคเตอร์ของกลุ่มปิโตรเคมี"
question_embedding = embedding_model.embed_query(question)

response = es.search(
    index="emission_data_upsert",
    body={
        "_source": ["ชื่อ", "รายละเอียด", "กลุ่ม", "ค่าแฟคเตอร์ (kgCO2e)"],
        "query": {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                    "params": {"query_vector": question_embedding}
                }
            }
        }
    }
)

print(response)

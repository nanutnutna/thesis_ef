# from fastapi import Query, APIRouter
# from langchain.chains import RetrievalQA
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_elasticsearch import ElasticsearchStore
# from langchain_ollama import OllamaLLM
# from elasticsearch import Elasticsearch
# import urllib3

# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# INDEX_NAME = "emission_data_upsert"

# router = APIRouter()

# # เชื่อมต่อ Elasticsearch
# es = Elasticsearch(
#     "https://localhost:9200",
#     basic_auth=("elastic", "JODDaUKomoKuPHFM2zEc"),
#     ca_certs="C:/Users/Nattapot/Documents/elasticsearch-8.17.0/config/certs/http_ca.crt"
# )

# # ตั้งค่า Embedding
# embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# # สร้าง ElasticVectorSearch
# vector_search = ElasticsearchStore(
#     es_connection=es,
#     index_name=INDEX_NAME,
#     embedding=embedding_model,
#     # return_source_documents=True
# )

# # ตั้งค่า Ollama LLM
# llm = OllamaLLM(
#     model="gemma2",
#     base_url="http://localhost:11434"
# )

# # สร้าง RetrievalQA Chain
# qa_chain = RetrievalQA.from_chain_type(
#     llm=llm,
#     retriever=vector_search.as_retriever(),
#     return_source_documents=True,
# )



# # @router.get("/query")
# # async def query_emissions(query: str = Query(..., description="The query to search the emissions data")):
# #     try:
# #         # รัน RetrievalQA Chain
# #         result = qa_chain.invoke({"query": query})

# #         return {
# #             "response": result["result"],
# #             "sources": [doc.metadata for doc in result["source_documents"]]
# #         }
# #     except Exception as e:
# #         return {"error": f"An error occurred: {str(e)}"}

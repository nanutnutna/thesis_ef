from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_elasticsearch import ElasticsearchStore
from langchain_ollama import OllamaLLM
from elasticsearch import Elasticsearch


INDEX_NAME = "emission_data_upsert"


router = APIRouter()
es = Elasticsearch("https://localhost:9200",
                   basic_auth=("elastic","JODDaUKomoKuPHFM2zEc"),
                   ca_certs="C:/Users/Nattapot/Documents/elasticsearch-8.17.0/config/certs/http_ca.crt"
)


embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

vector_search = ElasticsearchStore(
    es_connection=es,
    index_name=INDEX_NAME,
    embedding=embedding_model, 
)

llm = OllamaLLM(
    model="gemma2",
    base_url="http://localhost:11434"
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vector_search.as_retriever(),
)

question = "Emission factor of LPG in transportation"


response = qa_chain.run(question)
print(f"Answer: {response}")

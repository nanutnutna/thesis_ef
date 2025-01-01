from fastapi import FastAPI
from routers import search

app = FastAPI()
app.include_router(search.router)

@app.get("/")
async def root():
    return {"message": "Welcomr to Elasticsearch FastAPI API"}
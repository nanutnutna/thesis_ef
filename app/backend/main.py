from fastapi import FastAPI
from routers import search
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.include_router(search.router)

@app.get("/")
async def root():
    return {"message": "Welcomr to Elasticsearch FastAPI API"}




app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # หรือกำหนดเป็น ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
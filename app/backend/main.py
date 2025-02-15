from fastapi import FastAPI
from routers import search
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles


app = FastAPI()
app.include_router(search.router)
# app.include_router(llm.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # หรือกำหนดเป็น ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# app.mount("/static",StaticFiles(directory="images"))


@app.get("/")
async def root():
    return {"message": "Welcome to Elasticsearch FastAPI API"}
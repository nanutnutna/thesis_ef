from fastapi import FastAPI
from app.backend.routers import searchcfpcombine
from routers import searchcfplabel,searchcfp,searchcfo
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()
app.include_router(searchcfplabel.router)
app.include_router(searchcfp.router)
app.include_router(searchcfo.router)
app.include_router(searchcfpcombine.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# app.mount("/static",StaticFiles(directory="images"))


@app.get("/")
async def root():
    return {"message": "Welcome to Emission Factor Search"}
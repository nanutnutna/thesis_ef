from fastapi import FastAPI
from routers import searchcfplabel,searchcfp,searchcfo,searchcfpcombine,searchcfpcombine_no_synonyms,searchccombine_keyword_no_synonyms,searchccombine_keyword_with_synnyms,search_cloud
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()
app.include_router(searchcfplabel.router)
app.include_router(searchcfp.router)
app.include_router(searchcfo.router)
app.include_router(searchcfpcombine.router) 
app.include_router(searchcfpcombine_no_synonyms.router)
app.include_router(searchccombine_keyword_with_synnyms.router)
app.include_router(searchccombine_keyword_no_synonyms.router)
app.include_router(search_cloud.router)




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
    return {"message": "Welcome to Emission Factor Search"}
from fastapi import FastAPI
from api.routes import pipeline,results

app = FastAPI(title="Mulit-Omics Pipeline API")

app.include_router(pipeline.router)
app.include_router(results.router)
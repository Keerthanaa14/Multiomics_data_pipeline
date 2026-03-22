from fastapi import APIRouter
import pandas as pd
from pathlib import Path

router = APIRouter()

BASE = Path("data/gold")

@router.get("/pca/{omics}")
def get_pca(omics: str):
    file = BASE / omics / f"pca_{omics}.csv"

    if not file.exsists():
        return {"error": "File not found"}
    df = pd.read_csv(file)

    return df.head(100).to_dict(orient="records")

@router.get("/qc")
def get_qc():

    file = BASE / "qc_summary.csv"

    if not file.exsists():
        return {"error": "File not found"}
    
    df = pd.read_csv(file)

    return df.to_dict(orient="records")
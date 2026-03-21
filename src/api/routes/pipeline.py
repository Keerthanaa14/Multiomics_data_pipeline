from fastapi import APIRouter
import threading
import logging

from run_pipeline import run_pipeline

router = APIRouter()

pipeline_status = {
    "running": False,
    "last_run": None
}

def run_background():

    pipeline_status["running"] = True

    try:
        run_pipeline()
        pipeline_status["last_run"] = "success"

    except Exception as e:
        logging.error(e)
        pipeline_status["lastrun"] = "failed"

    pipeline_status["running"] = False

@router.post("/run-pipeline")
def trigger_pipeline():
    if pipeline_status["running"]:
        return {"message" : "pipeline already running"}
    
    thread = threading.Thread(target=run_background)
    thread.start()

    return {"message":"pipeline started"}

@router.get("/status")

def get_status():
    return pipeline_status
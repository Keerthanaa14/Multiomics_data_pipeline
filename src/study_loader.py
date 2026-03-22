import logging
from pathlib import Path

def load_available_studies(config=None):
    logging.info("Loading available studies...")
    studies = []

    #from config
    if config:
        cfg_studies = config.get("data.studies", [])
        if cfg_studies:
            logging.info(f"Loaded{len(cfg_studies)} studies from config")
            return cfg_studies
        
    #scan bronze layer
    base = Path("data/bronze")

    if not base.exists():
        logging.warning("Bronze data folder not found")
        return []
    
    for repo in ["geo", "pride"]:
        repo_path = base/repo
        if not repo_path.exists():
            continue
        for study_dir in repo_path.iterdir():

            if study_dir.is_dir():
                studies.append({
                    "study_id": study_dir.name,
                    "repository": repo
                })
    logging.info(f"Discovered {len(studies)} studies")

    return studies
import logging
import json
from pathlib import Path


def load_available_studies(config=None):

    logging.info("Loading available studies...")

    studies_by_repo = {"geo": [], "pride": []}

    # -------------------------
    # Load from config 
    # -------------------------
    if config:
        cfg_studies = config.get("data.studies", [])

        if cfg_studies:
            logging.info(f"Loaded {len(cfg_studies)} studies from config")

            # Ensure proper grouping
            for study in cfg_studies:

                repo = study.get("repository")

                if not repo:
                    # infer repo from study_id
                    sid = study.get("study_id", "").upper()

                    if sid.startswith("GSE"):
                        repo = "geo"
                    elif sid.startswith("PRIDE"):
                        repo = "pride"
                    else:
                        repo = "unknown"

                repo = repo.lower()

                studies_by_repo.setdefault(repo, []).append(study)

            return studies_by_repo

    # -------------------------
    # Scan bronze layer
    # -------------------------
    base = Path("data/bronze")

    if not base.exists():
        logging.warning("Bronze data folder not found")
        return studies_by_repo

    for repo in ["geo", "pride"]:

        repo_path = base / repo

        if not repo_path.exists():
            logging.warning(f"{repo} folder missing in bronze layer")
            continue

        for study_dir in repo_path.iterdir():

            if not study_dir.is_dir():
                continue

            meta_file = study_dir / "metadata.json"

            if not meta_file.exists():
                logging.warning(f"Missing metadata: {study_dir}")
                continue

            try:
                with open(meta_file, "r") as f:
                    metadata = json.load(f)

                # -------------------------
                # Ensure required fields
                # -------------------------
                metadata["study_id"] = metadata.get("study_id", study_dir.name)
                metadata["repository"] = repo  # enforce consistency

                # Optional defaults (prevents downstream crashes)
                metadata.setdefault("sample_size", None)
                metadata.setdefault("publication_year", None)
                metadata.setdefault("organism", "unknown")

                studies_by_repo[repo].append(metadata)

            except Exception as e:
                logging.error(f"Failed to read {meta_file}: {e}")

    # -------------------------
    # Final debug logs
    # -------------------------
    total = sum(len(v) for v in studies_by_repo.values())

    logging.info(f"Discovered {total} studies")

    for repo, studies in studies_by_repo.items():
        logging.info(f"{repo.upper()}: {len(studies)} studies → {[s['study_id'] for s in studies]}")

    return studies_by_repo
import os
import requests
import logging
from bs4 import BeautifulSoup

def list_files(url):
    try:
        res = requests.get(url, timeout=20)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, "html.parser")
        links = [a.get("href") for a in soup.find_all("a")]

        return [l for l in links if l and not l.startswith("?")]
    except Exception as e:
        logging.warning(f"Could not list {url}: {e}")
        return  []
    

def download_file(url, save_path):
    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()

            with open(save_path, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)

        logging.info(f"Downloaded: {save_path}")
        return save_path

    except Exception as e:
        logging.error(f"Failed: {url} | {e}")
        return None
    
def is_count_file(filename):
    name = filename.lower()

    if "count" not in name:
        return False
    
    valid_ext = (
        ".txt", ".tsv", ".csv",
        ".xls", ".xlsx",
        ".txt.gz", ".tsv.gz"
    )
    return name.endswith(valid_ext)

def download_geo_files(gse_id, bronze_root):

    prefix = gse_id[:-3] + "nnn"

    base = f"https://ftp.ncbi.nlm.nih.gov/geo/series/{prefix}/{gse_id}"
    study_dir = os.path.join(bronze_root, "geo", gse_id)

    results = {
        "matrix": None,
        "count_files": []
    }

    # series matrix file with metadata
    matrix_dir = f"{base}/matrix/"
    matrix_files = list_files(matrix_dir)
    
    for f in matrix_files:
        if "matrix" in f and f.endswith(".gz"):
            url = matrix_dir + f
            save_path = os.path.join(study_dir, f)

            results["matrix"] = download_file(url, save_path)
            break
    if not results["matrix"]:
        logging.warning(f"{gse_id} has no series matrix file")

    # Only download count files
    suppl_dir = f"{base}/suppl/"
    suppl_files = list_files(suppl_dir)

    for f in suppl_files:
        if is_count_file(f):
            url = suppl_dir + f
            save_path = os.path.join(study_dir, f)
            downloaded = download_file(url, save_path)

            if downloaded:
                results["count_files"].append(downloaded)
    
    return results
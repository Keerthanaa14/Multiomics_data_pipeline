import requests
import gzip
import pandas as pd
from pathlib import Path
import logging


def process_geo_expression(study_id):
    base_path = Path("data/bronze/geo") / study_id
    base_path.mkdir(parents=True, exist_ok=True)

    gz_file = base_path / f"{study_id}.txt.gz"
    csv_file = base_path / "expression.csv"

    if csv_file.exists():
        return str(csv_file)

    prefix = study_id[:-3] + "nnn"

    url = f"https://ftp.ncbi.nlm.nih.gov/geo/series/{prefix}/{study_id}/matrix/{study_id}_series_matrix.txt.gz"

    try:
        # Download
        r = requests.get(url, stream=True)
        if r.status_code != 200:
            logging.warning(f"No GEO matrix for {study_id}")
            return None

        with open(gz_file, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)

        # Parse
        with gzip.open(gz_file, "rt") as f:
            lines = f.readlines()

        start = next(i for i, l in enumerate(lines) if l.startswith("ID_REF"))

        from io import StringIO
        df = pd.read_csv(StringIO("".join(lines[start:])), sep="\t")

        df.to_csv(csv_file, index=False)

        gz_file.unlink()  # cleanup

        return str(csv_file)

    except Exception as e:
        logging.error(f"GEO parsing failed: {e}")
        return None
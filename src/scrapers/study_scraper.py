import requests
import logging
from urllib.parse import quote

from parsers.pride_parser import process_pride_expression
from scrapers.geo_downloader import download_geo_files


class StudyScraper:

    def __init__(self, config):
        self.config = config
        self.disease = self.config.get("filters.disease.name", "disease")

    # --------------------------------------------------
    # GEO HELPER: Resolve GSE accession
    # --------------------------------------------------
    def _get_gse_accession(self, base_url, gid):

        summary_url = (
            f"{base_url}esummary.fcgi?"
            f"db=gds&id={gid}&retmode=json"
        )

        try:
            res = requests.get(summary_url, timeout=20)
            res.raise_for_status()

            data = res.json()
            record = data.get("result", {}).get(str(gid), {})

            accession = record.get("accession")

            if accession and accession.startswith("GSE"):
                return accession

        except Exception as e:
            logging.error(f"Failed to resolve GSE for {gid}: {e}")

        return None

    # --------------------------------------------------
    # GEO SCRAPER
    # --------------------------------------------------
    def fetch_geo(self):

        if not self.config.get("repositories.geo.enabled", False):
            logging.info("GEO disabled")
            return []

        base_url = self.config.get("repositories.geo.api_endpoint")
        max_n = self.config.get("study_selection.per_repository.geo", 10)
        bronze_root = self.config.get("storage.bronze_path", "data/bronze")

        query = quote(self.disease)

        search_url = (
            f"{base_url}esearch.fcgi?"
            f"db=gds&term={query}+AND+gse[ETYP]&retmax={max_n}&retmode=json"
        )

        studies = []

        try:
            res = requests.get(search_url, timeout=20)
            res.raise_for_status()

            data = res.json()
            ids = data.get("esearchresult", {}).get("idlist", [])

            logging.info(f"GEO IDs fetched: {len(ids)}")

            if not ids:
                logging.warning("No GEO studies found")
                return []

            for gid in ids:

                # Step 1: Resolve GSE accession
                gse_id = self._get_gse_accession(base_url, gid)

                if not gse_id:
                    logging.warning(f"Skipping {gid} (no valid GSE accession)")
                    continue

                logging.info(f"Processing GEO {gse_id}")

                # Step 2: Download files
                files = download_geo_files(gse_id, bronze_root)

                matrix = files.get("matrix")
                count_files = files.get("count_files", [])

                # Step 3: Relaxed filtering (IMPORTANT)
                if not matrix and not count_files:
                    logging.warning(f"Skipping {gse_id} (no usable files)")
                    continue

                metadata = {
                    "study_id": gse_id,
                    "repository": "geo",
                    "disease_name": self.disease,
                    "files": {
                        "matrix": matrix,
                        "count_files": count_files
                    }
                }

                studies.append(metadata)

            logging.info(f"GEO processed {len(studies)} studies")
            return studies

        except Exception as e:
            logging.error(f"GEO error: {e}")
            return []

    # --------------------------------------------------
    # PRIDE SCRAPER
    # --------------------------------------------------
    def fetch_pride(self):

        if not self.config.get("repositories.pride.enabled", False):
            logging.info("PRIDE disabled")
            return []

        base_url = self.config.get("repositories.pride.api_endpoint")
        max_n = self.config.get("study_selection.per_repository.pride", 1)

        url = f"{base_url}projects?keyword={quote(self.disease)}&pageSize={max_n}"

        studies = []

        try:
            res = requests.get(url, timeout=20)
            res.raise_for_status()

            data = res.json()
            projects = data.get("_embedded", {}).get("projects", [])

            if not projects:
                logging.warning("No PRIDE studies found")
                return []

            for p in projects:

                pid = p.get("accession")

                if not pid:
                    continue

                logging.info(f"Processing PRIDE {pid}")

                expression_path = process_pride_expression(pid)

                if not expression_path:
                    logging.warning(f"Skipping {pid} (no expression data)")
                    continue

                metadata = {
                    "study_id": pid,
                    "repository": "pride",
                    "disease_name": self.disease,
                    "expression_file": expression_path
                }

                studies.append(metadata)

            logging.info(f"PRIDE processed {len(studies)} studies")
            return studies

        except Exception as e:
            logging.error(f"PRIDE error: {e}")
            return []

    # --------------------------------------------------
    # MAIN ENTRY
    # --------------------------------------------------
    def fetch_all(self):

        logging.info(f"Scraping studies for: {self.disease}")

        return {
            "geo": self.fetch_geo(),
            "pride": self.fetch_pride()
        }
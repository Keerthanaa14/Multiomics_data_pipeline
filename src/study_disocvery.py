import logging

class StudyDiscovery:
    def __init__(self, config_loader):
        """
        Initialize with an instance of Config loader
        """
        self.config = config_loader
        self.filters = self.config.get("filters", {})
        self.study_selection = self.config.get("study_selection", {})



    def filter_studies(self, studies, repository_name):
        
        filtered = []
        repo_config = self.config.get(f"repositories.{repository_name}", {})

        for study in studies:

            study_id = study.get("study_id", "UNKNOWN")
            logging.info(f"\n🔍 Checking study: {study_id}")

            # DISEASE FILTER
            disease_name = study.get('disease_name', '').lower()
            disease_cfg = self.filters.get("disease", {})

            if disease_cfg.get('ontology_id'):
                study_id_val = study.get('disease_ontology_id', '').strip().lower()
                config_id_val = disease_cfg['ontology_id'].strip().lower()

            if study_id_val != config_id_val:
                logging.warning(f"[FAIL][{study_id}] ontology mismatch: {study_id_val}")
                continue

            valid_terms = []

            name = disease_cfg.get('name')
            if name:
                valid_terms.append(name.lower())

            valid_terms.extend([s.lower() for s in disease_cfg.get('synonyms', [])])

            if valid_terms:
                if not any(term in disease_name for term in valid_terms):
                    logging.warning(f"[FAIL][{study_id}] disease mismatch: {disease_name}")
                    continue

            # PUBLICATION YEAR
            pub_cfg = self.filters.get("publication_year", {})
            year = study.get('publication_year')

            if pub_cfg.get('min') and year is not None and year < pub_cfg['min']:
                logging.warning(f"[FAIL][{study_id}] year too old: {year}")
                continue

            if pub_cfg.get('max') and year is not None and year > pub_cfg['max']:
                logging.warning(f"[FAIL][{study_id}] year too new: {year}")
                continue

            # TISSUE FILTER
            tissue_cfg = self.filters.get("tissue", {})
            tissue = study.get('tissue_type', '').lower()

            include_tissue = [t.lower() for t in (tissue_cfg.get('include') or [])]
            exclude_tissue = [t.lower() for t in (tissue_cfg.get('exclude') or [])]

            if include_tissue and tissue not in include_tissue:
                logging.warning(f"[FAIL][{study_id}] tissue mismatch: {tissue} not in {include_tissue}")
                continue

            if exclude_tissue and tissue in exclude_tissue:
                logging.warning(f"[FAIL][{study_id}] tissue excluded: {tissue}")
                continue

            # CELL TYPE
            cell_cfg = self.filters.get("cell_type", {})
            cell = study.get('cell_type', '').lower()

            include_cell = [c.lower() for c in (cell_cfg.get('include') or [])]
            exclude_cell = [c.lower() for c in (cell_cfg.get('exclude') or [])]

            if include_cell and cell not in include_cell:
                logging.warning(f"[FAIL][{study_id}] cell type mismatch: {cell}")
                continue

            if exclude_cell and cell in exclude_cell:
                logging.warning(f"[FAIL][{study_id}] cell excluded: {cell}")
                continue

            # ORGANISM
            org_cfg = self.filters.get("organism", {})
            include_org = org_cfg.get('include', [])

            if include_org and study.get('organism') not in include_org:
                logging.warning(f"[FAIL][{study_id}] organism mismatch: {study.get('organism')}")
                continue
            # SAMPLE SIZE
            min_samples = repo_config.get('min_sample_size')
            max_samples = repo_config.get('max_sample_size')
            sample_size = study.get('sample_size')

            if sample_size is not None:
                if min_samples and sample_size < min_samples:
                    logging.warning(f"[FAIL][{study_id}] sample too small: {sample_size}")
                    continue

                if max_samples and sample_size > max_samples:
                    logging.warning(f"[FAIL][{study_id}] sample too large: {sample_size}")
                    continue
            # PASSED
            logging.info(f"[PASS][{study_id}] ✅")
            filtered.append(study)

        return filtered

    def select_studies(self, studies, repository_name):
        """
        Select studies based on config; and per repo limits.
        """
        per_repo_limit = self.study_selection.get(f"study_selection.per_repository.{repository_name}", len(studies))
        strategy = self.study_selection.get('selection_strategy', 'most_recent')

        if strategy == 'most_recent':
            # Sort studies by publication date and return the most recent ones
            sorted_studies = sorted(studies, key=lambda x: x.get('publication_year', 0), reverse=True)
            return sorted_studies[:per_repo_limit]
        if strategy == 'largest_sample_size':
            # Sort studies by sample size and return the largest ones
            sorted_studies = sorted(studies, key=lambda x: x.get('sample_size', 0), reverse=True)
            return sorted_studies[:per_repo_limit]
        else:
            studies_sorted = studies  # fallback

        return studies_sorted[:per_repo_limit]

    def discover(self, studies_by_repo):
        """
        Discover studies across repositories by applying filters and selection criteria.
        """
        discovered = {}
        for repo, studies in studies_by_repo.items():
            filtered = self.filter_studies(studies, repo)
            selected = self.select_studies(filtered, repo)
            discovered[repo] = selected
            logging.info(f"{repo}: {len(selected)} studies discovered from {len(studies)} available.")
        return discovered

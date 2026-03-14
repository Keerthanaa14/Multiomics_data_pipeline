import logging

class StudyDiscovery:
    def __init__(self, config_loader):
        """
        Initialize with an instance of Config loader
        """
        self.config = config_loader
        self.filters = self.config.get("filters", {})
        self.study_selection = self.config.get("study_selection", {})
        self.repositories = self.config.get("repositories", [])


    def filter_studies(self, studies, repository_name):
        """
        Filter studies based on config; all filters are optional.
        """
        filtered = []
        repo_config = self.filters.get(repository_name, {})

        for study in studies:
            # disease filters
            disease_cfg = self.filters.get("disease", {})
            if disease_cfg.get('ontology_id') and study.get('disease_ontology_id') != disease_cfg['ontology_id']:
                continue
            if disease_cfg.get('name) and disease_cfg['name'].lower() not in study.get('disease_name', '').lower():
                continue
        
            # publication year filters
            pub_cfg = self.filters.get("publication_year", {})
            year = study.get('publication_year')
            if pub_cfg.get('min') and year is not None and year < pub_cfg['min']:
                continue
            if pub_cfg.get('max') and year is not None and year > pub_cfg['max']:
                continue
                
            # Tissue filters
            tissue_cfg = self.filters.get("tissue", {})
            tissue =study.get('tissue_type', '').lower()
            include_tissue = [t.lower() for t in tissue_cfg.get('include', [])]
            exclude_tissue = [t.lower() for t in tissue_cfg.get('exclude', [])]
            if include_tissue and tissue not in include_tissue:
                continue
            if exclude_tissue and tissue in exclude_tissue:
                continue

            # Cell type filters
            cell_cfg = self.filters.get("cell_type", {})
            cell = study.get('cell_type', '').lower()
            include_cell = [c.lower() for c in cell_cfg.get('include', [])]
            exclude_cell = [c.lower() for c in cell_cfg.get('exclude', [])]
            if include_cell and cell not in include_cell:
                continue
            if exclude_cell and cell in exclude_cell:
                continue
            
            #organism filters
            org_cfg = self.filters.get("organism", {})
            include_org = org_cfg.get('include', [])
            if include_org and study.get('organism') not in include_org:
                continue
                
            #sample size filters
            min_samples = repo_config.get('min_samples_size')
            max_samples = repo_config.get('max_samples_size')
            sample_size = study.get('sample_size')
            if min_samples and sample_size < min_samples:
                continue
            if max_samples and sample_size > max_samples:
                continue

            filtered.append(study)  
        return filtered

    def select_studies(self, studies, repository_name):
        """
        Select studies based on config; and per repo limits.
        """
        per_repo_limit = self.study_selection.get('per_repository', {}).get(repository_name, len(studies))
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

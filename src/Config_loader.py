import yaml
from pathlib import Path
import logging
class ConfigLoader:
    def __init__(self, config_path, environment=None):
        """Load YAML configuration.
        All settings are optional. Missing field return none.
        Environment-specific overrides are applied if given
        """
        self.config_path = Path(config_path)
        self.environment = environment
        self.config = self.load_config()
        if self.environment:
            self.apply_environment_overrides()

    def load_config(self):
        """Load the YAML configuration file. Return empty dict if missing"""
        if not self.config_path.exists():
            logging.warning(f"Config file not found: {self.config_path}") 
            return {}
        with open(self.config_path, 'r') as file:
            config = yaml.safe_load(file) or {}
            return config

    def apply_environment_overrides(self):
        """apply environment- specific overides if present."""
        environments = self.config.get("environments", {})
        env_config = environments.get(self.environment)
        if env_config:
            self.deep_update(self.config, env_config)

    def deep_update(self, original, updates):
        """Recursively update the original dictionary with values from updates."""
        for key, value in updates.items():
            if isinstance(value, dict) and isinstance(original.get(key), dict):
                self.deep_update(original[key], value)
            else:
                original[key] = value
    
    def get(self, path, default=None):
        """Access config values using dot notation.
        Return nothing if missing
        Example: config.get('filters.disease.name') -> "Alzheimer's disease"
        """
        keys = path.split('.')
        value = self.config
        for key in keys:
            if not isinstance(value, dict):
                return default
            value = value.get(key)
            if value is None:
                return default
        return value
    
    def show(self):
        """Print the entire configuration for debugging."""
        print(yaml.dump(self.config, default_flow_style=False))

    def get_pipeline_steps(self):
        """Return the list of pipeline steps to execute."""
        return self.get('pipeline_steps', [])

    def get_required_metadata_fields(self):
        """Return a list of required metadata fields."""
        return self.config.get('required_metadata_fields', [])

    def get_data_integrity_checks(self):
        """Return a dictionary of data integrity checks and their settings."""
        return {
            'check_duplicates': self.config.get('validation.check_duplicates', False),
            'check_data_types': self.config.get('validation.check_data_types', False),
            'validate_expression_ranges': self.get('validation.validate_expression_ranges', False)
        }
    def validate_required_fields(self, metadata):
        """Raise an error if any required metadata fields are missing."""
        missing = []
        for path in required_paths:
            if self.get(path) is None:
                missing.append(path)
        if missing:
            raise ValueError(f"Missing required config fields: {', '.join(missing)}")
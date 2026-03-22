import logging
from logging import config
from pathlib import Path

def write_delta_table(data, config):

    logging.info("Writing bronze layer with lineage...")
    base_path = Path("data/bronze/delta_table")
    compression = config.get("output.compression", "snappy")

    for _, dataset in data.items():
        metadata = dataset["metadata"]
        expression = dataset["expression"]

        repo = metadata["repository"].iloc[0]
        study_id = metadata["study_id"].iloc[0]

        path = base_path / repo / study_id
        path.mkdir(parents=True, exist_ok=True)

        metadata.to_parquet(path / "metadata.parquet", compression=compression, index=False)
        expression.to_parquet(path / "expression.parquet", compression=compression, index=False)

        logging.info(f"Written {repo}/{study_id} to {path} with compression={compression}")

    return True
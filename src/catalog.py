import pandas as pd
from pathlib import Path

def build_catalog(data):
    entries = []

    for name, dataset in data.items():
        meta = dataset["metadata"]
        expr = dataset["expression"]

        entry={
            "dataset": name,
            "repository": meta["repository"].iloc[0],
            "study_id": meta["study_id"].iloc[0] if "study_id" in meta else name,
            "samples": len(meta),
            "features": expr.shape[1],
            "feature_id_type": meta["feature_id_type"].iloc[0] if "feature_id_type" in meta else "unknown",
            "feature_id_standard": meta["feature_id_standard"].iloc[0] if "feature_id_standard" in meta else "unknown",
            "feature_mapping": meta["feature_mapping"].iloc[0] if "feature_mapping" in meta else "unknown",

        }

        entries.append(entry)

    df = pd.DataFrame(entries)

    out_path = Path("data/gold")
    out_path.mkdir(parents=True, exist_ok=True)

    df.to_csv(out_path / "catalog.csv", index=False)

    return df
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

def run_pvca(data, params):

    all_expr = []
    batch_labels = []
    condition_labels = []
    study_labels = []

    for name, dataset in data.items():

        expr = dataset["expression"]
        meta = dataset["metadata"]

        all_expr.append(expr)

        batch_labels.extend(meta["batch"].tolist())
        condition_labels.extend(meta["condition"].tolist())
        study_labels.extend(meta["study"].tolist())

    combined = pd.concat(all_expr, axis=0)

    n = params.get("n_components", 10)

    pca = PCA(n_components=n)
    pcs = pca.fit_transform(combined)

    df = pd.DataFrame(pcs, columns=[f"PC{i+1}" for i in range (n)])
    df["batch"] = batch_labels
    df["condition"] = condition_labels
    df["study"] = study_labels

    batch_var, condition_var, study_var = [], [], []

    for i in range(n):
        pc = f"PC{i+1}"
        var_total = np.var(df[pc])

        batch_var.append(np.var(df.groupby("batch")[pc].mean())/ (var_total + 1e-6))
        condition_var.append(np.var(df.groupby("condition")[pc].mean())/ (var_total + 1e-6))
        study_var.append(np.var(df.groupby("study")[pc].mean())/ (var_total + 1e-6))

    return {
        "mean_batch_variance": float(np.mean(batch_var)),
        "mean_condition_variance": float(np.mean(condition_var)),
        "mean_study_variance": float(np.mean(study_var))
    }


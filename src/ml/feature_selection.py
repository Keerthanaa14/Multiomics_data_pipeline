from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import logging

def run_feature_selection(data):

    results = {}

    for name, dataset in data.items():
        X = dataset["expression"]
        Y = dataset["metadata"]["condition"]

        # removing unknown labels
        Y = Y.reindex(X.index)
        valid_idx = (Y != "unknown") & (Y.notna())
        X = X.loc[valid_idx]
        Y = Y.loc[valid_idx]
        if len(Y) == 0:
            logging.warning(f"{name}: no valid samples")
            continue
        if len(set(Y)) < 2:
            continue

        model = RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            class_weight="balanced"
        )

        model.fit(X, Y)

        importance = pd.Series(
            model.feature_importances_,
            index=X.columns
        ).sort_values(ascending=False)

        results[name] = importance
    return results

#aggreate data per omics
def aggregate_feature_importance(results):
    if not results:
        return None
    dfs = []
    names = []
    for name, series in results.items():
        if series is None or len(series) == 0:
            continue

        dfs.append(series)
        names.append(name)

    if len(dfs) == 0:
        return None
    df = pd.concat(dfs, axis=1)
    df.columns = names

    df["mean_importance"] = df.mean(axis=1, skipna=True)
    df = df.fillna(0)

    return df.sort_values("mean_importance", ascending=False)
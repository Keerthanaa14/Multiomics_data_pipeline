from sklearn.ensemble import RandomForestClassifier
import pandas as pd

def run_feature_selection(data):

    results = {}

    for name, dataset in data.items():
        X = dataset["expression"]
        Y = dataset["metadata"]["condition"]

        # removing unknown labels
        valid_idx = Y != "unknown"
        X = X[valid_idx]
        Y = Y[valid_idx]

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
    
    df = pd.concat(results.values(), axis =1)
    df.columns = results.keys()

    df["mean_importance"] = df.mean(axis=1)

    return df.sort_values("mean_importance", ascending=False)
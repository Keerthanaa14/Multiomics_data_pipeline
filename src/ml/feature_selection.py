import logging
from typing import Dict, Any, Optional

import pandas as pd
from sklearn.ensemble import RandomForestClassifier


# --------------------------------------------------
# Helper: Standardize index
# --------------------------------------------------
def _standardize_index(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.index = df.index.astype(str).str.strip()
    return df


# --------------------------------------------------
# Helper: Prepare metadata index
# --------------------------------------------------
def _prepare_metadata(meta: pd.DataFrame) -> pd.DataFrame:
    meta = meta.copy()

    if "sample_id" in meta.columns:
        meta["sample_id"] = meta["sample_id"].astype(str).str.strip()
        meta = meta.set_index("sample_id")
    else:
        meta.index = meta.index.astype(str).str.strip()

    return meta


# --------------------------------------------------
# Helper: Align expression + metadata safely
# --------------------------------------------------
def _align_data(
    X: pd.DataFrame,
    meta: pd.DataFrame,
    dataset_name: str
):
    # Remove duplicates
    X = X[~X.index.duplicated(keep="first")]
    meta = meta[~meta.index.duplicated(keep="first")]

    # Find overlap
    common = X.index.intersection(meta.index)

    if len(common) == 0:
        logging.warning(f"{dataset_name}: no overlapping samples → skipping")
        return None, None

    # Enforce identical order
    X = X.loc[common].sort_index()
    meta = meta.loc[common].sort_index()

    if not X.index.equals(meta.index):
        logging.error(f"{dataset_name}: alignment failed after sorting")
        return None, None

    return X, meta


# --------------------------------------------------
# Main: Feature Selection
# --------------------------------------------------
def run_feature_selection(data: Dict[str, Any]) -> Dict[str, pd.Series]:
    """
    Runs RandomForest-based feature selection on multiple datasets.

    Parameters
    ----------
    data : dict
        {
            dataset_name: {
                "expression": pd.DataFrame,
                "metadata": pd.DataFrame
            }
        }

    Returns
    -------
    dict
        {dataset_name: feature_importance_series}
    """

    results = {}

    for name, dataset in data.items():
        logging.info(f"{name}: starting feature selection")

        try:
            # -----------------------------
            # Load data
            # -----------------------------
            X = dataset["expression"].copy()
            meta = dataset["metadata"].copy()

            # -----------------------------
            # Standardize indices
            # -----------------------------
            X = _standardize_index(X)
            meta = _prepare_metadata(meta)

            # -----------------------------
            # Align datasets
            # -----------------------------
            X, meta = _align_data(X, meta, name)

            if X is None:
                continue

            # -----------------------------
            # Extract labels
            # -----------------------------
            if "condition" not in meta.columns:
                logging.warning(f"{name}: 'condition' column missing → skipping")
                continue

            Y = meta["condition"]

            # -----------------------------
            # Clean labels
            # -----------------------------
            valid_idx = (Y.notna()) & (Y != "unknown")

            X = X.loc[valid_idx]
            Y = Y.loc[valid_idx]

            # -----------------------------
            # Validation
            # -----------------------------
            if len(Y) == 0:
                logging.warning(f"{name}: no valid samples after filtering")
                continue

            if Y.nunique() < 2:
                logging.warning(f"{name}: only one class → skipping")
                continue

            logging.info(
                f"{name}: aligned samples={len(X)}, features={X.shape[1]}"
            )

            # -----------------------------
            # Model
            # -----------------------------
            model = RandomForestClassifier(
                n_estimators=200,
                random_state=42,
                class_weight="balanced",
                n_jobs=-1
            )

            model.fit(X, Y)

            # -----------------------------
            # Feature importance
            # -----------------------------
            importance = pd.Series(
                model.feature_importances_,
                index=X.columns,
                name=name
            ).sort_values(ascending=False)

            results[name] = importance

            logging.info(
                f"{name}: feature selection complete"
            )

        except Exception as e:
            logging.exception(f"{name}: failed with error: {e}")

    return results


# --------------------------------------------------
# Aggregate Feature Importance Across Studies
# --------------------------------------------------
def aggregate_feature_importance(
    results: Dict[str, pd.Series]
) -> Optional[pd.DataFrame]:
    """
    Aggregates feature importance across datasets.

    Returns
    -------
    pd.DataFrame with mean importance
    """

    if not results:
        logging.warning("No results to aggregate")
        return None

    valid_series = []
    names = []

    for name, series in results.items():
        if series is None or len(series) == 0:
            continue
        valid_series.append(series)
        names.append(name)

    if not valid_series:
        logging.warning("All result series are empty")
        return None

    df = pd.concat(valid_series, axis=1)
    df.columns = names

    # Fill missing features with 0 importance
    df = df.fillna(0)

    # Mean importance across datasets
    df["mean_importance"] = df.mean(axis=1)

    df = df.sort_values("mean_importance", ascending=False)

    logging.info(
        f"Aggregation complete: {len(df)} total features"
    )

    return df


# --------------------------------------------------
# Optional: Get Top Features
# --------------------------------------------------
def get_top_features(
    aggregated_df: pd.DataFrame,
    top_n: int = 50
) -> pd.DataFrame:
    """
    Returns top N important features.
    """

    if aggregated_df is None or aggregated_df.empty:
        return pd.DataFrame()

    return aggregated_df.head(top_n)
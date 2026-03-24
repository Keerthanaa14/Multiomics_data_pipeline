import logging
from pathlib import Path
import pandas as pd
import plotly.express as px
import webbrowser


# -----------------------------------
#  SAFE PCA EXTRACTOR
# -----------------------------------
def extract_pca_df(result, key):

    pca = result.get(key)

    if pca is None:
        return pd.DataFrame()

    # Case 1: already dataframe
    if isinstance(pca, pd.DataFrame):
        return pca

    # Case 2: dict with pca_table
    if isinstance(pca, dict) and "pca_table" in pca:
        return pd.DataFrame(pca["pca_table"])

    # Case 3: dict with coords
    if isinstance(pca, dict) and "coords" in pca:
        return pd.DataFrame(pca["coords"])

    return pd.DataFrame()


def extract_variance(result, key):

    # new format
    if key in result and isinstance(result[key], dict):
        return result[key].get("variance")

    # old format
    if key == "pca_before":
        return result.get("pca_variance_before")

    if key == "pca_after":
        return result.get("pca_variance_after")

    return None


# -----------------------------------
#  SUMMARY
# -----------------------------------
def compute_summary(data, batch_results):

    total_samples = 0
    total_features = 0

    for dataset in data.values():
        total_samples += len(dataset["metadata"])
        total_features += dataset["expression"].shape[1]

    pc1_var = "N/A"

    try:
        first = list(batch_results.values())[0]
        var = extract_variance(first, "pca_before")

        if var:
            pc1_var = round(var[0], 4)

    except:
        pass

    return {
        "datasets": len(data),
        "samples": total_samples,
        "features": int(total_features / len(data)) if data else 0,
        "pc1": pc1_var
    }


# -----------------------------------
#  PCA INTERACTIVE
# -----------------------------------
def render_pca(batch_results):

    html = "<h2> PCA Analysis</h2>"

    for group, result in batch_results.items():

        before_df = extract_pca_df(result, "pca_before")
        after_df = extract_pca_df(result, "pca_after")

        if before_df.empty:
            html += f"<p>{group}: No PCA data</p>"
            continue

        # Ensure columns exist
        for col in ["PC1", "PC2"]:
            if col not in before_df.columns:
                before_df.columns = [f"PC{i+1}" for i in range(before_df.shape[1])]

        fig_before = px.scatter(
            before_df,
            x="PC1",
            y="PC2",
            color=before_df["condition"] if "condition" in before_df else None,
            symbol=before_df["batch"] if "batch" in before_df else None,
            hover_data=before_df.columns,
            title=f"{group} - PCA Before"
        )

        html += fig_before.to_html(full_html=False, include_plotlyjs="cdn")

        if not after_df.empty:

            if "PC1" not in after_df.columns:
                after_df.columns = [f"PC{i+1}" for i in range(after_df.shape[1])]

            fig_after = px.scatter(
                after_df,
                x="PC1",
                y="PC2",
                color=after_df["condition"] if "condition" in after_df else None,
                symbol=after_df["batch"] if "batch" in after_df else None,
                hover_data=after_df.columns,
                title=f"{group} - PCA After"
            )

            html += fig_after.to_html(full_html=False, include_plotlyjs=False)

    return html


# -----------------------------------
# FEATURE IMPORTANCE
# -----------------------------------
def render_features(feature_results):

    html = "<h2>Feature Importance</h2>"

    for group, df in feature_results.items():

        if isinstance(df, pd.DataFrame) and not df.empty:

            if "importance" not in df.columns:
                continue

            top = df.sort_values("importance", ascending=False).head(20)

            fig = px.bar(
                top,
                x="importance",
                y=top.columns[0],
                orientation="h",
                title=f"{group} Top Features"
            )

            html += fig.to_html(full_html=False, include_plotlyjs=False)

    return html


# -----------------------------------
# QC TABLE
# -----------------------------------
def render_qc(qc_results):

    df = pd.DataFrame(qc_results).T

    return f"""
    <h2>QC Summary</h2>
    {df.to_html()}
    """


# -----------------------------------
#  MAIN DASHBOARD
# -----------------------------------
def export_dashboard(data, qc_results, batch_results, feature_results):

    logging.info("Creating robust interactive dashboard...")

    base = Path("dashboard")
    base.mkdir(exist_ok=True)

    summary = compute_summary(data, batch_results)

    html = f"""
    <html>
    <head>
        <title>Multi-Omics Dashboard</title>
        <style>
            body {{ font-family: Arial; margin: 40px; }}
        </style>
    </head>

    <body>

    <h1>Multi-Omics Pipeline Dashboard</h1>

    <h2> Summary</h2>
    <p>Datasets: {summary['datasets']}</p>
    <p>Samples: {summary['samples']}</p>
    <p>Avg Features: {summary['features']}</p>
    <p>PC1 Variance: {summary['pc1']}</p>

    {render_qc(qc_results)}

    {render_pca(batch_results)}

    {render_features(feature_results)}

    </body>
    </html>
    """

    path = base / "dashboard.html"

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    logging.info(f"Dashboard saved: {path}")

    webbrowser.open(path.resolve().as_uri())

    return path
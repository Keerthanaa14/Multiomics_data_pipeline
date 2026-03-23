import pandas as pd
import gzip
from pathlib import Path
import logging


def read_gene_counts(file_path):

    # handle gz or txt
    if str(file_path).endswith(".gz"):
        f = gzip.open(file_path, "rt")
    else:
        f = open(file_path, "r")

    df = pd.read_csv(f, sep="\t")

    f.close()

    # standardize columns
    df.columns = [c.lower() for c in df.columns]

    # try common formats
    if "geneid" in df.columns:
        gene_col = "geneid"
    elif "gene_id" in df.columns:
        gene_col = "gene_id"
    else:
        raise ValueError("Gene ID column not found")

    if "counts" in df.columns:
        count_col = "counts"
    else:
        count_col = df.columns[-1]

    df = df[[gene_col, count_col]]
    df.columns = ["gene_id", "counts"]

    return df


def build_expression_matrix(folder_path):

    logging.info(f"Building expression matrix from {folder_path}")

    folder = Path(folder_path)

    files = list(folder.glob("*geneCounts*.txt*"))

    if not files:
        raise ValueError("No geneCounts files found")

    matrix = None

    for file in files:

        sample_name = file.name.split("_geneCounts")[0]

        df = read_gene_counts(file)

        df = df.set_index("gene_id")
        df.columns = [sample_name]

        if matrix is None:
            matrix = df
        else:
            matrix = matrix.join(df, how="outer")

    matrix = matrix.fillna(0)

    # transpose → samples as rows (your pipeline format)
    matrix = matrix.T

    logging.info(f"Matrix shape: {matrix.shape}")

    return matrix
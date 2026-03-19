import logging
import numpy as np

def run_zscore(df):
    return df.apply(lambda x: (x - np.mean(x)) / np.std(x) + 1e-6)

def run_quantile(df):
    ranked = df.stack().groupby(df.rank(method='first').stack().astype(int)).mean()
    return df.rank(method='min').stack().astype(int).map(ranked).unstack()

def run_median(df):
    return df - df.median()

def run_tpm(df):
    return df.div(df.sum(axis=0), axis=1) * 1e6

def run_fpkm(df):
    logging.warning("FPKM normalization is not implemented yet. Returning input dataframe.Gene lengths are needed for FPKM calculation, which are not currently available in the metadata. Consider using TPM or another method instead.")
    return df
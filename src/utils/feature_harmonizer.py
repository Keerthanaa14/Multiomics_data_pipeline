import logging
import pandas as pd

# R biomaRt mapping 

def map_ensembl_to_symbol_biomart(df):

    import rpy2.robjects as ro
    from rpy2.robjects import pandas2ri

    pandas2ri.activate()

    ro.r('''
         supressMessages(library(biomaRt))
         map_ids <- function(ids) {
            mart <- useEnsembl(
                biomart = "genes",
                dataset = "hsapiens_gene_ensembl"
         )
         res <- getBM(
            attributes = c("ensembl_gene_id", "hgnc_symbol"),
            filters = "ensembl_gene_id",
            values = ids,
            mart = mart
         )
         
         return(res)
         }
         ''')
    
    r_map = ro.globalenv["map_ids"]

    clean_ids = [x.split(".")[0] for x in df.columns]
    mapping_df =pd.DataFrame(r_map(clean_ids))

    mapping = dict(zip(
        mapping_df["ensembl_gene_id"],
        mapping_df["hgnc_symbol"]
    ))

    new_cols = []

    for col in clean_ids:
        symbol = mapping.get(col)
        new_cols.append(symbol if symbol else col)

    df.columns = new_cols

    #remove duplicates
    
    df = df.groupby(df.columns, axis=1).mean()

    return df

def harmonize_feature_ids(data,config):
    logging.info("Harmonizing feature IDs...")

    for name, dataset in data.items():
        df = dataset["expression"]
        meta = dataset["metadata"]

        repo = meta["repository"].iloc[0]

    #RNA ID mapping
    if repo == "geo":
        if any(col.startswith("ENSG") for col in df.columns [:50]):

            logging.info(f"{name}: Ensembl detected and mapping via biomaRT")

            df = map_ensembl_to_symbol_biomart(df)

    # proteomics ID cleaning
    elif repo == "pride":
        
        logging.info(f"{name}: clenaing Uniprot IDs")

        df.columns = df.columns.str.split(";").str[0]
        df.columns = df.columns.str.split("-").str[0]
        df.columns = df.columns.str.strip()

        meta["feature_ID_type"] = "protein_group"
        meta["feature_id_standard"] = "uniprot"
        meta["feature_mapping"] = "string_cleaning"

    meta["feature_count"] = df.shape[1]

    dataset["expression"] = df
    dataset["metadata"] = meta

    return data

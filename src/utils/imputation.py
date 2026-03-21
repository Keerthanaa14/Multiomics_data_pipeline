import logging
def impute_missing_values(data, config):
    logging.info("impute missing values for proteomics data...")

    for name, dataset in data.items():

        df = dataset["expression"]
        repo = dataset["metadata"]["repository"].iloc[0]

        if repo != "pride":
            continue

        missing_rate = df.isnull().mean().mean()
        logging.info(f"{name}: missinf rate = {missing_rate:.3f}")

        df = df.apply(lambda x: x.fillna(x.median()), axis=0)

        dataset["expression"] =df

    return data
import logging
def align_features(data):
    logging.info("Aligning features across datasets...")

    feature_sets = []

    for name, ds in data.items():
        cols = set(ds["expression"].columns)
        logging.info(f"{name}:{len(cols)} features")
        feature_sets.append(cols)

    common_features = set.intersection(*feature_sets)

    if len(common_features) == 0:
        raise ValueError("No common features across datasets")
    
    if len(common_features) < 500:
        logging.warning("Low feature overlap -PCA may be unreliable")

    logging.info(f"common features restained: {len(common_features)}")

    for name in data:
        data[name]["expression"] = data[name]["expression"][list(common_features)]

    return data
def split_by_omics(data):
    groups = {
        "rna": {},
        "proteomics": {}
    }

    for name, dataset in data.items():
        repo = dataset["metadata"] ["repository"].iloc[0]

        if repo == "geo":
            groups["rna"][name] = dataset
        
        elif repo == "pride":
            groups["proteomics"] [name] = dataset

    return groups
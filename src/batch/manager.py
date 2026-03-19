import logging
from .methods import apply_batch_method

def detect_batch_effect(data,config):

    logging.info("Detecting batch effects...")
    cfg= config["methods"]["batch_detection"]

    primary = cfg["primary_method"]
    secondary = cfg.get("secondary_method")
    params = cfg.get("parameters", {})

    results = {}

    #Run primary method
    results["primary"] = apply_batch_method(data, primary, params)

    if secondary:
        results[secondary] = apply_batch_method(data, secondary, params)
    
    return results
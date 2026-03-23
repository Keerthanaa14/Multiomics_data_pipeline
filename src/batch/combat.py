import pandas as pd
import logging


def run_combat(df, metadata):

    logging.info("Running ComBat batch correction...")
    if metadata["batch"].nunique() < 2:
        logging.warning("Only one batch → skipping ComBat")
        return df

    if metadata["condition"].nunique() < 2:
        logging.warning("Only one condition → skipping ComBat")
        return df

    try:
        import rpy2.robjects as ro
        from rpy2.robjects import pandas2ri
        from rpy2.robjects.conversion import localconverter

    except Exception as e:
        logging.warning(f"rpy2 import failed: {e}")
        return df  # fallback safely

    try:
        # --------------------------------------------------
        # Ensure required columns
        # --------------------------------------------------
        if "batch" not in metadata.columns:
            raise ValueError("metadata missing 'batch' column")

        if "condition" not in metadata.columns:
            logging.warning("metadata missing 'condition' → using intercept only")
            metadata["condition"] = "A"

        # Convert to string (important for R factors)
        metadata["batch"] = metadata["batch"].astype(str)
        metadata["condition"] = metadata["condition"].astype(str)

        # --------------------------------------------------
        # Define R function
        # --------------------------------------------------
        ro.r('''
            suppressMessages(library(sva))

            run_combat <- function(expr, batch, condition) {

                batch <- as.factor(batch)
                condition <- as.factor(condition)

                mod <- model.matrix(~ condition)

                corrected <- ComBat(
                    dat = as.matrix(expr),
                    batch = batch,
                    mod = mod,
                    par.prior = TRUE,
                    prior.plots = FALSE
                )

                return(as.data.frame(corrected))
            }
        ''')

        r_func = ro.globalenv["run_combat"]

        # --------------------------------------------------
        # Proper conversion (modern rpy2)
        # --------------------------------------------------
        with localconverter(ro.default_converter + pandas2ri.converter):
            expr_r = ro.conversion.py2rpy(df)
            batch_r = ro.conversion.py2rpy(metadata["batch"])
            condition_r = ro.conversion.py2rpy(metadata["condition"])

        # Run ComBat
        corrected_r = r_func(expr_r, batch_r, condition_r)

        # Convert back to pandas
        with localconverter(ro.default_converter + pandas2ri.converter):
            corrected = ro.conversion.rpy2py(corrected_r)

        # --------------------------------------------------
        # Restore structure
        # --------------------------------------------------
        corrected = pd.DataFrame(corrected)
        corrected.columns = df.columns
        corrected.index = df.index

        return corrected

    except Exception as e:
        logging.warning(f"ComBat failed: {e}")
        logging.warning("Falling back → returning original data")
        return df
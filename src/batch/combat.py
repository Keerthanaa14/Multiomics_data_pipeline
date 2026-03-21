import pandas as pd
import logging

def run_combat(df, metadata):
    logging.info("Running ComBat batch correction...")

    import rpy2.robjects as ro
    from rpy2.robjects import pandas2ri

    pandas2ri.activate()

    ro.r('''
        suppressMessages(library(sva))
        run_combat <- function(expr, batch, condition) {
            mod <- model.matrix(~ condition)
            corrected <- ComBat(
                dat = as.matrix(expr),
                batch =batch,
                mod =mod,
                par.prior = TRUE,
                prior.plots = FALSE
        )
        return(as.data.frame(corrected)) 
    }
    ''')
    r_func = ro.globalenv["run_combat"]

    batch = metadata["batch"]
    condition = metadata["condition"]

    corrected = r_func(df, batch, condition)

    corrected = pd.DataFrame(corrected)
    corrected.columns = df.columns
    corrected.index = df.index

    return corrected
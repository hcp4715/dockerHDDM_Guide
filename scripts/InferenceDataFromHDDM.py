def InferenceDataFromHDDM(modelres=None, nppc = 1000, save_name=None):
    """
    Convert HDDM object with multiple chain to InferenceData
    
    modelres:   a list of HDDM model, each element represents one chain
    nppc:     integer, number of posterior predictives
    savename: string, name used for save the InferenceData
    
    """
    import sys, os, time, csv, glob
    import matplotlib.pyplot as plt
    import seaborn as sns
    import numpy as np
    import pandas as pd
    import xarray as xr
    
    import pymc as pm
    import hddm
    import kabuki
    import arviz as az

    from p_tqdm import p_map
    from functools import partial
    
    from post_pred_gen_redefined import _parents_to_random_posterior_sample
    from post_pred_gen_redefined import _post_pred_generate
    from post_pred_gen_redefined import post_pred_gen

    from pointwise_loglik_gen import _pointwise_like_generate
    from pointwise_loglik_gen import pointwise_like_gen
    

    ms_tmp = modelres
    
    
    # Check whether InferenceData with the same name already exist, if yes, we won't rerun the whole process
    InfDataName = save_name + "_netcdf"
    
    if os.path.exists(InfDataName):
        print("Inference data ", save_name, " already exist, will load model data instead of re-run")
        
        # Load netcdf file
        InfData_tmp = az.from_netcdf(InfDataName)
        
    else:
        print("start converting {}".format(save_name))

        ### Observations
        xdata_observed = ms_tmp[0].data.copy()
        xdata_observed.index.names = ['trial_idx']
        xdata_observed = xdata_observed[['rt', 'response']]
        xdata_observed = xr.Dataset.from_dataframe(xdata_observed)

        ### posteriors
        xdata_posterior = []
        for jj in range(len(ms_tmp)):
            trace_tmp = ms_tmp[jj].get_traces()
            trace_tmp['chain'] = jj
            trace_tmp['draw'] = np.arange(len(trace_tmp), dtype=int)
            xdata_posterior.append(trace_tmp)
        xdata_posterior = pd.concat(xdata_posterior)
        xdata_posterior = xdata_posterior.set_index(["chain", "draw"])
        xdata_posterior = xr.Dataset.from_dataframe(xdata_posterior)

        ### Posterior predictives
        xdata_post_pred = [] # define an empty dict      
        xdata_post_pred = p_map(partial(post_pred_gen, samples = nppc), ms_tmp)

        for chain in range(len(xdata_post_pred)):
            xdata_post_pred[chain]["response"] = xdata_post_pred[chain]["response"].astype(float)

        xdata_post_pred = pd.concat(xdata_post_pred, names=['chain'], 
                                    keys = list(range(len(xdata_post_pred))))
        xdata_post_pred = xdata_post_pred.reset_index(level=1, drop=True)
        xdata_post_pred = xr.Dataset.from_dataframe(xdata_post_pred)

        ### Point-wise log likelihood
        xdata_loglik = [] # define an empty dict
        xdata_loglik = p_map(partial(pointwise_like_gen), ms_tmp)
        xdata_loglik = pd.concat(xdata_loglik, names=['chain'], 
                                 keys = list(range(len(xdata_loglik))))
        xdata_loglik = xdata_loglik.reset_index(level=1, drop=True)
        xdata_loglik = xr.Dataset.from_dataframe(xdata_loglik)

        ### convert to InfData
        InfData_tmp = az.InferenceData(posterior=xdata_posterior, 
                                       observed_data=xdata_observed,
                                       posterior_predictive=xdata_post_pred,
                                       log_likelihood = xdata_loglik)
        
        ### save the InfData for later use
        InfData_tmp.to_netcdf(InfDataName)
        
    return InfData_tmp
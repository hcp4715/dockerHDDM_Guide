def _HDDMarviz(data=None,model=None,samples=2000,nppc = 1000,burn=1000,thin=1,chains=4,savefile=True,savetag=None):
    """
    Run one HDDM and convert to InferenceData
    
    """
    import sys, os, time, csv, glob
    import feather
    import matplotlib.pyplot as plt
    import seaborn as sns
    import numpy as np
    import pandas as pd
    import xarray as xr
    
    import pymc as pm
    import hddm
    import kabuki
    import arviz as az
    from patsy import dmatrix

    from p_tqdm import p_map
    from functools import partial
    
    from post_pred_gen_redefined import _parents_to_random_posterior_sample
    from post_pred_gen_redefined import _post_pred_generate
    from post_pred_gen_redefined import post_pred_gen

    from pointwise_loglik_gen import _pointwise_like_generate
    from pointwise_loglik_gen import pointwise_like_gen
    
    # get the model function's name for saving name
    m_key = model.__name__  
    
    if savetag is not None:
        save_name_m = m_key + "_" + savetag
    else:
        save_name_m = m_key
        
# Check whether InferenceData with the same name already exist, if yes, we won't rerun the whole process
    InfDataName = save_name_m + "_netcdf"
    if os.path.exists(InfDataName):
        print("Inference data ", save_name_m, " already exist, will load model data instead of re-run")
        
        # Load netcdf file
        InfData_tmp = az.from_netcdf(InfDataName)
        
        # Load model files, here we assume that both model object and inferencedata were saved.
        file_names = glob.glob(save_name_m + "_chain_*[!db]", recursive=False)
        file_names = sorted(file_names, key=lambda x: x[-1]) # sort filenames by chain ID
        ms_tmp = []
        for fname in file_names:
            print('current loading: ', fname, '\n')
            ms_tmp.append(hddm.load(fname))
        
    else:
        print("start model fitting for {}".format(m_key))
    
        ms_tmp = p_map(partial(model, 
                               df=data, 
                               samples=samples,
                               burn=burn,
                               thin=thin, 
                               save_name=save_name_m),
                       range(chains))

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
        
    return ms_tmp, InfData_tmp 

def HDDMarviz(data=None, model_func=None, samples=2000, nppc = 1000, burn=1000, thin=1, chains=4, savefile=True, savetag=None):
    """
    Run a model or a list of models in parallel and return an ArviZ InfData or a list of InfData
    
    data: dataframe, input data, can be simulated data or real data
    model_func: string, which defines a function or a list of func that can fit data with "HDDM", "HDDMStimulus", "HDDMRegressor".
    samples: int, n of sample for mcmc
    nppc: # of posterior predictive check, default is 1000, if None, the number will be same as posterior samples, i.e., (samples - burn)/thin
    burn: int, n of sample that will burn in
    thin:
    chains: int, how many chains
    savefile: bool, "True", save the temporary data; "False", do not save. Here we make it always true.
    
    This function will fit the data with all models in the model_func
    
    """
    
    from HDDMarviz import _HDDMarviz
    
    # if model_func is a single function
    if callable(model_func):
        models, InfData = _HDDMarviz(data=data, 
                                     model=model_func, 
                                     samples=samples, 
                                     nppc=nppc, 
                                     burn=burn, 
                                     thin=thin, 
                                     chains=chains, 
                                     savefile=savefile,
                                     savetag=savetag)
    
    # if model_func is a list of functions
    elif isinstance(model_func, list):
        InfData = {}
        models = {}
        for ii in range(len(model_func)):
            m_key = model_func[ii].__name__
            models[m_key] = []
            InfData[m_key] = []
            models[m_key], InfData[m_key] = _HDDMarviz(data=data, 
                                                       model=model_func[ii],
                                                       samples=samples, 
                                                       nppc=nppc, 
                                                       burn=burn, 
                                                       thin=thin, 
                                                       chains=chains, 
                                                       savefile=savefile,
                                                       savetag=savetag)
    else:
        raise ValueError('The model function should be a function or a list of function')
    

    return models, InfData
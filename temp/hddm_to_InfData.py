def hddm_to_InfData(data=None, m_keys=None, model_func=None, runtime="0", samples=2000, nppc = 1000, burn=1000, thin=1, chains=4, savefile=True):
    """
    This func is for running multiple models
    
    data: dataframe, input data, can be simulated data or real data
    m_keys: list, a list of id for different models, which is used as the key for the model_func.
    model_func: list, a list of model functions
    runtime: str, the nth repetition of running the current script
    samples: int, n of sample for mcmc
    burn: ..
    chains: int, how many chains
    savefile: bool, "True", save the temporary data; "False", do not save [NOT USED!!!]
    
    This function will fit the data with all models in the model_func
    
    """
    import sys, os, time, csv
    import pymc as pm
    import hddm
    import kabuki

    import arviz as az
    import numpy as np
    import pandas as pd
    import feather
    import xarray as xr
    import matplotlib.pyplot as plt
    import seaborn as sns
    from patsy import dmatrix

    from p_tqdm import p_map
    from functools import partial
    
    from post_pred_gen_redifined import _parents_to_random_posterior_sample
    from post_pred_gen_redifined import _post_pred_generate
    from post_pred_gen_redifined import post_pred_gen

    from pointwise_loglik_gen import _pointwise_like_generate
    from pointwise_loglik_gen import pointwise_like_gen

    InfData = {}
    models = {}
    
    for ii in range(len(m_keys)):
        m_key = m_keys[ii]

        ### Run models
#         if not os.path.exists("./tmpModelFiles"):
#             os.makedirs(directory)        
        save_name_m = m_key + "_tmp"  + runtime
#         print("start model fitting for ", m_key)
        ms_tmp = p_map(partial(model_func[ii], 
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

        ### PPC
        xdata_post_pred = [] # define an empty dict    
#         print("start PPC for ", m_key)
        start_time = time.time()  
        xdata_post_pred = p_map(partial(post_pred_gen, samples = nppc), ms_tmp)
        
#         print("Save PPC to feather files")
        for chain in range(len(xdata_post_pred)):
            ftrname = "df_" + m_key + "_tmp" + runtime + "_ppc_chain_" + str(chain) + ".ftr"
#             print(ftrname)
            xdata_post_pred[chain].reset_index().to_feather(ftrname)
            xdata_post_pred[chain]["response"] = xdata_post_pred[chain]["response"].astype(float)
        
#         print("Generating PPC for ", m_key, " costs %f seconds" % (time.time() - start_time))
        
        xdata_post_pred = pd.concat(xdata_post_pred, names=['chain'], 
                                    keys = list(range(len(xdata_post_pred))))
        xdata_post_pred = xdata_post_pred.reset_index(level=1, drop=True)
        xdata_post_pred = xr.Dataset.from_dataframe(xdata_post_pred)
        
        ### Point-wise log likelihood
        xdata_loglik = [] # define an empty dict
#         print("start calculating loglik for ", m_key)
        start_time = time.time()  # the start time of the processing
        xdata_loglik = p_map(partial(pointwise_like_gen), ms_tmp)
        
        for chain in range(len(xdata_loglik)):
            ftrname = "df_" + m_key + "_tmp" + runtime + "_pll_chain_" + str(chain) + ".ftr"
#             print(ftrname)
            xdata_loglik[chain].reset_index().to_feather(ftrname)
            
#         print("Generating loglik for", m_key, " costs %f seconds" % (time.time() - start_time))

        xdata_loglik = pd.concat(xdata_loglik, names=['chain'], 
                                keys = list(range(len(xdata_loglik))))
        xdata_loglik = xdata_loglik.reset_index(level=1, drop=True)
        xdata_loglik = xr.Dataset.from_dataframe(xdata_loglik)
        
        ### convert to InfData
        InfData[m_key] = az.InferenceData(posterior=xdata_posterior, 
                                                 observed_data=xdata_observed,
                                                 posterior_predictive=xdata_post_pred,
                                                 log_likelihood = xdata_loglik)
        models[m_key] = ms_tmp
    return models, InfData
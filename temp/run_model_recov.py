# Preparation
import sys, os, time, csv
import glob
import datetime
from datetime import date

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

import argparse

# sys.path.append('../')
# sys.path.append('../model_code/')
# sys.path.append('../data_processing_code/')
sys.path.append('./')

from post_pred_gen_redifined import _parents_to_random_posterior_sample
from post_pred_gen_redifined import _post_pred_generate
from post_pred_gen_redifined import post_pred_gen

from pointwise_loglik_gen import _pointwise_like_generate
from pointwise_loglik_gen import pointwise_like_gen

# import self-defined functions
from SimData import SimData
from model_recov import model_recov
from run_models import run_m1, run_m2, run_m4, run_m5, run_m7

model_func = [run_m1, run_m2, run_m4, run_m5, run_m7]

m_keys = ["ms1",
          "ms2",
          "ms4",
          "ms5",
          "ms7"]

df_keys = ["sim_df1", 
           "sim_df2", 
           "sim_df4", 
           "sim_df5",
           "sim_df7"]

def main():
    '''
    This python function is a wrapper used to run model recovery.

    Examples of how to call it:

    # run model recovery for the 1st time, with 4 iterations, 2000 samples, 1000 burn, and 4 chain
    python run_model_recov.py --runtime "0" --iteration 4 --samples 2000 --burn 1000 --chains 4
    
    # run model without warnings
    python -W ignore run_model_recov.py --runtime "0" --iteration 4 --samples 2000 --burn 1000 --chains 4

    '''

    parser = argparse.ArgumentParser()
#     parser.add_argument('--seed', type=int, default=4)
    parser.add_argument('--runtime', '-rt', type=str, default="0")
    parser.add_argument('--iteration', '-it', type=int, default=1)
    parser.add_argument('--samples', '-sp', type=int, default=2000)
    parser.add_argument('--burn', '-bn', type=int, default=1000)
    parser.add_argument('--chains', '-ch', type=int, default=4)

    args = parser.parse_args()
    print(args.runtime)
    print(args.iteration)
    print(args.samples)
    print(args.burn)
    print(args.chains)
    
    conf_mat_dic = pd.DataFrame(0, index=m_keys, columns=df_keys)
    conf_mat_loo = pd.DataFrame(0, index=m_keys, columns=df_keys)
    conf_mat_waic = pd.DataFrame(0, index=m_keys, columns=df_keys)

    for sim in range (args.iteration):   
        for df_key in df_keys:
            ### simulate data
            data = SimData(df_key)

            ### fit the sim data
            print("Start model recovery for ", df_key)
            models, InfData = model_recov(data=data, 
                                          m_keys=m_keys, 
                                          model_func=model_func,
                                          runtime=args.runtime,
                                          samples = args.samples,
                                          burn=args.burn,
                                          chains=args.chains)
            ### compare models
            tmp_loo_comp = az.compare(InfData, ic="loo")
            tmp_loo_comp = tmp_loo_comp.reset_index()
            tmp_waic_comp = az.compare(InfData, ic="waic")
            tmp_waic_comp = tmp_waic_comp.reset_index()

            tmp_dic = []
            indx_name = []

            for m_key, model in models.items():
                m_tmp = kabuki.utils.concat_models(model)
                tmp_dic.append(m_tmp.dic)
                indx_name.append(m_key)

            tmp_dic_comp = pd.DataFrame(tmp_dic, index=indx_name, columns=['dic'])
            tmp_dic_comp = tmp_dic_comp.sort_values(by=['dic'])
            tmp_dic_comp = tmp_dic_comp.reset_index()
            #conf_mat_dic.rename(columns={'index':'rank'}, inplace=True)

            ### record the best models
            conf_mat_dic.loc[tmp_dic_comp.loc[0, 'index'], df_key] += 1
            conf_mat_loo.loc[tmp_loo_comp.loc[0, 'index'], df_key] += 1
            conf_mat_waic.loc[tmp_waic_comp.loc[0, 'index'], df_key] += 1
            
            fname_dic = "conf_mat_dic_" + args.runtime + ".csv"
            fname_loo = "conf_mat_loo_" + args.runtime + ".csv"
            fname_waic = "conf_mat_waic_" + args.runtime + ".csv"
            conf_mat_dic.to_csv(fname_dic)
            conf_mat_loo.to_csv(fname_loo)
            conf_mat_waic.to_csv(fname_waic)

if __name__=='__main__':
    main()
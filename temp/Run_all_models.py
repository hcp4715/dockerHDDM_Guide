# Preparation
import sys, os, time, csv
import glob
import datetime
from datetime import date
import random

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
# from SimData import SimData


def main():
    '''
    This python function is a wrapper used to run our models, which were defined in "Def_Models".

    Examples of how to call it:

    # run model recovery for the 1st time, with 4 iterations, 2000 samples, 1000 burn, and 4 chain
    python -W ignore Run_all_models.py --samples 30 --burn 10 --thin 5 --nppc 8 --chains 4 --test 1 --save 0 --model "ms7"
    
    
    # run model 7 without warnings
    python -W ignore Run_all_models.py --samples 15000 --burn 7000 --thin 5 --nppc 1000 --chains 4 --test 0 --save 1 --model "ms7"

    # run all models without warnings
    python -W ignore Run_all_models.py --samples 25000 --burn 10000 --thin 3 --nppc 1000 --chains 4 --test 0 --save 1
    '''
    
    from hddm_to_InfData import hddm_to_InfData
    from Def_Models import run_m0, run_m1, run_m2, run_m3,run_m4, run_m5, run_m6, run_m7

    model_func = [run_m0, run_m1, run_m2, run_m3,run_m4, run_m5, run_m6, run_m7]

    m_keys = ["ms0",
              "ms1",
              "ms2",
              "ms3",
              "ms4",
              "ms5",
              "ms6",
              "ms7"]
    
    parser = argparse.ArgumentParser()
#     parser.add_argument('--seed', type=int, default=4)
#     parser.add_argument('--runtime', '-rt', type=str, default="0")
    
    parser.add_argument('--samples', '-sp', type=int, default=2000)
    parser.add_argument('--burn', '-bn', type=int, default=1000)
    parser.add_argument('--thin', '-tn', type=int, default=1)
    parser.add_argument('--nppc', '-np', type=int, default=1000)
    parser.add_argument('--chains', '-ch', type=int, default=4)
    parser.add_argument('--test', '-t', type=int, default=0)
    parser.add_argument('--save', '-s', type=int, default=1)
    parser.add_argument('--model', '-m', type=str, default=None)
    
    args = parser.parse_args()
    
    data = hddm.load_csv('/opt/conda/lib/python3.7/site-packages/hddm/examples/cavanagh_theta_nn.csv')
    
    if args.test == 1:
        print("This is a testing run")
        runtime = "0"
        samples = args.samples
        burn = args.burn
        thin = args.thin
        nppc = args.nppc
        chains = args.chains

        df_subj = data['subj_idx'].unique()
        # random select without repetition
        random.seed(10)
        indices = random.sample(range(len(df_subj)), 5)
        df_test_list = [df_subj[i] for i in sorted(indices)]    
        data = data[data['subj_idx'].isin(df_test_list)]
    else:
        print("This is NOT a testing run")
        runtime = "1"
        samples = args.samples
        burn = args.burn
        thin = args.thin
        nppc = args.nppc
        chains = args.chains
        
    if args.save == 0:
        savefile = False
        print("We will NOT save the files")
    else:
        savefile = True
        print("We will save the files")
        
    if args.model is None:
        m_keys = m_keys
        model_func = model_func
    else:
        model_func = [model_func[m_keys.index(args.model)]]
        m_keys = [m_keys[m_keys.index(args.model)]]
        print("The model of current run is: ", args.model)
    
    print("The Run time is: ", runtime)
    print("The # of MCMC samples: ", samples)
    print("The # of PPC: ", nppc)
    print("The # of burnin is: ", burn)
    print("The # of Chains: ", chains)

    models, InfData = hddm_to_InfData(data=data,
                                      m_keys=m_keys, 
                                      model_func=model_func,
                                      runtime=runtime,
                                      samples=samples,
                                      burn=burn,
                                      thin=thin,
                                      nppc=nppc,
                                      chains=chains,
                                      savefile=savefile)
    
if __name__=='__main__':
    main()
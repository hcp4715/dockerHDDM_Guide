### Note about this script 
# 
# Purpose: run all models defined in `Def_Models.py` in terminal
#

import random, sys, os, csv   # import random and other related library
import hddm                   # import hdddm
import argparse               # import argpase for defining arguments

# Add the folder that contains script in path
# This path is useful inside the docker image, 
# Please change the path to your local folder path if you use this outside docker
scripts_dir = '/home/jovyan/scripts'  
sys.path.append(scripts_dir)

# define the function that can be run in terminal
def main():
    '''
    This python function is a wrapper used to run our models, which were defined in "Def_Models". Examples of how to call it:

    ## run a quick test
    python -W ignore Run_all_models.py --samples 30 --burn 10 --thin 3 --nppc 8 --chains 4 --test 1 --model "ms0"
    
    # run the model 4 without warnings
    python -W ignore Run_all_models.py --samples 30000 --burn 9000 --thin 3 --nppc 5000 --chains 4 --test 0 --model "ms4"

    # run all models without warnings
    python -W ignore Run_all_models.py --samples 40000 --burn 10000 --thin 3 --nppc 5000 --chains 5 --test 0
    '''
    # import the self-defined function
    from HDDMarviz import HDDMarviz
    # import the models
    from Def_Models import ms0, ms1, ms2, ms3, ms4

    # put all models in a list
    model_func = [ms0, ms1, ms2, ms3, ms4]

    # create a list of model key for later retrieval.
    m_keys = ["ms0",
              "ms1",
              "ms2",
              "ms3",
              "ms4"]
    
    # Define the input arguments of the current script, we can add more if we have different needs.
    parser = argparse.ArgumentParser()   
    parser.add_argument('--samples', '-sp', type=int, default=2000)  # number of samples
    parser.add_argument('--burn', '-bn', type=int, default=1000)     # number of burnin (warmup)
    parser.add_argument('--thin', '-tn', type=int, default=1)        # number of thin
    parser.add_argument('--nppc', '-np', type=int, default=1000)     # number of posterior predicitve samples
    parser.add_argument('--chains', '-ch', type=int, default=4)      # number of chains of mcmc
    parser.add_argument('--test', '-t', type=int, default=0)         # use test to define to mode: testing or real data fitting 
    parser.add_argument('--model', '-m', type=str, default=None)     # input model defining functions 
    parser.add_argument('--savetag', '-tag', type=str, default=None) # tag for saving model files
    args = parser.parse_args()
    
    # load the data will be used as input
    data = hddm.load_csv(hddm.__path__[0] + '/examples/cavanagh_theta_nn.csv')
    
    if args.test == 1: # use test to define to mode: testing or real data fitting Run a simple and quick model to test the script.
        print("This is a testing run")
        runtime = "0"
        samples = args.samples
        burn = args.burn
        thin = args.thin
        nppc = args.nppc
        chains = args.chains
        df_subj = data['subj_idx'].unique()
        random.seed(10)
        indices = random.sample(range(len(df_subj)), 5) # random select 5 participant to save time
        df_test_list = [df_subj[i] for i in sorted(indices)]    
        data = data[data['subj_idx'].isin(df_test_list)]
        savetag="tmp"
    else:
        print("This is NOT a testing run")
        runtime = "1"
        samples = args.samples
        burn = args.burn
        thin = args.thin
        nppc = args.nppc
        chains = args.chains
        savetag = args.savetag
        
    if args.model is None: # if model is not specified, run all models in the model list.
        m_keys = m_keys
        model_func = model_func
        print("Will runn all models in the model_func")
    else:
        model_func = [model_func[m_keys.index(args.model)]]
        m_keys = [m_keys[m_keys.index(args.model)]]
        print("The model of current run is: ", args.model)

    print("The # of MCMC samples: ", samples)
    print("The # of PPC: ", nppc)
    print("The # of burnin is: ", burn)
    print("The # of Chains: ", chains)

    models, InfData = HDDMarviz(data=data, 
                                model_func=model_func,
                                samples=samples, 
                                nppc=nppc, 
                                burn=burn, 
                                thin=thin, 
                                chains=chains, 
                                savetag=savetag)
    
if __name__=='__main__':
    main()
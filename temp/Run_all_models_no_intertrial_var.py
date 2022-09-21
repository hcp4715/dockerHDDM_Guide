import random
import hddm
import argparse, sys, os, csv

scripts_dir = '/home/jovyan/scripts'
sys.path.append(scripts_dir)

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
    from Def_Models_no_intertrial_var import ms0, ms1_noSV, ms2_noSV, ms3_noSV, ms4_noSV, ms5_noSV
   
    # put all models in a list
    model_func = [ms0, ms1_noSV, ms2_noSV, ms3_noSV, ms4_noSV, ms5_noSV]
    
    # create a list of model key for later retrieval.
    m_keys = ["ms0",
              "ms1_noSV",
              "ms2_noSV",
              "ms3_noSV",
              "ms4_noSV",
              "ms5_noSV"]
    
    # Define the input arguments of the current script, we can add more if we have different needs.
    parser = argparse.ArgumentParser()   
    parser.add_argument('--samples', '-sp', type=int, default=2000)
    parser.add_argument('--burn', '-bn', type=int, default=1000)
    parser.add_argument('--thin', '-tn', type=int, default=1)
    parser.add_argument('--nppc', '-np', type=int, default=1000)
    parser.add_argument('--chains', '-ch', type=int, default=4)
    parser.add_argument('--test', '-t', type=int, default=0)
    parser.add_argument('--model', '-m', type=str, default=None)
    parser.add_argument('--savetag', '-tag', type=str, default=None)
    args = parser.parse_args()
    
    # data = hddm.load_csv(os.path.join(os.path.dirname(hddm.__file__), 
    #                                       'examples', 
    #                                       'cavanagh_theta_nn.csv'))
    
    data = hddm.load_csv(hddm.__path__[0] + '/examples/cavanagh_theta_nn.csv')
    
    # Run a simple and quick model to test the script.
    if args.test == 1:
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
                                # savefile=True,
                                savetag=savetag)
    
if __name__=='__main__':
    main()
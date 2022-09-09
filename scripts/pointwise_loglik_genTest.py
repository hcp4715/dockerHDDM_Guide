# https://github.com/hddm-devs/kabuki/blob/master/kabuki/analyze.py#L420
def _parents_to_random_posterior_sample(bottom_node, pos=None):
    """Walks through parents and sets them to pos sample."""
    import pymc as pm
    import numpy as np
    for i, parent in enumerate(bottom_node.extended_parents):

        assert len(parent.trace()) >= pos, "pos larger than posterior sample size"
        parent.value = parent.trace()[pos]

def _pointwise_like_generate(bottom_node, samples=None, subsample=None, data=None, append_data=False):
    """Generate posterior predictive data from a single observed node."""
    import pymc as pm
    import numpy as np
    import pandas as pd
    from copy import deepcopy
    import hddm
    
    datasets = []

    ##############################
    # Iterate the posterior and generate likelihood for each data point
    
    for i, parent in enumerate(bottom_node.extended_parents):
        if not isinstance(parent, pm.Node): # Skip non-stochastic nodes
            continue
        else:
            mc_len = len(parent.trace())
            break
    # samples=samples
    if samples is None:
        samples = mc_len
        # print("Number of samples is equal to length of MCMC trace.")

    assert samples, "Can not determine the number of samples"
    
    for sample in range(samples):
        _parents_to_random_posterior_sample(bottom_node, pos = sample)
        
        param_dict = deepcopy(bottom_node.parents.value)
        
        # for regressor models
        if 'reg_outcomes' in param_dict:
            del param_dict['reg_outcomes']

            pointwise_lik = bottom_node.value.copy()
            pointwise_lik.index.names = ['trial_idx']        # change the index label as "trial_idx"
            pointwise_lik.drop(['rt'],axis=1,inplace=True)   # drop 'rt' b/c not gonna use it.

            for i in bottom_node.value.index:
                # get current params
                for p in bottom_node.parents['reg_outcomes']:
                    param_dict[p] = bottom_node.parents.value[p].loc[i].item()

                # calculate the point-wise likelihood.
                tmp_lik = hddm.wfpt.pdf_array(x = np.array(bottom_node.value.loc[i]),
                                              v = np.array(param_dict['v']),
                                               a = np.array(param_dict['a']), 
                                               t = np.array(param_dict['t']),
                                               p_outlier = param_dict['p_outlier'],
                                               sv = param_dict['sv'],
                                               z = param_dict['z'],
                                               sz = param_dict['sz'],
                                               st = param_dict['st'])
                pointwise_lik.loc[i, 'log_lik'] = tmp_lik
                
            # check if there is zero prob.
            if 0 in pointwise_lik.values:
                pointwise_lik['log_lik']=pointwise_lik['log_lik'].replace(0.0, pointwise_lik['log_lik'].mean())

            elif pointwise_lik['log_lik'].isnull().values.any():
                print('NAN in the likelihood, check the data !')
                break

            pointwise_lik['log_lik'] = np.log(pointwise_lik['log_lik'])

            if np.isinf(pointwise_lik['log_lik']).values.sum() > 0:
                print('Correction does not work!!!\n')
                
        # for other models
        else:
            tmp_lik = hddm.wfpt.pdf_array(x = bottom_node.value['rt'].values,
                                          v = np.array(param_dict['v']),
                                          a = np.array(param_dict['a']), 
                                          t = np.array(param_dict['t']),
                                          p_outlier = param_dict['p_outlier'],
                                          sv = param_dict['sv'],
                                          z = param_dict['z'],
                                          sz = param_dict['sz'],
                                          st = param_dict['st'])
            # check if there is zero prob.
            if np.sum(tmp_lik == 0.0) > 0:
                tmp_lik[tmp_lik == 0.0] = np.mean(tmp_lik)
            elif np.sum(np.isnan(tmp_lik))  > 0:
                print('NAN in the likelihood, check the data !')
                break

#             obs = np.log(tmp_lik)                
            tmp_lik = np.log(tmp_lik)
            
            if np.sum(np.isinf(tmp_lik)) > 0:
                print('Correction does not work!!!\n')

            pointwise_lik = pd.DataFrame({'log_lik': tmp_lik}, index=bottom_node.value.index)
            pointwise_lik.index.names = ['trial_idx'] 

        datasets.append(pointwise_lik)

    return datasets


def pointwise_like_gen(model, groupby=None, samples=None, subsample=None, append_data=False, progress_bar=True):
    """Run posterior predictive check on a model.
    :Arguments:
        model : kabuki.Hierarchical
            Kabuki model over which to compute the ppc on.
        
    :Optional:
        samples : int
            How many draws of MCMC are used to generate for each node.
        
        subsample: n of subsample
        groupby : list
            Alternative grouping of the data. If not supplied, uses splitting
            of the model (as provided by depends_on).
        append_data : bool (default=False)
            Whether to append the observed data of each node to the replicatons.
        progress_bar : bool (default=True)
            Display progress bar
    :Returns:
        Hierarchical pandas.DataFrame with multiple sampled RT data sets.
        1st level: wfpt node
        2nd level: draw, i.e., draw/sample of MCMC
        3rd level: original data index, which was renamed as "trial_idx"
    :See also:
        post_pred_stats
    """
    import pymc.progressbar as pbar
    import pandas as pd
    
    print("started to generate posterior predicitves")
    
    results = {}

    # Progress bar
    if progress_bar:
        n_iter = len(model.get_observeds())
        bar = pbar.progress_bar(n_iter)
        bar_iter = 0
    else:
        print("Sampling...")

    if groupby is None:
        #### here I changed `iloc` to `loc`
        iter_data = ((name, model.data.loc[obs['node'].value.index]) for name, obs in model.iter_observeds())
    else:
        iter_data = model.data.groupby(groupby)

    # iterate through each node
    for name, data in iter_data:
        node = model.get_data_nodes(data.index)

        if progress_bar:
            bar_iter += 1
            bar.update(bar_iter)

        if node is None or not hasattr(node, 'random'):
            continue # Skip

        ##############################
        # Sample and generate stats
        datasets = _pointwise_like_generate(node, samples=samples, subsample = subsample, data=data, append_data=append_data)
        results[name] = pd.concat(datasets, names=['draw'], keys=list(range(len(datasets))))
            

    if progress_bar:
        bar_iter += 1
        bar.update(bar_iter)


    return pd.concat(results, names=['node'])
# https://github.com/hddm-devs/kabuki/blob/master/kabuki/analyze.py#L420
def _parents_to_random_posterior_sample(bottom_node, pos=None):
    """Walks through parents and sets them to pos sample."""
    import pymc as pm
    import numpy as np
    for i, parent in enumerate(bottom_node.extended_parents):
#         if not isinstance(parent, pm.Node): # Skip non-stochastic nodes
#             continue

#         if pos is None:
#             # Set to random posterior position
#             pos = np.random.randint(0, len(parent.trace()))

        assert len(parent.trace()) >= pos, "pos larger than posterior sample size"
        parent.value = parent.trace()[pos]

# https://github.com/hddm-devs/kabuki/blob/master/kabuki/analyze.py#L271
def _post_pred_generate(bottom_node, samples=None, data=None, append_data=False):
    """Generate posterior predictive data from a single observed node."""
    import pymc as pm
    import numpy as np
    
    
    datasets = []

    ##############################
    # Sample and generate stats
    # If number of samples is fixed, use the original code, i.e., randomly sample one set of
    # values from extended_parents and generate random value;
    #
    # If number of samples is None, use the lenght of trace, and iterate the whole posterior.

    for i, parent in enumerate(bottom_node.extended_parents):
        if not isinstance(parent, pm.Node): # Skip non-stochastic nodes
            continue
        else:
            mc_len = len(parent.trace())
            break
    # samples=samples
    if samples is None:
            samples = mc_len
            print("Number of samples is equal to length of MCMC trace.")

    assert samples, "Can not determine the number of samples"
    
    if samples == mc_len:
        for sample in range(samples):
            _parents_to_random_posterior_sample(bottom_node, pos = sample)
            
            # Generate data from bottom node
            sampled_data = bottom_node.random()
            sampled_data.index = bottom_node.value.index
            sampled_data.index.names = ['trial_idx']

            # add the "response" column for regression models
            if not "response" in sampled_data.columns:
                sampled_data["response"] = np.where(sampled_data['rt'] > 0, 1,
                                                    np.where(sampled_data['rt'] <=0, 0, None)) 
                        
            if append_data and data is not None:
                sampled_data = sampled_data.join(data.reset_index(), lsuffix='_sampled')
            datasets.append(sampled_data)
    
    else:
        for sample in range(samples):
            pos = np.random.randint(0, mc_len)
            _parents_to_random_posterior_sample(bottom_node, pos = pos)

            # Generate data from bottom node
            sampled_data = bottom_node.random()
            sampled_data.index = bottom_node.value.index  # data's trial_idx to the ppc data
            sampled_data.index.names = ['trial_idx']
            
            # add the "response" column for regression models
            if not "response" in sampled_data.columns:
                sampled_data["response"] = np.where(sampled_data['rt'] > 0, 1,
                                                    np.where(sampled_data['rt'] <=0, 0, None)) 

            if append_data and data is not None:
                sampled_data = sampled_data.join(data.reset_index(), lsuffix='_sampled')
            datasets.append(sampled_data)

    return datasets

# https://github.com/hddm-devs/kabuki/blob/master/kabuki/analyze.py#L287
def prior_pred_gen(model, groupby=None, samples=None, append_data=False, progress_bar=True):
    """Run prior predictive check on a model. (not finished yet)
    :Arguments:
        model : kabuki.Hierarchical
            Kabuki model over which to compute the ppc on.
    :Optional:
        samples : int
            How many samples to generate for each node. If None, will used the MCMC samples

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
        2nd level: draw, i.e., draw of MCMC or samples of prior predictive.
        3rd level: original data index (trial_idx)
    :See also:
        prior_pred_stats
    """
    import pymc.progressbar as pbar
    import pandas as pd
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

    for name, data in iter_data:
        node = model.get_data_nodes(data.index)

        if progress_bar:
            bar_iter += 1
            bar.update(bar_iter)

        if node is None or not hasattr(node, 'random'):
            continue # Skip

        ##############################
        # Sample and generate stats
        datasets = _post_pred_generate(node, samples=samples, data=data, append_data=append_data)
        results[name] = pd.concat(datasets, names=['draw'], keys=list(range(len(datasets))))            

    if progress_bar:
        bar_iter += 1
        bar.update(bar_iter)

    return pd.concat(results, names=['node'])
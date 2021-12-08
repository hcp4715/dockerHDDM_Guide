def plot_ppc_by_cond(
    data,
    or_d=None, # original dataset
    subjs=None,     # subject's index
    conds=None,     # condition
    kind="kde",
    alpha=None,
    mean=True,
    observed=True,
    color=None,
    colors=None,
    grid=None,
    figsize=None,
    textsize=None,
    data_pairs=None,
    var_names=None,
    filter_vars=None,
    coords=None,
    flatten=None,
    flatten_pp=None,
    num_pp_samples=None,
    random_seed=None,
    jitter=None,
    animated=False,
    animation_kwargs=None,
    legend=True,
    labeller=None,
    ax=None,
    backend=None,
    backend_kwargs=None,
    group="posterior",
    show=None,
):
    """
    Plot for posterior/prior predictive checks.

    Parameters
    ----------

    """
    from arviz.plots.plot_utils import (
        default_grid,
        filter_plotters_list,
        get_plotting_function,
        _scale_fig_size,
    )
    
    from arviz.labels import BaseLabeller
    from arviz.sel_utils import xarray_var_iter
    from arviz.rcparams import rcParams
    
    from arviz.utils import (
        _var_names,
        _subset_list,
    )
    
#         xarray_sel_iter,
#         _dims,
#         _zip_dims,
#         _scale_fig_size,
        
    from itertools import product
    # _var_names, _subset_list, filter_plotters_list,
    # xarray_sel_iter, xarray_var_iter, _dims, _zip_dims
#     from func4PPCPlot import , , 
#     from func4PPCPlot import 
#     from func4PPCPlot import default_grid, get_plotting_function
    # from rcparams import 
    from numbers import Integral
    import numpy as np
    
    if group not in ("posterior", "prior"):
        raise TypeError("`group` argument must be either `posterior` or `prior`")

    for groups in (f"{group}_predictive", "observed_data"):
        if not hasattr(data, groups):
            raise TypeError(f'`data` argument must have the group "{groups}" for ppcplot')

    if kind.lower() not in ("kde", "cumulative", "scatter"):
        raise TypeError("`kind` argument must be either `kde`, `cumulative`, or `scatter`")

    if colors is None:
        colors = ["C0", "k", "C1"]

    if isinstance(colors, str):
        raise TypeError("colors should be a list with 3 items.")

    if len(colors) != 3:
        raise ValueError("colors should be a list with 3 items.")

    if color is not None:
        warnings.warn("color has been deprecated in favor of colors", FutureWarning)
        colors[0] = color

    if data_pairs is None:
        data_pairs = {}

    if backend is None:
        backend = rcParams["plot.backend"]
    backend = backend.lower()
    if backend == "bokeh":
        if animated:
            raise TypeError("Animation option is only supported with matplotlib backend.")

    observed_data = data.observed_data

    if group == "posterior":
        predictive_dataset = data.posterior_predictive
    elif group == "prior":
        predictive_dataset = data.prior_predictive

    if coords is None:
        coords = {}

    if labeller is None:
        labeller = BaseLabeller()

    if random_seed is not None:
        np.random.seed(random_seed)

    total_pp_samples = predictive_dataset.sizes["chain"] * predictive_dataset.sizes["draw"]
    if num_pp_samples is None:
        if kind == "scatter" and not animated:
            num_pp_samples = min(5, total_pp_samples)
        else:
            num_pp_samples = total_pp_samples

    if (
        not isinstance(num_pp_samples, Integral)
        or num_pp_samples < 1
        or num_pp_samples > total_pp_samples
    ):
        raise TypeError(
            "`num_pp_samples` must be an integer between 1 and " + f"{total_pp_samples}."
        )

    pp_sample_ix = np.random.choice(total_pp_samples, size=num_pp_samples, replace=False)

    for key in coords.keys():
        coords[key] = np.where(np.in1d(observed_data[key], coords[key]))[0]
        
    obs_plotters = []
    pp_plotters = []

    if conds is None:
        dim_tmp = ['subj_idx']
        level_ls = subjs
    else:
        dim_tmp = ['subj_idx'] + conds
    #     levels = list(chain(or_d[conds].drop_duplicates().values.tolist()))
        levels = or_d[conds].drop_duplicates().values.tolist()
        level_ls = list(product(subjs, levels))


    # convert tuple to a dict
    levels_ls_tmp= {}
    for ii in range(len(level_ls)):
        tmp = level_ls[ii]
        levels_ls_tmp[ii] = []
        if (isinstance(tmp, int)) or (isinstance(tmp, str)):
            levels_ls_tmp[ii].append(tmp)
        else: #  isinstance(tmp, list):
            for jj in tmp:
    #             print(jj)
                if (isinstance(jj, int)) or (isinstance(jj, str)):
                    levels_ls_tmp[ii].append(jj)
                else:
                    levels_ls_tmp[ii]  = levels_ls_tmp[ii] + jj

    # dict's value to list       
    level_ls = list(levels_ls_tmp.values())

    for level in level_ls:
        print(level)
        # combine the subj_idx with conditions
        crit_tmp=[]
        for i, j in zip(dim_tmp, level):
            if isinstance(j, str):
                crit_tmp.append(i + "=='" + str(j) + "'")
            else:
                crit_tmp.append(i + "==" + str(j))

        crit_tmp = " and ".join(crit_tmp) # combine the conditions
        plot_idx = or_d.query(crit_tmp).index

        data_tmp = data.isel(trial_idx=plot_idx)

        observed_data_tmp = data_tmp.observed_data
        predictive_data_tmp = data_tmp.posterior_predictive

        if var_names is None:
            var_names = list(observed_data_tmp.data_vars)
        data_pairs = {}
        var_names = _var_names(var_names, observed_data_tmp, None)
        pp_var_names = [data_pairs.get(var, var) for var in var_names]
        pp_var_names = _var_names(pp_var_names, predictive_data_tmp, None)

        flatten_pp = None
        flatten = None
        num_pp_samples = 50
        coords = {}

        if flatten_pp is None and flatten is None:
            flatten_pp = list(predictive_data_tmp.dims.keys())
        elif flatten_pp is None:
            flatten_pp = flatten
        if flatten is None:
            flatten = list(observed_data_tmp.dims.keys())

        total_pp_samples = predictive_data_tmp.sizes["chain"] * predictive_data_tmp.sizes["draw"]

        pp_sample_ix = np.random.choice(total_pp_samples, size=num_pp_samples, replace=False)

        for key in coords.keys():
            coords[key] = np.where(np.in1d(observed_data_tmp[key], coords[key]))[0]

        obs_plotters_tmp = filter_plotters_list(
            list(
                xarray_var_iter(
                    observed_data_tmp.isel(coords),
                    skip_dims=set(flatten),
                    var_names=var_names,
                    combined=True,
                )
            ),
            "plot_ppc",
        )

        length_plotters_tmp = len(obs_plotters_tmp)
        pp_plotters_tmp = [
            tup
            for _, tup in zip(
                range(length_plotters_tmp),
                xarray_var_iter(
                    predictive_data_tmp.isel(coords),
                    var_names=pp_var_names,
                    skip_dims=set(flatten_pp),
                    combined=True,
                ),
            )
        ]

        for var_idx in range(len(var_names)):
            tmp0 = list(obs_plotters_tmp[0])
            tmp1 = list(pp_plotters_tmp[0])
            for i, j in zip(dim_tmp, level):
                if i == "subj_idx":        
                    tmp0[1][i] = "subj_" + str(j)
                    tmp0[2][i] = "subj_" + str(j)
                    tmp1[1][i] = "subj_" + str(j)
                    tmp1[2][i] = "subj_" + str(j)
                else:
                    tmp0[1][i] = i + "_" + str(j)
                    tmp0[2][i] = i + "_" + str(j)
                    tmp1[1][i] = i + "_" + str(j)
                    tmp1[2][i] = i + "_" + str(j)

            obs_plotters.append(tuple(tmp0))
            pp_plotters.append(tuple(tmp1))
                    
    length_plotters = len(obs_plotters)
    rows, cols = default_grid(length_plotters, grid=grid)

    ppcplot_kwargs = dict(
        ax=ax,
        length_plotters=length_plotters,
        rows=rows,
        cols=cols,
        figsize=figsize,
        animated=animated,
        obs_plotters=obs_plotters,
        pp_plotters=pp_plotters,
        predictive_dataset=predictive_dataset,
        pp_sample_ix=pp_sample_ix,
        kind=kind,
        alpha=alpha,
        colors=colors,
        jitter=jitter,
        textsize=textsize,
        mean=mean,
        observed=observed,
        total_pp_samples=total_pp_samples,
        legend=legend,
        labeller=labeller,
        group=group,
        animation_kwargs=animation_kwargs,
        num_pp_samples=num_pp_samples,
        backend_kwargs=backend_kwargs,
        show=show,
    )

    # TODO: Add backend kwargs
    plot = get_plotting_function("plot_ppc", "ppcplot", backend)
    axes = plot(**ppcplot_kwargs)
    return axes

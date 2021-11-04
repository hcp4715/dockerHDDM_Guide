## This script re-define the functions needed for ploting condition-wise ppc

def _var_names(var_names, data, filter_vars=None):
    """Handle var_names input across arviz.
    Parameters
    ----------
    var_names: str, list, or None
    data : xarray.Dataset
        Posterior data in an xarray
    filter_vars: {None, "like", "regex"}, optional, default=None
        If `None` (default), interpret var_names as the real variables names. If "like",
         interpret var_names as substrings of the real variables names. If "regex",
         interpret var_names as regular expressions on the real variables names. A la
        `pandas.filter`.
    Returns
    -------
    var_name: list or None
    """
    if filter_vars not in {None, "like", "regex"}:
        raise ValueError(
            f"'filter_vars' can only be None, 'like', or 'regex', got: '{filter_vars}'"
        )

    if var_names is not None:
        if isinstance(data, (list, tuple)):
            all_vars = []
            for dataset in data:
                dataset_vars = list(dataset.data_vars)
                for var in dataset_vars:
                    if var not in all_vars:
                        all_vars.append(var)
        else:
            all_vars = list(data.data_vars)

        all_vars_tilde = [var for var in all_vars if var.startswith("~")]
        if all_vars_tilde:
            warnings.warn(
                """ArviZ treats '~' as a negation character for variable selection.
                   Your model has variables names starting with '~', {0}. Please double check
                   your results to ensure all variables are included""".format(
                    ", ".join(all_vars_tilde)
                )
            )

        try:
            var_names = _subset_list(var_names, all_vars, filter_items=filter_vars, warn=False)
        except KeyError as err:
            msg = " ".join(("var names:", f"{err}", "in dataset"))
            raise KeyError(msg) from err
    return var_names

def _subset_list(subset, whole_list, filter_items=None, warn=True):
    """Handle list subsetting (var_names, groups...) across arviz.
    Parameters
    ----------
    subset : str, list, or None
    whole_list : list
        List from which to select a subset according to subset elements and
        filter_items value.
    filter_items : {None, "like", "regex"}, optional
        If `None` (default), interpret `subset` as the exact elements in `whole_list`
        names. If "like", interpret `subset` as substrings of the elements in
        `whole_list`. If "regex", interpret `subset` as regular expressions to match
        elements in `whole_list`. A la `pandas.filter`.
    Returns
    -------
    list or None
        A subset of ``whole_list`` fulfilling the requests imposed by ``subset``
        and ``filter_items``.
    """
    import numpy as np
    if subset is not None:

        if isinstance(subset, str):
            subset = [subset]

        whole_list_tilde = [item for item in whole_list if item.startswith("~")]
        if whole_list_tilde and warn:
            warnings.warn(
                "ArviZ treats '~' as a negation character for selection. There are "
                "elements in `whole_list` starting with '~', {0}. Please double check"
                "your results to ensure all elements are included".format(
                    ", ".join(whole_list_tilde)
                )
            )

        excluded_items = [
            item[1:] for item in subset if item.startswith("~") and item not in whole_list
        ]
        filter_items = str(filter_items).lower()
        not_found = []

        if excluded_items:
            if filter_items in ("like", "regex"):
                for pattern in excluded_items[:]:
                    excluded_items.remove(pattern)
                    if filter_items == "like":
                        real_items = [real_item for real_item in whole_list if pattern in real_item]
                    else:
                        # i.e filter_items == "regex"
                        real_items = [
                            real_item for real_item in whole_list if re.search(pattern, real_item)
                        ]
                    if not real_items:
                        not_found.append(pattern)
                    excluded_items.extend(real_items)
            not_found.extend([item for item in excluded_items if item not in whole_list])
            if not_found:
                warnings.warn(
                    f"Items starting with ~: {not_found} have not been found and will be ignored"
                )
            subset = [item for item in whole_list if item not in excluded_items]

        else:
            if filter_items == "like":
                subset = [item for item in whole_list for name in subset if name in item]
            elif filter_items == "regex":
                subset = [item for item in whole_list for name in subset if re.search(name, item)]

        existing_items = np.isin(subset, whole_list)
        if not np.all(existing_items):
            raise KeyError(f"{np.array(subset)[~existing_items]} are not present")

    return subset

class BaseLabeller:
    """WIP."""
    from typing import Union
    def dim_coord_to_str(self, dim, coord_val, coord_idx):
        """WIP."""
        return f"{coord_val}"

    def sel_to_str(self, sel: dict, isel: dict):
        """WIP."""
        if not sel:
            return ""
        return ", ".join(
            [
                self.dim_coord_to_str(dim, v, i)
                for (dim, v), (_, i) in zip(sel.items(), isel.items())
            ]
        )

    def var_name_to_str(self, var_name: Union[str, None]):
        """WIP."""
        return var_name

    def var_pp_to_str(self, var_name, pp_var_name):
        """WIP."""
        var_name_str = self.var_name_to_str(var_name)
        pp_var_name_str = self.var_name_to_str(pp_var_name)
        return f"{var_name_str} / {pp_var_name_str}"

    def model_name_to_str(self, model_name):
        """WIP."""
        return model_name

    def make_label_vert(self, var_name: Union[str, None], sel: dict, isel: dict):
        """WIP."""
        var_name_str = self.var_name_to_str(var_name)
        sel_str = self.sel_to_str(sel, isel)
        if not sel_str:
            return var_name_str
        if var_name_str is None:
            return sel_str
        return f"{var_name_str}; {sel_str}"

    def make_label_flat(self, var_name: str, sel: dict, isel: dict):
        """WIP."""
        var_name_str = self.var_name_to_str(var_name)
        sel_str = self.sel_to_str(sel, isel)
        if not sel_str:
            return var_name_str
        if var_name is None:
            return sel_str
        return f"{var_name_str}[{sel_str}]"

    def make_pp_label(self, var_name, pp_var_name, sel, isel):
        """WIP."""
        names = self.var_pp_to_str(var_name, pp_var_name)
        return self.make_label_vert(names, sel, isel)

    def make_model_label(self, model_name, label):
        """WIP."""
        model_name_str = self.model_name_to_str(model_name)
        if model_name_str is None:
            return label
        return f"{model_name}: {label}"
    
def filter_plotters_list(plotters, plot_kind):
    """Cut list of plotters so that it is at most of length "plot.max_subplots"."""
    from rcparams import rcParams
    max_plots = rcParams["plot.max_subplots"]
    max_plots = len(plotters) if max_plots is None else max_plots
    if len(plotters) > max_plots:
        warnings.warn(
            "rcParams['plot.max_subplots'] ({max_plots}) is smaller than the number "
            "of variables to plot ({len_plotters}) in {plot_kind}, generating only "
            "{max_plots} plots".format(
                max_plots=max_plots, len_plotters=len(plotters), plot_kind=plot_kind
            ),
            UserWarning,
        )
        return plotters[:max_plots]
    return plotters

def xarray_sel_iter(data, var_names=None, combined=False, skip_dims=None, reverse_selections=False):
    """Convert xarray data to an iterator over variable names and selections.
    Iterates over each var_name and all of its coordinates, returning the variable
    names and selections that allow properly obtain the data from ``data`` as desired.
    Parameters
    ----------
    data : xarray.Dataset
        Posterior data in an xarray
    var_names : iterator of strings (optional)
        Should be a subset of data.data_vars. Defaults to all of them.
    combined : bool
        Whether to combine chains or leave them separate
    skip_dims : set
        dimensions to not iterate over
    reverse_selections : bool
        Whether to reverse selections before iterating.
    Returns
    -------
    Iterator of (var_name: str, selection: dict(str, any))
        The string is the variable name, the dictionary are coordinate names to values,.
        To get the values of the variable at these coordinates, do
        ``data[var_name].sel(**selection)``.
    """
    if skip_dims is None:
        skip_dims = set()

    if combined:
        skip_dims = skip_dims.union({"chain", "draw"})
    else:
        skip_dims.add("draw")

    if var_names is None:
        if isinstance(data, xr.Dataset):
            var_names = list(data.data_vars)
        elif isinstance(data, xr.DataArray):
            var_names = [data.name]
            data = {data.name: data}

    for var_name in var_names:
        if var_name in data:
            new_dims = _dims(data, var_name, skip_dims)
            vals = [purge_duplicates(data[var_name][dim].values) for dim in new_dims]
            dims = _zip_dims(new_dims, vals)
            idims = _zip_dims(new_dims, [range(len(v)) for v in vals])
            if reverse_selections:
                dims = reversed(dims)
                idims = reversed(idims)

            for selection, iselection in zip(dims, idims):
                yield var_name, selection, iselection

def xarray_var_iter(data, var_names=None, combined=False, skip_dims=None, reverse_selections=False):
    """Convert xarray data to an iterator over vectors.
    Iterates over each var_name and all of its coordinates, returning the 1d
    data.
    Parameters
    ----------
    data : xarray.Dataset
        Posterior data in an xarray
    var_names : iterator of strings (optional)
        Should be a subset of data.data_vars. Defaults to all of them.
    combined : bool
        Whether to combine chains or leave them separate
    skip_dims : set
        dimensions to not iterate over
    reverse_selections : bool
        Whether to reverse selections before iterating.
    Returns
    -------
    Iterator of (str, dict(str, any), np.array)
        The string is the variable name, the dictionary are coordinate names to values,
        and the array are the values of the variable at those coordinates.
    """
    data_to_sel = data
    if var_names is None and isinstance(data, xr.DataArray):
        data_to_sel = {data.name: data}

    for var_name, selection, iselection in xarray_sel_iter(
        data,
        var_names=var_names,
        combined=combined,
        skip_dims=skip_dims,
        reverse_selections=reverse_selections,
    ):
        yield var_name, selection, iselection, data_to_sel[var_name].sel(**selection).values

def _dims(data, var_name, skip_dims):
    return [dim for dim in data[var_name].dims if dim not in skip_dims]


def _zip_dims(new_dims, vals):
    from itertools import product, tee
    return [{k: v for k, v in zip(new_dims, prod)} for prod in product(*vals)]


def default_grid(n_items, grid=None, max_cols=4, min_cols=3):  # noqa: D202
    """Make a grid for subplots.
    Tries to get as close to sqrt(n_items) x sqrt(n_items) as it can,
    but allows for custom logic
    Parameters
    ----------
    n_items : int
        Number of panels required
    grid : tuple
        Number of rows and columns
    max_cols : int
        Maximum number of columns, inclusive
    min_cols : int
        Minimum number of columns, inclusive
    Returns
    -------
    (int, int)
        Rows and columns, so that rows * columns >= n_items
    """
    from rcparams import rcParams
    if grid is None:

        def in_bounds(val):
            return np.clip(val, min_cols, max_cols)

        if n_items <= max_cols:
            return 1, n_items
        ideal = in_bounds(round(n_items ** 0.5))

        for offset in (0, 1, -1, 2, -2):
            cols = in_bounds(ideal + offset)
            rows, extra = divmod(n_items, cols)
            if extra == 0:
                return rows, cols
        return n_items // ideal + 1, ideal
    else:
        rows, cols = grid
        if rows * cols < n_items:
            raise ValueError("The number of rows times columns is less than the number of subplots")
        if (rows * cols) - n_items >= cols:
            warnings.warn("The number of rows times columns is larger than necessary")
        return rows, cols
    

def get_plotting_function(plot_name, plot_module, backend):
    """Return plotting function for correct backend."""
    import importlib
    from numbers import Integral
    
    _backend = {
        "mpl": "matplotlib",
        "bokeh": "bokeh",
        "matplotlib": "matplotlib",
    }
    
    if backend is None:
        backend = rcParams["plot.backend"]
    backend = backend.lower()

    try:
        backend = _backend[backend]
    except KeyError as err:
        raise KeyError(
            "Backend {} is not implemented. Try backend in {}".format(
                backend, set(_backend.values())
            )
        ) from err

    if backend == "bokeh":
        try:
            import bokeh

            assert packaging.version.parse(bokeh.__version__) >= packaging.version.parse("1.4.0")

        except (ImportError, AssertionError) as err:
            raise ImportError(
                "'bokeh' backend needs Bokeh (1.4.0+) installed." " Please upgrade or install"
            ) from err

    # Perform import of plotting method
    # TODO: Convert module import to top level for all plots
    module = importlib.import_module(f"arviz.plots.backends.{backend}.{plot_module}")

    plotting_method = getattr(module, plot_name)

    return plotting_method
import pymc3 as pm
import arviz as az
import xarray as xr

from generate_data import generate_data

n = 70
Years_indiv, Mean_RT_comp_Indiv, Mean_RT_incomp_Indiv = generate_data(7, n)

dims = {"y_obs_comp": ["subject"], "y_obs_incomp": ["subject"]}
with pm.Model() as model_pow:
    α_c = pm.HalfCauchy('α_c', 10)
    α_i = pm.HalfCauchy('α_i', 10)
    β = pm.Normal('β', 1, 2)
    γ_c = pm.Normal('γ_c', Mean_RT_comp_Indiv.mean(), .5)
    γ_i = pm.Normal('γ_i', Mean_RT_incomp_Indiv.mean(), .5)
    σ = pm.HalfNormal('σ', .2)
    μ_c = α_c*Years_indiv**-β + γ_c
    μ_i = α_i*Years_indiv**-β + γ_i
    y_obs_comp = pm.Normal('y_obs_comp', μ_c, σ, observed=Mean_RT_comp_Indiv)
    y_obs_incomp = pm.Normal('y_obs_incomp', μ_i, σ, observed=Mean_RT_incomp_Indiv)

    trace_pow = pm.sample(2000, chains=4, cores=4, tune=2000, target_accept=.9)
    idata_pow = az.from_pymc3(trace_pow, dims=dims)

with pm.Model() as model_exp:
    α_c = pm.HalfCauchy('α_c', 5)
    α_i = pm.HalfCauchy('α_i', 5)
    β = pm.Normal('β', 1, 1)
    γ_c = pm.Normal('γ_c', Mean_RT_comp_Indiv.mean(), .5)
    γ_i = pm.Normal('γ_i', Mean_RT_incomp_Indiv.mean(), .5)
    σ = pm.HalfNormal('σ', .2)
    μ_c = α_c*pm.math.exp(-β*Years_indiv) + γ_c
    μ_i = α_i*pm.math.exp(-β*Years_indiv) + γ_i
    y_obs_comp = pm.Normal('y_obs_comp', μ_c, σ, observed=Mean_RT_comp_Indiv)
    y_obs_incomp = pm.Normal('y_obs_incomp', μ_i, σ, observed=Mean_RT_incomp_Indiv)

    trace_exp = pm.sample(2000, chains=4, cores=4, tune=2000, target_accept=.9)
    idata_exp = az.from_pymc3(trace_exp, dims=dims)

print("\n\n\n###    stored pointwise log likelihood data    ###\n")
print(idata_exp.log_likelihood)

# cross validation
log_lik_exp = idata_exp.log_likelihood
log_lik_pow = idata_pow.log_likelihood

print("\n\nLeave one *observation* out cross validation (whole model)")
condition_dim = xr.DataArray(["compatible", "incompatible"], name="condition")
idata_exp.sample_stats["log_likelihood"] = xr.concat((log_lik_exp.y_obs_comp, log_lik_exp.y_obs_incomp), dim=condition_dim)
idata_pow.sample_stats["log_likelihood"] = xr.concat((log_lik_pow.y_obs_comp, log_lik_pow.y_obs_incomp), dim=condition_dim)
print(az.loo(idata_exp), "\n")
print(az.compare({"exp": idata_exp, "pow": idata_pow}))

print("\n\nLeave one *subject* out cross validation (whole model)")
idata_exp.sample_stats["log_likelihood"] = log_lik_exp.to_array().sum("variable")
idata_pow.sample_stats["log_likelihood"] = log_lik_pow.to_array().sum("variable")
print(az.loo(idata_exp), "\n")
print(az.compare({"exp": idata_exp, "pow": idata_pow}))

print("\n\nLeave one observation out cross validation (y_obs_comp only)")
idata_exp.sample_stats["log_likelihood"] = log_lik_exp.y_obs_comp
idata_pow.sample_stats["log_likelihood"] = log_lik_pow.y_obs_comp
print(az.loo(idata_exp), "\n")
print(az.compare({"exp": idata_exp, "pow": idata_pow}))

print("\n\nLeave one observation out cross validation (y_obs_incomp only)")
idata_exp.sample_stats["log_likelihood"] = log_lik_exp.y_obs_incomp
idata_pow.sample_stats["log_likelihood"] = log_lik_pow.y_obs_incomp
print(az.loo(idata_exp), "\n")
print(az.compare({"exp": idata_exp, "pow": idata_pow}))

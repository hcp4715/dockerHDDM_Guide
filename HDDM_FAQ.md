# FAQ about HDDM
HDDM has a user forum, which has a lot of valuable discussions. Members of developer team are also active to answer questions. However, the questions and answers are not well archived, some questions persist or re-occur, and answers to similar questions are scattered in different posts. Here I tried to collect the useful Q & A to make it easier for futuer users.


## Q1: Installation (To-be-done)
There are so many questions about errors in installing HDDM

### Q1.1 HDDM 0.9.* with Windows 10
Qs:
As:

### Q1.2 HDDM 0.9.* with MacOS
Qs:
As:

### Q1.3 HDDM 0.8.0 with Windows 10
Qs:
As:


### Q1.4 HDDM 0.8.0 with MacOS
Qs:
As:

## Q2: Between-subject effects
### Description of the question: 
How to model the effect of individual differences or between-subject effect in HDDM.

#### Variation 1: 
Modelling the effect of a continuous between-subject factor (e.g., scale scores).
#### Variation 2:
Modelling group effect (e.g.,  three groups of participants).

### Posts and scripts
Several posts had discussed this issue. 
Jan 2017 to Dec 2020: https://groups.google.com/g/hddm-users/c/C96uz2_xFl8
May 2017 to Aug 2020: https://groups.google.com/g/hddm-users/c/eJ3vsuR4rRE/m/ZEUZQP4kBAAJ, which focused on between and within-subject effect.

Similar question re-appeared at April 2020 https://groups.google.com/g/hddm-users/c/JWDYbE85XTU/m/RkPBgTLSEQAJ, May 2020 https://groups.google.com/g/hddm-users/c/F65i6vWjsAM/m/-HOsL7SLBwAJ.

Answer from Michael J Frank, with example code: https://groups.google.com/group/hddm-users/attach/7d8208ab9c71a/hddm_bwsubs_simulation.py?part=0.1

Another example code: https://github.com/hcp4715/SalientGoodSelf/blob/master/HDDM/hddm_bwsubs_interact_simulation.ipynb

Also example from Mads Lund Pedersen: https://groups.google.com/group/hddm-users/attach/424fe40194564/GoNoGoRegressionTest.html?part=0.1.1

### Solutions

General solution: The core of this issue is how to model between-subject effect of individuals differences using hierarchical model within the context of DDM. Thus, the first thing need to know is that this issue can only be addressed by `HDDMregressor(.)`. Then comes the question how to write the code. In those discussions, Michael and Mads offered their example code. The final answer is to simulating and make sure that you can recovery the parameter.

The long answer from Michael: https://groups.google.com/g/hddm-users/c/C96uz2_xFl8/m/GWhXFZtHAwAJ

We've been interested to add capability for estimating regression coefficients for between subject effects, e.g. to see if we can estimate within HDDM the impact of a continuous measure x, where x can be age, IQ, etc on DDM params.  The upshot is that the answer is yes, at least in theory:  I ran some simulations and could accurately recover the coefficients. including when there are additional within-subject condition effects, which are also accurately recovered in the same model.  (I reiterate a point from a previous post though, based on this article, that it is actually fine to fit the model without x as a regressor at all, and then to correlate the individual subject intercepts with the between subjects factor after the fact  -- but that involves a classical correlation test whereas the regression approach here estimates the effect and its uncertainty within the bayesian parameter estimation itself). 

Here are some issues to consider when doing this (followed by code, modified from Nate's earlier post) - we will also add to the hddm docs.

1. a central issue that came up (and I believe was one factor driving the error Nate was getting) is that when estimating parameters, they should still be informed by, and in the range of, the priors. The intercept parameters for the main DDM parameters are informed by empirical priors (see the supplement of the 2013 paper), and so my earlier recommendation to try a ~ 0 +X was misguided because it would enforce the intercept to be 0 which has very low prior density for a  (this is not a problem for v ~ 0 +X, given that 0 is in the range of priors for drift, but it turns out there is no need to enforce  intercepts to be 0 after all -- which is good because one would usually like to still estimate indiv subject parameters that reflect variability beyond that explained by the single x factor).   

2. Relatedly, a key recommendation is to first z-score (or at least mean-center) the between subjects factor x and to then estimate e.g., a ~ 1 +X. This way every subject still has an intercept drawn from an overall group distribution, with priors of that distribution centered at empirical priors, but then we can also estimate the degree to which this intercept is modified up or down by the (z-scored / mean-centered) between-subjects factor.  

I ran generate and recover simulations, code below, and confirmed that the beta coefficient on the x factor is recovered quite well at least for the various cases I tried. (In the generative data, the intercepts should also be within the range of priors for this to work reliably (e.g. a_int > 0), which makes sense).   I also confirmed that this works for both threshold and drift (and I image t should be fine too), and when allowing both to vary freely during fitting it correctly estimated the magnitude of the specific factor that varied in generative data, and pinned the other one at ~zero). 


* Note one limitation in the implementation is that while we allow x to affect the mean of the group distribution on the intercept, we assume the variance of that distribution is constant across levels of x - ie. there is no way currently to allow a_std to vary with x. But that's not such a terrible limitation (it just means that a_std for the overall group parameters will need to be large enough to accommodate the most variable group - but it should still go *down* relative to not allowing x to influence the mean at all).  

anyway here is example code

```
## Generate data

beta_a = 0.1      #between subjects scaling factor - adjust this and should be able to recover its true value
a_int = 1 # set intercept within range of empirical priors 
v_int = 0.3
x_range = range(11)    # set values of between subject measures, here from 0 to 10
trials_per_level=100    
subjs_per_bin = 10

data_group = pd.DataFrame()     #empty df to append to  

for x in x_range:

  xx=(x-mean(x_range))/std(x_range) # z-score the x factor
  a = a_int+ beta_a*xx #  indiv subj param values that are centered on intercept but deviate from it up or down by z-scored x
 # v = v_int+ beta_a*xx  # can also do for drift, here using same beta coeff
   
# parvec = {'v':.3, 'a':a, 't':.3, 'sv':0, 'z':.5, 'sz':0, 'st':0}
# parvec2 = {'v':.3, 'a':a+.5, 't':.3, 'sv':0, 'z':.5, 'sz':0, 'st':0}
  parvec = {'v':.3, 'a':a, 't':.3}   # set a to value set by regression, here v is set to constant

# note that for subjs_per_bin > 1, these are just the mean values of the parameters; indiv subjs within bin are sampled from distributions with the given means, but can still differ within bin around those means. not including sv, sz, st in the statement ensures those are actually 0.
 
 data_a, params_a = hddm.generate.gen_rand_data({'level1': parvec}, size=trials_per_level, subjs=subjs_per_bin)
 
  # can also do with two levels of within-subj conditions
  #data_a, params_a = hddm.generate.gen_rand_data({'level1': parvec,'level2': parvec2}, size=trials_per_level, subjs=subjs_per_bin)

 data_a['x'] = Series(xx*np.ones((len(data_a))), index=data_a.index) # store the (z-scored) between subjects factor in the data frame, same value for every row for each subject in the bin

 data_a['subj_idx'] = Series(x*subjs_per_bin+data_a['subj_idx']*np.ones((len(data_a))), index=data_a.index) # store the correct subj_idx when iterating over multiple subjs per bin
  
  #concatenate data_a with group data
  data_a_df = pd.DataFrame(data=[data_a])
  data_group = data_group.append([data_a], ignore_index=True)

## Recover

a_reg = {'model': 'a ~ 1+x', 'link_func': lambda x: x}
#a_reg_within = {'model': 'a ~ 1+x + C(condition)', 'link_func': lambda x: x}
# for including and estimating within subject effects of  condition

v_reg = {'model': 'v ~ 1+x', 'link_func': lambda x: x}
reg_comb = [a_reg, v_reg]
#m_reg = hddm.HDDMRegressor(data_group, reg_comb, group_only_regressors=['true']) 

m_reg = hddm.HDDMRegressor(data_group, a_reg, group_only_regressors=['true'])
m_reg.find_starting_values()
m_reg.sample(1500, burn = 200)

m_reg.print_stats() # check values of reg coefficients against the generated ones

```

Note also that in addition to checking the regression coefficient, if the recovery works, then all of the variance due to X should be soaked up by the regression coefficient, and there should be no residual correlation between the individual estimated subject intercepts and x. 

```
## check for residual correlation with x 
p =[]
pp=[] 
from scipy import stats
for i in range(0,(1+max(x_range))*subjs_per_bin -1):
    a='a_Intercept_subj.'
    a+=str(i)
    a+='.0'
    xx=i//subjs_per_bin
    p1=m_reg.nodes_db.node[a] 
    p.append(p1.trace().mean()) 
    pp.append(xx)
     
scatter(pp,p)
stats.pearsonr(pp,p) # should be zero correlation if entirely accounted for by x regressor - this correlation should instead be positive if x is removed from the model fit

```

## Q3: Stimulus-coding, Response-coding, vs. Accuracy-Coding
### 

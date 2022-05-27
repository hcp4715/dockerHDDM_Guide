'''
Simulation of between-subjects regressor effects on HDDM parameters

The goal of the script is to verify that effects of between-subjects regressor on 
HDDM parameters can be accurately estimated, including when there are also within-subject effects.

Values of a between-subject regressor on a or v are simulated by creating multiple subject datasets at increasing
values of the regressor.  

Created on Feb 8, 2017

'''
import hddm
from numpy import mean, std
import numpy as np         
from pandas import Series
import pandas as pd
import os as os
import matplotlib.pyplot as plt

os.chdir('/storage/home/mnh5174')

## Generate data

beta_a = 0.4  # between subjects scaling factor - adjust this and should be able to recover its true value
a_int = 1  # set intercept within range of empirical priors 
v_int = 0.3
x_range = range(11)  # set values of between subject measures, here from 0 to 10
trials_per_level = 200    
subjs_per_bin = 10

data_group = pd.DataFrame()  # empty df to append to  

for x in x_range:
    xx = (x - mean(x_range)) / std(x_range)  # z-score the x factor
    a = a_int + beta_a * xx  #  indiv subj param values that are centered on intercept but deviate from it up or down by z-scored x
    # v = v_int+ beta_a*xx  # can also do for drift, here using same beta coeff
    
    # parvec = {'v':.3, 'a':a, 't':.3, 'sv':0, 'z':.5, 'sz':0, 'st':0}
    # parvec2 = {'v':.3, 'a':a+.5, 't':.3, 'sv':0, 'z':.5, 'sz':0, 'st':0}
    parvec = {'v':.3, 'a':a, 't':.3}  # set a to value set by regression, here v is set to constant

    # note that for subjs_per_bin > 1, these are just the mean values of the parameters; indiv subjs within bin are sampled from distributions with the given means, but can still differ within bin around those means. 
    #not including sv, sz, st in the statement ensures those are actually 0.

    data_a, params_a = hddm.generate.gen_rand_data({'level1': parvec}, size=trials_per_level, subjs=subjs_per_bin)
    
    # can also do with two levels of within-subj conditions
    # data_a, params_a = hddm.generate.gen_rand_data({'level1': parvec,'level2': parvec2}, size=trials_per_level, subjs=subjs_per_bin)

    data_a['z_x'] = Series(xx * np.ones((len(data_a))), index=data_a.index)  # store the (z-scored) between subjects factor in the data frame, same value for every row for each subject in the bin
    data_a['x'] = Series(x * np.ones((len(data_a))), index=data_a.index)  # store the (z-scored) between subjects factor in the data frame, same value for every row for each subject in the bin
    data_a['a_population'] = Series(a * np.ones((len(data_a))), index=data_a.index)  # store the (z-scored) between subjects factor in the data frame, same value for every row for each subject in the bin
    data_a['subj_idx'] = Series(x * subjs_per_bin + data_a['subj_idx'] * np.ones((len(data_a))), index=data_a.index)  # store the correct subj_idx when iterating over multiple subjs per bin
     
    # concatenate data_a with group data
    data_a_df = pd.DataFrame(data=[data_a])
    data_group = data_group.append([data_a], ignore_index=True)

#write original simulated data to file
data_group.to_csv('data_group.csv')

## Recover parameters

a_reg = {'model': 'a ~ 1 + z_x', 'link_func': lambda x: x}
# a_reg_within = {'model': 'a ~ 1+x + C(condition)', 'link_func': lambda x: x}
# for including and estimating within subject effects of  condition

v_reg = {'model': 'v ~ 1 + z_x', 'link_func': lambda x: x}
reg_comb = [a_reg, v_reg]
# m_reg = hddm.HDDMRegressor(data_group, reg_comb, group_only_regressors=['true']) 

m_reg = hddm.HDDMRegressor(data_group, a_reg, group_only_regressors=['true'])
m_reg.find_starting_values()
m_reg.sample(3000, burn=500, dbname='a_bwsubs_t200.db', db='pickle')
m_reg.save('a_bwsubs_model_t200')

m_reg.print_stats()  # check values of reg coefficients against the generated ones

#load from file and examine recovery
m_reg = hddm.load('a_bwsubs_model_t200')
data_group = pd.read_csv('data_group.csv')

#look at correlation of recovered parameter with original
subjdf = data_group.groupby('subj_idx').first().reset_index()

## check for residual correlation with x 
a_int_recovered =[]

#obtain mean a intercept parameter for subjects
from scipy import stats
for i in range(0,(1+max(x_range))*subjs_per_bin):
    a='a_Intercept_subj.'
    a+=str(i)
    a+='.0'
    p1=m_reg.nodes_db.node[a] 
    a_int_recovered.append(p1.trace().mean())
    
#obtain mean a regression weight for z_x
a_x_recovered = m_reg.nodes_db.node['a_z_x'].trace().mean()

#compute predicted a parameter as a function of subject intercept and between-subjects regressor
subjdf.apred = a_int_recovered + a_x_recovered * subjdf.z_x

#correlation of recovered a with population a. r = .97 here: good!
fig = plt.figure()
fig.set_size_inches(5, 4)
plt.scatter(subjdf.apred,subjdf.a_population) #predicted versus observed a
plt.xlabel('recovered a')
plt.ylabel('simulated a')
plt.savefig('correlation of simulated and recovered a params.png', dpi=300, format='png')
print('Pearson correlation between a_x and x') 
print(stats.pearsonr(subjdf.apred,subjdf.a_population)) # correlation between predicted a value and population a value


#correlation of subject intercept with between-subjects regressor
#should be zero correlation if entirely accounted for by x regressor - this correlation should instead be positive if x is removed from the model fit
fig = plt.figure()
fig.set_size_inches(5, 4)
plt.scatter(subjdf.x,a_int_recovered)
plt.xlabel('between subjs regressor x')
plt.ylabel('recovered subject a intercept')
plt.show()
plt.savefig('residual correlation between subj intercept and x.png', dpi=300, format='png')
print('Pearson correlation between a_x and x') 
print(stats.pearsonr(a_int_recovered,subjdf.x))

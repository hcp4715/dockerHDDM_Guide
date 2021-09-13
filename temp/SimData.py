def SimData(df_key, n_subj = 14):
    """
    simulate data based on model specification
    """
    
    import hddm
    import kabuki
    import numpy as np
    import pandas as pd
    from patsy import dmatrix
    
    full_colnames = ['subj_idx', 'conf', 'dbs', 'rt', 'response', 'theta', 'v', 'a', 't',
                    'z', 'sv', 'st', 'sz']
    
    if df_key == "sim_df1":
        n_trials_cond = 320/1

        params_m1 = {'v':2., 'a':1.5, 't':.4, 'sv':0, 'z':.5, 'sz':0, 'st':0}

        sim_data, sim_params_m1 = hddm.generate.gen_rand_data(params_m1,
                                                                    size=n_trials_cond,
                                                                    subjs=n_subj)

        # add conf and dbs
        # sim_data.rename(columns = {'condition': 'conf'}, inplace = True)
        sim_data['conf']  = np.tile(["HC", "HC", "LC", "LC"], int(len(sim_data)/4))
        sim_data['dbs']   = np.tile([0, 1, 0, 1], int(len(sim_data)/4))
        sim_data['theta'] = np.random.normal(0, 1, len(sim_data))
        sim_data = sim_data[['subj_idx', 'conf', 'dbs', 'rt', 'response', 'theta']]

        sim_data_full = sim_data.copy()
        sim_data_full['v'] = None
        sim_data_full['a'] = None
        sim_data_full['t'] = None
        sim_data_full['z'] = None
        sim_data_full['sv'] = None
        sim_data_full['st'] = None
        sim_data_full['sz'] = None

        for subj in range(n_subj):
            sim_data_full['v'].loc[(sim_data_full['subj_idx'] == subj)] = sim_params_m1[subj]['v']
            sim_data_full['a'].loc[(sim_data_full['subj_idx'] == subj)] = sim_params_m1[subj]['a']
            sim_data_full['t'].loc[(sim_data_full['subj_idx'] == subj)] = sim_params_m1[subj]['t']
            sim_data_full['z'].loc[(sim_data_full['subj_idx'] == subj)] = sim_params_m1[subj]['z']
            sim_data_full['sv'].loc[(sim_data_full['subj_idx'] == subj)] = sim_params_m1[subj]['sv']
            sim_data_full['st'].loc[(sim_data_full['subj_idx'] == subj)] = sim_params_m1[subj]['st']
            sim_data_full['sz'].loc[(sim_data_full['subj_idx'] == subj)] = sim_params_m1[subj]['sz']
            
    elif df_key == "sim_df2":
        n_trials_cond = int(320/2)

        params_m2 = {'HC': {'v':2.,  'a':1.5, 't':.4, 'sv':0, 'z':.5, 'sz':0, 'st':0},
                     'LC' : {'v':3.2, 'a':1.5, 't':.4, 'sv':0, 'z':.5, 'sz':0, 'st':0}}

        sim_data, sim_params_m2 = hddm.generate.gen_rand_data(params_m2,
                                                              size=n_trials_cond,
                                                              subjs=n_subj)
        # add conf and dbs
        sim_data.rename(columns = {'condition': 'conf'}, inplace = True)
        sim_data['dbs'] = np.tile([0,1], int(len(sim_data)/2))
        sim_data['theta'] = np.random.normal(0, 1, len(sim_data))
        sim_data = sim_data[['subj_idx', 'conf', 'dbs', 'rt', 'response', 'theta']]

        sim_data_full = sim_data.copy()
        sim_data_full['v'] = None
        sim_data_full['a'] = None
        sim_data_full['t'] = None
        sim_data_full['z'] = None
        sim_data_full['sv'] = None
        sim_data_full['st'] = None
        sim_data_full['sz'] = None

        for subj in range(n_subj):
            sim_data_full['v'].loc[(sim_data_full['conf'] == "HC") & (sim_data_full['subj_idx'] == subj)] = sim_params_m2['HC'][subj]['v']
            sim_data_full['v'].loc[(sim_data_full['conf'] == "LC") & (sim_data_full['subj_idx'] == subj)] = sim_params_m2['LC'][subj]['v']
            sim_data_full['a'].loc[(sim_data_full['conf'] == "HC") & (sim_data_full['subj_idx'] == subj)] = sim_params_m2['HC'][subj]['a']
            sim_data_full['a'].loc[(sim_data_full['conf'] == "LC") & (sim_data_full['subj_idx'] == subj)] = sim_params_m2['LC'][subj]['a']
            sim_data_full['t'].loc[(sim_data_full['conf'] == "HC") & (sim_data_full['subj_idx'] == subj)] = sim_params_m2['HC'][subj]['t']
            sim_data_full['t'].loc[(sim_data_full['conf'] == "LC") & (sim_data_full['subj_idx'] == subj)] = sim_params_m2['LC'][subj]['t']
            sim_data_full['z'].loc[(sim_data_full['conf'] == "HC") & (sim_data_full['subj_idx'] == subj)] = sim_params_m2['HC'][subj]['z']
            sim_data_full['z'].loc[(sim_data_full['conf'] == "LC") & (sim_data_full['subj_idx'] == subj)] = sim_params_m2['LC'][subj]['z']
            sim_data_full['sv'].loc[(sim_data_full['conf'] == "HC") & (sim_data_full['subj_idx'] == subj)] = sim_params_m2['HC'][subj]['sv']
            sim_data_full['sv'].loc[(sim_data_full['conf'] == "LC") & (sim_data_full['subj_idx'] == subj)] = sim_params_m2['LC'][subj]['sv']
            sim_data_full['st'].loc[(sim_data_full['conf'] == "HC") & (sim_data_full['subj_idx'] == subj)] = sim_params_m2['HC'][subj]['st']
            sim_data_full['st'].loc[(sim_data_full['conf'] == "LC") & (sim_data_full['subj_idx'] == subj)] = sim_params_m2['LC'][subj]['st']
            sim_data_full['sz'].loc[(sim_data_full['conf'] == "HC") & (sim_data_full['subj_idx'] == subj)] = sim_params_m2['HC'][subj]['sz']
            sim_data_full['sz'].loc[(sim_data_full['conf'] == "LC") & (sim_data_full['subj_idx'] == subj)] = sim_params_m2['LC'][subj]['sz']

        sim_data_full = sim_data_full[full_colnames]
        
    elif df_key == "sim_df4":
        n_trials_cond = int(320/2)

        # hyper parameters of the linear regresion
        # need to be reconsidered in the future

        intercept_mu = 2
        intercept_sigma = 1

        slope_mu = 1.2
        slope_sigma = 0.6  

        sim_data = []
        sim_params_m4 = []

        for subj in range(n_subj):
            v_high = np.random.normal(intercept_mu, intercept_sigma)
            slope_tmp = np.random.normal(slope_mu, slope_sigma)
            v_low = v_high + slope_tmp

            params_m4_tmp = {'HC': {'v':v_high,  'a':1.5, 't':.4, 'sv':0, 'z':.5, 'sz':0, 'st':0},
                             'LC' : {'v':v_low, 'a':1.5, 't':.4, 'sv':0, 'z':.5, 'sz':0, 'st':0}}

            params_m4_tmp['HC']['a'] = params_m4_tmp['LC']['a'] = np.random.normal(1.5, 0.1)
            params_m4_tmp['HC']['t'] = params_m4_tmp['LC']['t'] = np.random.normal(0.4, 0.1)
            params_m4_tmp['HC']['z'] = params_m4_tmp['LC']['z'] = np.random.normal(0.5, 0.1)
            params_m4_tmp['HC']['sv'] = params_m4_tmp['LC']['sv'] = np.abs(np.random.normal(0., 0.05))
            params_m4_tmp['HC']['st'] = params_m4_tmp['LC']['st'] = np.abs(np.random.normal(0., 0.05))
            params_m4_tmp['HC']['sz'] = params_m4_tmp['LC']['sz'] = np.abs(np.random.normal(0., 0.05))

            sim_data_tmp, sim_params_m4_tmp = hddm.generate.gen_rand_data(params_m4_tmp,
                                                                                size=n_trials_cond,
                                                                                subjs=1)
            # params_m4.append(params_m4_tmp)
            sim_data_tmp.rename(columns = {'condition': 'conf'}, inplace = True)
            sim_data_tmp['dbs'] = np.tile([0,1], n_trials_cond)
            sim_data_tmp['theta'] = np.random.normal(0, 1, len(sim_data_tmp))

            sim_data_tmp['v'] = sim_params_m4_tmp['HC']['v']
            sim_data_tmp['v'].loc[sim_data_tmp['conf'] == 'LC'] = sim_params_m4_tmp['LC']['v']
            sim_data_tmp['a'] = sim_params_m4_tmp['HC']['a']
            sim_data_tmp['t'] = sim_params_m4_tmp['HC']['t']
            sim_data_tmp['z'] = sim_params_m4_tmp['HC']['z']
            sim_data_tmp['sv'] = sim_params_m4_tmp['HC']['sv']
            sim_data_tmp['st'] = sim_params_m4_tmp['HC']['st']
            sim_data_tmp['sz'] = sim_params_m4_tmp['HC']['sz']

            sim_data.append(sim_data_tmp)
            sim_params_m4.append(sim_params_m4_tmp)

        sim_data_full = pd.concat(sim_data, names=['subj_idx'], keys=list(range(len(sim_data))))
        sim_data_full.drop(['subj_idx'], axis=1, inplace=True)
        sim_data_full.reset_index(inplace=True) 
        sim_data_full.drop(['level_1'], axis=1, inplace=True)
        # sim_data.rename(columns = {'level_1':'trial'}, inplace = True)
        sim_data_full = sim_data_full[full_colnames]
        sim_data = sim_data_full[['subj_idx', 'conf', 'dbs', 'rt', 'response', 'theta']].copy()
        
    elif df_key == "sim_df5":
        
        n_trials_cond = int(320/2)

        sim_data = []
        for subj in range(n_subj):
            ### for dbd ON:
            theta_hc = np.random.normal(-0.03, 1, n_trials_cond)
            tmp_df0 = pd.DataFrame(columns=['subj_idx','conf','dbs','theta'])
            tmp_df0['theta'] = theta_hc
            tmp_df0['subj_idx'] = subj
            tmp_df0['conf'] = 'HC'
            tmp_df0['dbs'] = np.repeat([0,1], n_trials_cond/2, axis=0)

            theta_lc  = np.random.normal(0.03, 1, n_trials_cond)
            tmp_df1 = pd.DataFrame(columns=['subj_idx','conf','dbs','theta'])
            tmp_df1['theta'] = theta_lc
            tmp_df1['subj_idx'] = subj
            tmp_df1['conf'] = 'LC'
            tmp_df1['dbs'] = np.repeat([0,1], n_trials_cond/2, axis=0)

            tmp_df_ls = [tmp_df0, tmp_df1]
            tmp_df = pd.concat(tmp_df_ls)
            tmp_df = tmp_df.sample(frac=1).reset_index(drop=True)

            # generate design matrix for a_on

            dm_tmp = pd.DataFrame(dmatrix("theta:C(conf, Treatment('LC'))", tmp_df))

            intercept_tmp = np.random.normal(1.5, 0.3) #### Used normal distribution again
            slope_hc_tmp = np.random.normal(0.08, 0.02)
            slope_lc_tmp = np.random.normal(-0.02, 0.02)
            coef_tmp = [intercept_tmp, slope_hc_tmp, slope_lc_tmp]
            coef_tmp = pd.DataFrame(coef_tmp)

            tmp_df['a'] = np.dot(dm_tmp, coef_tmp)

            # get drift rate v
            v_high = np.random.normal(2,  0.1, int(len(tmp_df)/2))
            v_low = np.random.normal(3.2, 0.1, int(len(tmp_df)/2))

            tmp_df['v'] = None
            tmp_df['v'].loc[tmp_df['conf']=='HC'] = v_high
            tmp_df['v'].loc[tmp_df['conf']=='LC'] = v_low

            # add noise to other parameters
            tmp_df['t'] = np.random.normal(0.4, 0.1, len(tmp_df))
            tmp_df['z'] = np.random.normal(0.5, 0.1, len(tmp_df))
            tmp_df['sv'] = np.abs(np.random.normal(0, 0.05, len(tmp_df)))
            tmp_df['sz'] = np.abs(np.random.normal(0, 0.05, len(tmp_df)))
            tmp_df['st'] = np.abs(np.random.normal(0, 0.05, len(tmp_df)))

            tmp_df['rt'] = None
            tmp_df['response'] = None

            for trial in range(len(tmp_df)):
                params_tmp = {'v': tmp_df['v'].iloc[trial],
                              'a': tmp_df['a'].iloc[trial],
                              't': tmp_df['t'].iloc[trial],
                              'sv': tmp_df['sv'].iloc[trial],
                              'z': tmp_df['z'].iloc[trial],
                              'sz': tmp_df['sz'].iloc[trial],
                              'st':tmp_df['st'].iloc[trial]
                             }

                sim_tmp, _ = hddm.generate.gen_rand_data(params_tmp,
                                                      size=1,
                                                      subjs=1)
                tmp_df['rt'].iloc[trial] = sim_tmp['rt'].iloc[0].copy()
                tmp_df['response'].iloc[trial] = sim_tmp['response'].iloc[0].copy()    

            sim_data.append(tmp_df)

        sim_data_full = pd.concat(sim_data, ignore_index=True)

        # convert python object to float
        sim_data_full['rt'] = sim_data_full['rt'].astype(float)
        sim_data_full['response'] = sim_data_full['response'].astype(float)

        sim_data = sim_data_full.drop(['a', 'v'], axis=1).copy()
        sim_data_full = sim_data_full[full_colnames]
        sim_data = sim_data[['subj_idx', 'conf', 'dbs', 'rt', 'response', 'theta']]
        
    elif df_key == "sim_df7":
        n_trials_cond = int(320/4)

        sim_data = []
        for subj in range(n_subj):
            theta_on_hc  = np.random.normal(-0.03, 1, n_trials_cond)
            tmp_df0 = pd.DataFrame(columns=['subj_idx','conf','dbs','theta'])
            tmp_df0['theta'] = theta_on_hc
            tmp_df0['subj_idx'] = subj
            tmp_df0['conf'] = 'HC'
            tmp_df0['dbs'] = 1

            theta_off_hc = np.random.normal( 0.03, 1, n_trials_cond)
            tmp_df1 = pd.DataFrame(columns=['subj_idx','conf','dbs','theta'])
            tmp_df1['theta'] = theta_off_hc
            tmp_df1['subj_idx'] = subj
            tmp_df1['conf'] = 'HC'
            tmp_df1['dbs'] = 0

            theta_on_lc  = np.random.normal( 0.03, 1, n_trials_cond)
            tmp_df2 = pd.DataFrame(columns=['subj_idx','conf','dbs','theta'])
            tmp_df2['theta'] = theta_on_lc
            tmp_df2['subj_idx'] = subj
            tmp_df2['conf'] = 'LC'
            tmp_df2['dbs'] = 1

            theta_off_lc = np.random.normal(-0.03, 1, n_trials_cond)
            tmp_df3 = pd.DataFrame(columns=['subj_idx','conf','dbs','theta'])
            tmp_df3['theta'] = theta_off_lc
            tmp_df3['subj_idx'] = subj
            tmp_df3['conf'] = 'LC'
            tmp_df3['dbs'] = 0

            tmp_df_ls = [tmp_df0, tmp_df1, tmp_df2, tmp_df3]
            tmp_df = pd.concat(tmp_df_ls)
            tmp_df = tmp_df.sample(frac=1).reset_index(drop=True)


            # generate design matrix for a

            dm_tmp = pd.DataFrame(dmatrix("theta:C(conf, Treatment('LC')):C(dbs, Treatment('0'))", tmp_df))

            intercept_tmp = np.random.normal(1.5, 0.3) #### Used normal distribution again
            slope_on_hc_tmp = np.random.normal(0.08, 0.02)
            slope_off_hc_tmp = np.random.normal(-0.07, 0.02)
            slope_on_lc_tmp = np.random.normal(0.02, 0.02)
            slope_off_lc_tmp = np.random.normal(-0.02, 0.02)

            coef_tmp = [intercept_tmp, slope_on_hc_tmp, slope_off_hc_tmp, slope_on_lc_tmp, slope_off_lc_tmp]
            coef_tmp = pd.DataFrame(coef_tmp)

            tmp_df['a'] = np.dot(dm_tmp, coef_tmp)

            # get drift rate v

            v_intercept_mu = 2
            v_intercept_sigma = 1

            v_slope_mu = 1.2
            v_slope_sigma = 0.6  

            v_high = np.random.normal(v_intercept_mu, v_intercept_sigma, int(len(tmp_df)/2))
            slope_tmp = np.random.normal(v_slope_mu, v_slope_sigma, int(len(tmp_df)/2))

            v_low = v_high + slope_tmp

            tmp_df['v'] = None
            tmp_df['v'].loc[tmp_df['conf']=='HC'] = v_high
            tmp_df['v'].loc[tmp_df['conf']=='LC'] = v_low

            # add noise to other parameters
            tmp_df['t'] = np.random.normal(0.4, 0.1, len(tmp_df))
            tmp_df['z'] = np.random.normal(0.5, 0.1, len(tmp_df))
            tmp_df['sv'] = np.abs(np.random.normal(0, 0.05, len(tmp_df)))
            tmp_df['sz'] = np.abs(np.random.normal(0, 0.05, len(tmp_df)))
            tmp_df['st'] = np.abs(np.random.normal(0, 0.05, len(tmp_df)))

            tmp_df['rt'] = None
            tmp_df['response'] = None

            for trial in range(len(tmp_df)):
                params_tmp = {'v': tmp_df['v'].iloc[trial],
                              'a': tmp_df['a'].iloc[trial],
                              't': tmp_df['t'].iloc[trial],
                              'sv': tmp_df['sv'].iloc[trial],
                              'z': tmp_df['z'].iloc[trial],
                              'sz': tmp_df['sz'].iloc[trial],
                              'st':tmp_df['st'].iloc[trial]
                             }

                sim_tmp, _ = hddm.generate.gen_rand_data(params_tmp,
                                                      size=1,
                                                      subjs=1)
                tmp_df['rt'].iloc[trial] = sim_tmp['rt'].iloc[0].copy()
                tmp_df['response'].iloc[trial] = sim_tmp['response'].iloc[0].copy()        

            sim_data.append(tmp_df)

        # sim_data = pd.concat(sim_data, ignore_index=True)
        sim_data_full = pd.concat(sim_data, ignore_index=True)

        # convert python object to float
        sim_data_full['rt'] = sim_data_full['rt'].astype(float)
        sim_data_full['response'] = sim_data_full['response'].astype(float)

        sim_data_full = sim_data_full[full_colnames]
        sim_data = sim_data_full[['subj_idx', 'conf', 'dbs', 'rt', 'response', 'theta']]

    return sim_data
        
        
        

    
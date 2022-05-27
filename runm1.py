def run_m1(id, df_acc):
    print('running model 1 %i'%id);
    
    import hddm
    import random
    
    exp_name = 'm1'
    print('running models %i'%id, 'for ', exp_name)
    
    # USE the absolute directory in docker.
    dbname = 'm1_chain_%i.db'%id # define the database name, which uses pickle format
    mname  = 'm1_chain_%i'%id    # define the name for the model
    
    m = hddm.HDDM(df_acc,
                  include= ['z', 'v', 't'],
                  depends_on={'v': ['condition', 'StimType'], 'z': ['condition', 'StimType']}, 
                  p_outlier=0.05)
    
    m.find_starting_values()
    m.sample(500, burn=100, dbname=dbname, db='pickle')
    m.save(mname)
    
    return m

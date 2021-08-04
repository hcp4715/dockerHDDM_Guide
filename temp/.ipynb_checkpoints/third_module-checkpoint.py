

def loadm(name="*"):
  """
  加载模型
  :param name:str, 模型名称，可选参数，如果没有将加载目录下所有模型
  :return:dict,存在两个keys(data,modelname)
  """
  m=[]
  mname = []
  import glob
  import hddm
  files = glob.glob(name+".hddm")
  for i in files:
    m.append(hddm.load(i))
    mname.append(i.split(".",1)[0])
  return {"data":m,"modelname":mname}

def DIC_results(*m): 
  """
  计算所有模型DIC
  :param m:hddm, 模型，可选参数，如果没有将自动加载目录下所有模型
  :return:dataframe + hddm
  """
  import hddm
  import pandas as pd
  from third_module import loadm
  if m != ():
    print("m exist")
    mdic = [model.dic for model in m[0]["data"]]
    results = pd.DataFrame({"model_name":m[0]["modelname"],"DIC":mdic})
  else:
    print("load local model file")
    m = loadm()
    mdic = [model.dic for model in m["data"]]
    results = pd.DataFrame({"model_name":m["modelname"],"DIC":mdic})
  return results.sort_values("DIC",ascending=False, inplace=False),m

def params(*m):
  """
  计算所有模型的参数值
  :param m:hddm, 模型，可选参数，如果没有将自动加载目录下所有模型
  :return:dict,包括各modelname + params
  """
  import hddm
  import pandas as pd
  from third_module import loadm
  import numpy as np
  paradata = []
  paradata1 = []
  if m != ():
    print("m exist")
    m = m[0]
  else:
    print("load local model file")
    m = loadm()
  for i in range(len(m["modelname"])):
      sta = m["data"][i].gen_stats()
      paradata1.append(sta)
      sta1 = sta[(1-sta.index.str.contains("_s")).astype(np.bool)]['mean']
      paradata.append(sta1)
      print(m["modelname"][i],"'s para:\n",sta1)
  return {"modelname": m["modelname"],"params":paradata,"para_all":paradata1}

def contrast(params,name=0,condinum=2):
  """
  所有参数avtz，的差异性检验
  :param params:模型参数，来自于函数params
  :param name:模型名字, 必须指定需要比较的模型
  :param condinum:必须指明变量有多少水平
  :return:p，f值
  """
  import hddm
  import matplotlib as plt
  if isinstance(name,int):
    mname = params["modelname"][name]
    para = params["para_all"][name]
  else:
    mname = name
    para = params["para_all"][params["modelname"] == name]

  para = para[para.index.str.contains('.{6}\(')]
  paraname = ['a','v','t','z']
  para = {i:para[para.index.str.contains(i)] for i in paraname}

  results = {}
  for i,j in para.items():
    if len(j) == 0:
      continue
    a = [j[j.index.str.contains('\('+str(i+1)+'\)')]['mean'] for i in range(condinum)]
    from scipy.stats import f_oneway
    if condinum == 2:
      f,p = f_oneway(a[0],a[1])
    elif condinum == 3:
      f,p = f_oneway(a[0],a[1],a[2])
    elif condinum == 4:
      f,p = f_oneway(a[0],a[1],a[2],a[3])
    elif condinum == 5:
      f,p = f_oneway(a[0],a[1],a[2],a[3],a[4])
    elif condinum == 6:
      f,p = f_oneway(a[0],a[1],a[2],a[3],a[4],a[5])
    results[mname+str(i)] = (f,p)
  return results

def contrast_plot(m,name=0,paralist=['v','a','t','z'],condnum=2):
  """
  参数差异比较画图
  :param m:hddm模型
  :param name:模型名称，或者数字索引
  :param paralist:list,指定需要比较的参数
  :param condnum:int,条件数量
  :return:dataframe + hddm
  """
  import hddm 
  import matplotlib.pyplot as plt

  condition = ["("+str(x+1)+")" for x in range(condnum)]

  if isinstance(name,int):
    mm = m["data"][name]
  else:
    mm = m["data"][m["modelname"] == name+".hddm"]
  
  for i in paralist:
    hddm.analyze.plot_posterior_nodes(mm.nodes_db.node[[str(i)+x for x in condition]])
    plt.xlabel(str(i))
    plt.ylabel('Posterior probability')
    if isinstance(name,int):
      plt.title('Posterior of' + m["modelname"][name] + 'group means')
    else:
      plt.title('Posterior of' + name +"'s " + str(i) + 'group means')
    plt.show()
    plt.savefig(str(i)+'.pdf')

def parallel(func, *args, show=False, thread=False, **kwargs):
  """
  并行计算
  :param func: 函数，必选参数
  :param args: list/tuple/iterable,1个或多个函数的动态参数，必选参数
  :param show:bool,默认False,是否显示计算进度
  :param thread:bool,默认False,是否为多线程
  :param kwargs:1个或多个函数的静态参数，key-word形式
  :return:list,与函数动态参数等长
  """
  import time
  from functools import partial
  from pathos.pools import ProcessPool, ThreadPool
  from tqdm import tqdm
  # 冻结静态参数
  p_func = partial(func, **kwargs)
  # 打开进程/线程池
  pool = ThreadPool() if thread else ProcessPool()
  try:
      if show:
          start = time.time()
          # imap方法
          with tqdm(total=len(args[0]), desc="计算进度") as t:  # 进度条设置
              r = []
              for i in pool.imap(p_func, *args):
                  r.append(i)
                  t.set_postfix({'并行函数': func.__name__, "计算花销": "%ds" % (time.time() - start)})
                  t.update()
      else:
          # map方法
          r = pool.map(p_func, *args)
      return r
  except Exception as e:
      print(e)
  finally:
      # 关闭池
      pool.close()  # close the pool to any new jobs
      pool.join()  # cleanup the closed worker processes
      pool.clear()  # Remove server with matching state

def gelman_rubin_test(df,times=5,**argm):
  """
  计算gelman_rubin r hat值, 默认samples=5000 burn=2000
  :param df:预处理后的数据
  :param times: chian的数量
  :return:gelman_rubin
  """
  import hddm
  from third_module import parallel
  data_sets = [df] * times
  def temp(df,**argm):
    import hddm
    m = hddm.HDDM(df,**argm)
    samples = 5000
    burn=2000
    m.find_starting_values()
    m.sample(samples,burn,dbname='gelman',db='pickle')
    return m
  ms = parallel(temp,data_sets,**argm)
  results = hddm.analyze.gelman_rubin(ms)
  return results



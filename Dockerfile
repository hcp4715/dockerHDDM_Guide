# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# This Dockerfile is for DDM tutorial
# The buid from the base of minimal-notebook, based on python 3.8.8
# 
FROM jupyter/minimal-notebook:python-3.8.8

LABEL maintainer="Hu Chuan-Peng <hcp4715@hotmail.com>"

USER root

# ffmpeg for matplotlib anim & dvipng for latex labels
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg dvipng && \
    rm -rf /var/lib/apt/lists/*

USER $NB_UID

# Install Python 3 packages
RUN conda install --quiet --yes \
    'arviz=0.11.4' \
    'beautifulsoup4=4.9.*' \
    'conda-forge::blas=*=openblas' \
    'bokeh=2.0.*' \
    'bottleneck=1.3.*' \
    'cloudpickle=1.4.*' \
    'cython=0.29.*' \
    'dask=2.15.*' \
    'dill=0.3.*' \
    'git' \
    'h5py=2.10.*' \
    'hdf5=1.10.*' \
    'ipywidgets=7.6.*' \
    'ipympl=0.8.*'\
    'jupyter_bokeh' \
    'jupyterlab_widgets' \
    'matplotlib-base=3.3.*' \
    'mkl-service' \
    'numba=0.54.*' \
    'numexpr=2.7.*' \
    'pandas=1.0.*' \
    'patsy=0.5.*' \
    'protobuf=3.11.*' \
    'pytables=3.6.*' \
    'scikit-image=0.16.*' \
    'scikit-learn=0.22.*' \
    'scipy=1.4.*' \
    'seaborn=0.11.*' \
    'sqlalchemy=1.3.*' \
    'statsmodels=0.13.*' \
    'sympy=1.5.*' \
    'vincent=0.4.*' \
    'widgetsnbextension=3.5.*'\
    'xlrd=1.2.*' \
    # 'ipyparallel=6.3.0' \
    'pymc=2.3.8' \
    && \
    conda clean --all -f -y && \
    # Activate ipywidgets extension in the environment that runs the notebook server
    # jupyter nbextension enable --py widgetsnbextension --sys-prefix && \
    # Activate ipyparallel extension in the enviroment
    # ipcluster nbextension enable && \
    # # Also activate ipywidgets extension for JupyterLab
    # # Check this URL for most recent compatibilities
    # # https://github.com/jupyter-widgets/ipywidgets/tree/master/packages/jupyterlab-manager
    # jupyter labextension install @jupyter-widgets/jupyterlab-manager@^2.0.0 --no-build && \
    # jupyter labextension install @bokeh/jupyter_bokeh@^2.0.0 --no-build && \
    # jupyter labextension install jupyter-matplotlib@^0.7.2 --no-build && \
    # jupyter lab build -y && \
    # jupyter lab clean -y && \
    # npm cache clean --force && \
    # fix-permissions "${CONDA_DIR}" &&\
    # rm -rf "/home/${NB_USER}/.cache/yarn" && \
    # rm -rf "/home/${NB_USER}/.node-gyp" && \
    fix-permissions "/home/${NB_USER}"

# conda install --channel=numba llvmlite
# pip install sparse
# conda install -c conda-forge python-graphviz
  
USER $NB_UID
RUN pip install --upgrade pip && \
    pip install --no-cache-dir 'hddm==0.8.0' && \
    pip install --no-cache-dir 'feather-format' && \
    # install plotly and its chart studio extension
    pip install --no-cache-dir 'chart_studio==1.1.0' && \
    pip install --no-cache-dir 'plotly==4.14.3' && \
    pip install --no-cache-dir 'cufflinks==0.17.3' && \
    # install ptitprince for raincloud plot in python
    pip install --no-cache-dir 'ptitprince==0.2.*' && \
    # pip install --no-cache-dir 'kabuki==0.6.3' && \
    pip install --no-cache-dir 'p_tqdm' && \
    pip install --no-cache-dir 'paranoid-scientist' && \
    pip install --no-cache-dir 'pyddm' && \
    pip install --no-cache-dir 'pymc3==3.11.*' && \
    pip install --no-cache-dir 'bambi==0.6.*' && \
    fix-permissions "/home/${NB_USER}"

# uninstall old kabuki and install from Github, specify the commit at Jul 9, 2021
RUN pip install --no-cache-dir git+git://github.com/hddm-devs/kabuki.git@9f9c30189f0756c360b37aa8ed4b72d5b4dbb40c && \
    fix-permissions "/home/${NB_USER}"

# # Install facets which does not have a pip or conda package at the moment
# WORKDIR /tmp

# RUN git clone https://github.com/PAIR-code/facets.git && \
#     jupyter nbextension install facets/facets-dist/ --sys-prefix && \
#     rm -rf /tmp/facets && \
#     fix-permissions "${CONDA_DIR}"  &&\
#     fix-permissions "/home/${NB_USER}"

# Import matplotlib the first time to build the font cache.
ENV XDG_CACHE_HOME="/home/${NB_USER}/.cache/"

RUN MPLBACKEND=Agg python -c "import matplotlib.pyplot" &&\
     fix-permissions "/home/${NB_USER}"

# USER $NB_UID
# WORKDIR $HOME

# # Change the configuration of ipyparallel
# RUN sed -i  "/# Configuration file for jupyter-notebook./a c.NotebookApp.server_extensions.append('ipyparallel.nbextension')"  /home/jovyan/.jupyter/jupyter_notebook_config.py

USER $NB_UID
RUN jupyter nbextension enable --py widgetsnbextension --sys-prefix && \
    jupyter labextension install @jupyter-widgets/jupyterlab-manager --no-build && \
    jupyter labextension install jupyter-matplotlib --no-build && \
    jupyter lab build && \
        jupyter lab clean && \
        jlpm cache clean && \
        npm cache clean --force && \
        rm -rf "/home/${NB_USER}/.cache/yarn" && \
        rm -rf "/home/${NB_USER}/.node-gyp" && \
    fix-permissions "/home/${NB_USER}"

# USER root
RUN jupyter notebook --generate-config -y

USER $NB_UID
# Copy example data and scripts to the example folder
RUN mkdir /home/$NB_USER/examples && \
    rm -r /home/$NB_USER/work && \
    fix-permissions /home/$NB_USER

# COPY /example/Hddm_test_parallel.ipynb /home/${NB_USER}/example
# COPY /example/df_example.csv /home/${NB_USER}/example
# COPY /example/HDDM_official_tutorial_ArviZ.ipynb /home/${NB_USER}/example
# COPY /example/HDDM_official_tutorial_reproduced.ipynb /home/${NB_USER}/example


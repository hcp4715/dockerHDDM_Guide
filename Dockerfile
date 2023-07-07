# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# This Dockerfile is for DDM tutorial
# The buid from the base of minimal-notebook, based on python 3.8.8
ARG HDDMVersion=3dcf4af58f2b7ce44c8b7e6a2afb21073d0a5ef9
ARG BASE_CONTAINER=jupyter/scipy-notebook:python-3.8
FROM $BASE_CONTAINER
LABEL authors="Hu Chuan-Peng <hcp4715@hotmail.com>,bef0rewind <ron.huafeng@gmail.com>"

USER root

RUN buildDeps='gcc g++ gfortran' && \
    set -x && \
    apt-get update && apt-get install -y $buildDeps --no-install-recommends && \
    apt-get install -y libatlas-base-dev liblapack-dev libopenblas-dev --no-install-recommends && \
    apt-get install -y ffmpeg dvipng --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*
    

USER $NB_UID

ARG HDDMVersion
# Install pymc2 and hddm. pymc2 is installed using a patch to fix build warnings and errors
# Uninstall pymc 5 to avoid conflict with pymc2
COPY /0001-fix-build.patch 001.patch
RUN pip uninstall --no-cache-dir pymc -y && \
    git clone https://github.com/pymc-devs/pymc2.git pymc2 &&  mv 001.patch pymc2 && \
    cd pymc2 && \
    git checkout 6b1b51ddea1a74c50d9a027741252b30810b29e0 && \
    git apply 001.patch && \
    pip install --no-cache-dir . && \
    cd .. && rm -rf pymc2 && \
    pip install --no-cache-dir git+https://github.com/hddm-devs/kabuki && \    
    pip install --no-cache-dir git+https://github.com/hddm-devs/hddm@${HDDMVersion} && \
    fix-permissions "/home/${NB_USER}"

# Install other Python 3 packages
RUN conda install -c conda-forge --quiet --yes \
    'git' \
    'jupyter_bokeh' \
    'python-graphviz' && \
    conda clean --all -f -y && \
    pip install --upgrade pip && \
    pip install --no-cache-dir 'plotly==4.14.3' && \
    pip install --no-cache-dir 'cufflinks==0.17.3' && \
    # install ptitprince for raincloud plot in python
    pip install --no-cache-dir 'ptitprince==0.2.*' && \
    pip install --no-cache-dir 'p_tqdm' && \
    # install paranoid-scientist for pyddm
    pip install --no-cache-dir 'paranoid-scientist' && \
    pip install --no-cache-dir 'pyddm' && \
    # install bambi
    pip install --no-cache-dir 'pymc3==3.11.*' && \
    pip install --no-cache-dir 'bambi==0.8.*' && \
    fix-permissions "/home/${NB_USER}"

# Import matplotlib the first time to build the font cache.
ENV XDG_CACHE_HOME="/home/${NB_USER}/.cache/"

RUN MPLBACKEND=Agg python -c "import matplotlib.pyplot" &&\
    rm -r /home/${NB_USER}/work && \
    fix-permissions "/home/${NB_USER}"

WORKDIR $HOME

COPY /temp/HDDM_official_tutorial_reproduced.ipynb \
     /temp/RLHDDMtutorial_reproduced.ipynb \
     /tutorial/dockerHDDM_tutorial.ipynb \
     /tutorial/Run_all_models.py \
     /tutorial/Def_Models.py \
     example/

COPY /scripts/HDDMarviz.py \
     /scripts/plot_ppc_by_cond.py \
     /scripts/pointwise_loglik_gen.py \
     /scripts/post_pred_gen_redefined.py \
     /scripts/InferenceDataFromHDDM.py \
     scripts/

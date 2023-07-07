# About this Repo

This is a repo for preparing *A Hitchhiker’s Guide to Bayesian Hierarchical Drift-Diffusion Modeling with dockerHDDM* 

Please read our preprint at: https://psyarxiv.com/6uzga/

The docker image described by this tutorial can be found at: https://hub.docker.com/r/hcp4715/hddm, with tag `0.8_tutorial`.

## Repository Structure

The Docker image comes with multiple Jupyter notebooks that provide a tutorial and examples on how to use HDDM. It also contains various scripts that could be useful for your analysis.

This Docker image is set up to make it easy to use HDDM, especially for machines with aarch64 architecture (like M1 Chip Mac) which are not natively supported due to dependency on the deprecated version of PyMC (PyMC2).

```
dockerHDDM_Guide
|   Dockerfile
|   README.md
|
└───scripts
|   |    HDDMarvz.py
|   |    InferenceDataFromHDDM.py
|   |    plot_ppc_by_cond.py
|   |    pointwise_loglik_gen.py
|   |    post_pred_gen_redefined.py
|   |    ...
|
└───temp
|   |    include all kinds of temporary notebooks and scripts
|   |    ...
|
└───tutorial
    |    dockerHDDM_tutorial.ipynb
    |    Def_Models.py
    |    Run_all_models.py
    |    figs
```

## Understanding HDDM

[HDDM](https://github.com/hddm-devs/hddm/) (Hierarchical Drift Diffusion Model) is a Python toolbox for hierarchical Bayesian parameter estimation of the Drift Diffusion Model, powered by PyMC. The Drift Diffusion Models are widely used in psychology and cognitive neuroscience to study decision making.

## Scope of the current tutorial
We limited our tutorial to classic functions in HDDM (version 0.8.0), instead of the latest version of HDDM (0.9.*). However, the docker images of more recent HDDM are available (https://hub.docker.com/r/hcp4715/hddm).

## Quick Start Guide

### Step 1: Docker Installation

For Mac users, see [this](https://docs.docker.com/desktop/install/mac-install/) for installation and [this](https://docs.docker.com/desktop/mac/permission-requirements/) for permission requirements. 

For Windows users, see [this](https://docs.docker.com/desktop/install/windows-install/) for installation and [this](https://docs.docker.com/desktop/windows/permission-requirements/) for permission requirements.

For Linux users, you may only need the docker engine instead of the docker desktop, see the differences [here](https://docs.docker.com/desktop/faqs/linuxfaqs/#what-is-the-difference-between-docker-desktop-for-linux-and-docker-engine). Please see [here](https://docs.docker.com/engine/install/) for installing the docker engine in different distributions of Linux.

** Please verify docker desktop or docker engine is properly installed ** 

For Mac & Windows users, start docker desktop and then run `hello-world` images by the following code in your terminal or command line:

`docker run hello-world`

This command downloads a test image and runs it in a container. When the container runs, it prints a confirmation message and exits.

For Linux users, verification of the installation is part of the instructions, which include code (for Ubuntu) like this:

`sudo docker run hello-world`

If you want to run docker without `sudo`, please see [here](https://docs.docker.com/engine/install/linux-postinstall/).

### Step 2: Pull the `hddm:08_tutorial`

Now that we successfully installed docker and can run docker in the terminal or command line, we then pull the docker image for the current tutorial using the code below:

```
docker pull hcp4715/hddm:0.8_tutorial
```

Note that this is also part of our tutorial (see our preprint: https://psyarxiv.com/6uzga/) and code (in `jupyter notebook`, i.e., `./tutorial/dockerHDDM_tutorial.ipynb` in this repo).

### Step 3: Using HDDM and the tutorial

Now that we successfully pulled the docker image for the tutorial, we can use use the HDDM inside the docker by starting a container.

Run the code below in the terminal:

```
docker run -it --rm --cpus=5 \
-v /home/hcp4715/DDM/dockerHDDM_guide:/home/jovyan/work \
-p 8888:8888 hcp4715/hddm:0.8_tutorial jupyter notebook
```

`docker run` ---- run a docker image in a container

`-it` ---- Keep STDIN open even if not attached

`--rm` ---- Automatically remove the container when it exits

`--cpus=5` ---- Number of cores will be used by docker, make sure you have more cores than the number here

`-v` ---- mount a folder to the container

`/home/hcp4715/DDM/dockerHDDM_guide` ---- the directory of a local folder where I store my script and data. 

`/home/jovyan/work` ---- the folder path  where the local folder will be mounted [**do not change this unless you know what you are doing**]

`-p` ---- Publish a container’s port(s) to the host

`hcp4715/ddm:0.8_tutorial` ---- the docker image to run

`jupyter notebook` ---- Open the juypter notebook when start running the container.

After running the code above, bash will output like this:

```
....
To access the notebook, open this file in a browser:
        file:///home/jovyan/.local/share/jupyter/runtime/nbserver-6-open.html
Or copy and paste one of these URLs:
    http://174196acc395:8888/?token=75f1a7a8ffcbb55f0c2802433a9a5d57ac00868e05089c09
 or http://127.0.0.1:8888/?token=75f1a7a8ffcbb55f0c2802433a9a5d57ac00868e05089c09
```

Copy the url (http://127.0.0.1:8888/?.......) to a browser (firefox or chrome) and it will show a web page, this is the interface of jupyter notebook! 

Under the `Files` tab, there should be three folders: `work`, `example`, and `scripts`. The `work` folder is the local folder mounted in docker container. The `example` folder was the one built in docker image, this folder contains several example jupyter notebooks, including `dockerHDDM_tutorial.ipynb`. The `scripts` folder contains python scripts that are supporting function unavailable in original HDDM.

Enter `example` folder, you can reproduce the analysis we presented in the tutorial.

Enter `work` folder, you can analyze your own data stored in folder `/home/hcp4715/DDM/dockerHDDM_guide` with HDDM (version 0.8).

## Building the Docker Image

The Docker image is built from a Jupyter scipy-notebook base and comes with all necessary system and Python packages for running HDDM. The HDDM version can be specified during the build process using the build argument `HDDMVersion`. If no version is specified, it defaults to the v0.8.0 branch.

To build the Docker image, you can use the following command:

```bash
docker build --build-arg HDDMVersion=<version> -t hddm:<tag> .
```

Replace `<version>` with the HDDM version you want to install and `<tag>` with the tag you want to use for the Docker image.

## Acknowledgement
Thank [@madslupe](https://github.com/madslupe) for his previous HDDM image, which laid the base for the current version. Thank [Dr Rui Yuan](https://scholar.google.com/citations?user=h8_wSLkAAAAJ&hl=en) for his help in creating the Dockerfile.

## Contributing

Contributions to improve this Docker image are welcome. If you find any issues or have suggestions, please open an issue in this repository.
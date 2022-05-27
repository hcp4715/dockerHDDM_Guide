# Reproducible Bayesian hierarchical drift-diffusion modelling with docker

## What is HDDM? 
A python package for hierarchical drift-diffusion models.

### Scope of the current tutorial
We limited our tutorial to classic functions in HDDM (version 0.8.0), instead of the latest version of HDDM (0.9.5), which included likelihood-free methods that are not stable and widely used yet. However, the docker image of HDDM 0.9.5 is available.

## Motivation behind this guide
1. HDDM is an influential package for DDM, which is an class of models that used widely in different fields
2. HDDM' tutorial is outdated 
3. Principled workflow are recommended in recent year.

## How to use this guide

First, this guide included both theoretical and practical parts. 

Second, all scripts and code were packaged into a docker image. You need to pull the docker image from docker hub. To do so, first install docker and test it. There are many tutorial on this, here is one on [docker's website](https://docs.docker.com/engine/install/ubuntu/) for linux. Then, pull the docker image from docker hub:

```
docker pull hcp4715/hddm:0.8_tutorial
```

**Note**: you may need `sudo` permission to run `docker`.

After pulling it from docker hub, you can then run jupyter notebook in the container (e.g., in bash of linux):

```
docker run -it --rm --cpus=5 \
-v /home/hcp4715/DDM_guide:/home/jovyan/work \
-p 8888:8888 hcp4715/hddm:0.8_tutorial jupyter notebook
```

`docker run` ---- run a docker image in a container

`-it` ---- Keep STDIN open even if not attached

`--rm` ---- Automatically remove the container when it exits

`--cpus=5` ---- Number of cores will be used by docker

`-v` ---- mount a folder to the container

`/home/hcp4715/DDM_guide` ---- the directory of a local folder where I stored my data. 

`/home/jovyan/work` ---- the folder path  where the local folder will be mounted. 

`-p` ---- Publish a container’s port(s) to the host

`hcp4715/ddm:0.8_tutorial` ---- the docker image to run

`jupyter notebook` ---- Open juypter notebook when start running the container.

After running the code above, bash will has output like this:

```
....
To access the notebook, open this file in a browser:
        file:///home/jovyan/.local/share/jupyter/runtime/nbserver-6-open.html
Or copy and paste one of these URLs:
    http://174196acc395:8888/?token=75f1a7a8ffcbb55f0c2802433a9a5d57ac00868e05089c09
 or http://127.0.0.1:8888/?token=75f1a7a8ffcbb55f0c2802433a9a5d57ac00868e05089c09
```

Copy the url (http://127.0.0.1:8888/?.......) to a browser (firefox or chrome) and it will show a web page, this is the interface of jupyter notebook! 

Under the `Files` tab, there should be three folders: `work`, `example`, and `scripts`. The `work` folder is the local folder mounted in docker container. The `example` folder was the one built in docker image, this folder includes example jupyter notebooks. The `scripts` folder contains python scripts that are supporting function unavailable in original HDDM.

Enter `work` folder, you can start your analysis within jupyter notebook.

## Using the tutorial scipts
You can also run the tutorial notebook in the `example` folder without mounting local folder to the docker container. 

```
docker run -it --rm --cpus=5 \
-p 8888:8888 hcp4715/hddm:0.8_tutorial jupyter notebook
```

## Potential errors
* Permission denied. Please see this [post](https://groups.google.com/forum/#!topic/hddm-users/Qh-aOC0N6cU) about the permission problem.

## How this docker image was built
An alternative way to get the docker image is to build it from `Dockerfile`.

I built this docker image under Ubuntu 20.04. 

Code for building the docker image (don't forget the `.` in the end):

```
docker build -t hcp4715/hddm:0.8_tutorial -f Dockerfile .
```
You can replace `hcp4715` with your username in docker hub, and replace `ddm:0.8_tutorial` with a name and tag you prefer.

## Acknowledgement
Thank [@madslupe](https://github.com/madslupe) for his previous HDDM image, which laid the base for the current version. Thank [Dr Rui Yuan](https://scholar.google.com/citations?user=h8_wSLkAAAAJ&hl=en) for his help in creating the Dockerfile.

# Workshop #1

The following packages are used in this project:

* matplotlib.pyplot
* scipy
* moviepy
* numpy
* cv2

The easyest way to create a working environment is to install [miniconda](https://conda.io/miniconda.html) and run the following command to install the packages specied in the `environment.yml` file.

`sudo conda env create -f environment.yml`

After success, activate the environment:

`source activate bpcar`	

and run the demo:

`python lanes1.py`

If you see something like this, you are good!

![output](output1.png)
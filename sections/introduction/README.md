<a href="../../#table-of-contents"><-- Back to table of contents</a>

# Introduction

## Getting started

This tutorial is an introduction to mass spectrometry data handling and preprocessing in Python, and also an introduction to some machine learning algorithms.
As with a previous tutorial in this summer school, we will rely on the scikit-learn and numpy packages to handle, respectively, the machine learning and matrices of data. 

<img src="https://www.python.org/static/img/python-logo@2x.png" height="50" />

<img src="http://scikit-learn.org/stable/_static/scikit-learn-logo-small.png" height="50" /> 

<img src="http://www.numpy.org/_static/numpy_logo.png" height="50" />

Please ensure you run the install script in order for some sections of code to work.
This will simply compile some c++ code that will be used for the alignment algorithm.

```bash
sh install.sh
```

Then, activate the conda environment and enter the example directory

```bash
activate ms
cd example/
```

And open a jupyter notebook

```bash
jupyter notebook
```

**Alternative :**

If you want to run this tutorial from elsewhere than the virtual machine from the Summer School, use the *install_without_conda.sh* script that does not use anaconda or miniconda.

```bash
sh install_without_conda.sh
```

The command to activate the virtual environment is slightly different, shown below:

```bash
source ms/bin/activate
```

You can then enter the *example* directory and open a jupyter notebook.

## Objectives

After completing this tutorial, you should have acquired the following skills:
* Using Python to apply correction algorithms to mass spectra data sets.
* Perform machine learning experiments using correct protocols.
* Applying learning algorithms to mass spectra data

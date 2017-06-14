# Applying Virtual Lock Masses and Alignment

## Loading the spectra

The dataset used for this tutorial is a set of 80 samples of red blood cell cultures. 
Their spectra was acquired by LDTD-ToF mass spectrometry on a Waters Synapt G2-Si instrument. 
These spectra were acquired in high resolution mode using a data independant acquisition mode (MS^e).

Of these 80 samples, 40 are from red blood cell cultures infected by malaria. 
The other 40 samples are not infected. It is the objective of this tutorial to correct and align these spectra in order to classify them by machine learning.

First, the data must be loaded into memory. The file is contained within the tutorial repository, named "dataset.h5". 
It uses the [hdf5 file format](https://en.wikipedia.org/wiki/Hierarchical_Data_Format), which is a very efficient format for multiple types of datasets and numerical data.

The function load_spectra handles the loading operation, returning the spectra ready for the next step.

```python
from tutorial_code.utils import load_spectra

datafile = "dataset.h5"
spectra = load_spectra(datafile)
```
Here, the spectra are loaded in memory. 
However, no mass correction or alignment has been applied to this data.

## Applying the Virtual Lock Mass Algorithm

*summarize correction problem*

*show example figure*

*the virtual lock mass algorithm must be applied to the dataset*

```python
code snippet
```

*explain commands*

## Applying Alignment

*VLM peaks are already aligned, but some variation remains on other peaks*

*fig?*

*an alignment algorithm must be applied to the data to render spectra more comparable*

```python
code snippet
```

*Intensity normalisations can be introduced at this point*

*The data is ready to be converted into a format appropriate for machine learning*

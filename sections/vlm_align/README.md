<a href="../../#table-of-contents"><-- Back to table of contents</a>

# Applying Virtual Lock Masses and Alignment

## Loading the spectra

The dataset used for this tutorial is a set of 80 samples of red blood cell cultures. 
Their spectra was acquired by LDTD-ToF mass spectrometry on a Waters Synapt G2-Si instrument. 
These spectra were acquired in high resolution mode using a data independant acquisition mode ($MS^e$).

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

The code for the Virtual Lock Mass Corrector is imported by the following command.

```python
from tutorial_code.virtual_lock_mass import VirtualLockMassCorrector
```

After this, we need to create a corrector.
The command below creates one with a maximum window size of 40 ppms and a minimum peak intensity of 1000.
These settings provide the maximum number of VLM correction points on the dataset.

The corrector is subsequently fitted to the dataset.
It is at this step that the algorithm detects the Virtual Lock Mass points, as described in Plenary session 9.

Once the algorithm has detected the correction points, we will use the *transform* function in order to apply the correction algorithm to the spectra.
The resulting corrected spectra need to be stored in a new variable, *corrected_spectra*.

```python
corrector = VirtualLockMassCorrector(window_size=40, minimum_peak_intensity=1000)

corrector.fit(spectra)

corrected_spectra = corrector.transform(spectra)
```

## Applying Alignment

Now that larger shifts between samples have been corrected, one step remains for the preprocessing of the spectra.
This is an **alignment** step, in order to remove small random variations in the m/z values of the peaks.
These variations are due to random noise, to quantum effects in detection and to preprocessing by the mass spectrometer for example.

We import the code for the aligned with this command:

```python
from tutorial_code.aligner import Mass_Spectra_Aligner
```
We then create an aligner.
The command below creates an aligner with a window size of 20 ppms.

As with the corrector, the aligner first needs to be *fitted* to the set of spectra.
During this steps, it detects the alignment sequences and alignment points needed to align the spectra.

Afterwards, we *transform* the dataset by applying the alignment to the spectra.
Individual peaks will be moved to the alignment point closest to their m/z value, as long as that m/z value is within the window of 20 ppms.

```python
aligner = Mass_Spectra_Aligner(window_size=20)

aligner.fit(corrected_spectra)

aligned_spectra = aligner.transform(corrected_spectra)
```

After both correction and alignment, the spectra are ready to be compared.
Although the format of the data is not right for statistical analysis or machine learning applications, since these methods require the data to be in **matrix** form.

We then convert the data into a matrix using the given code.

```python
from tutorial_code.utils import spectrum_to_matrix

data = spectrum_to_matrix(aligned_spectra)
```

Finally, we need to extract the labels from the spectra in order to be able to classify the spectra according to their status (infected or not infected by malaria).

The following code will extract the tags from the data and return it.

```python
from tutorial_code.utils import extract_tags

tags = extract_tags(aligned_spectra)
```

We are now ready to apply machine learning approaches to the set of spectra.
Please proceed to the next section.

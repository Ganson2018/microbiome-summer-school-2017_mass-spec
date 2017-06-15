# -*- coding: utf-8 -*-

import numpy as np
from .spectrum import Spectrum
from .spectrum_io import hdf5_load
from .spectrum_utils import ThresholdedPeakFiltering

def load_spectra(datafile):
    """
    Loads the spectra from an hdf5 file into memory
    :param datafile: the hdf5 file containing the spectra
    :return: the spectra in an ndarray.
    """
    spectra = hdf5_load(datafile)
    thresher = ThresholdedPeakFiltering(threshold=250)
    spectra = thresher.fit_transform(spectra)
    return spectra
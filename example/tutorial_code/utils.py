# -*- coding: utf-8 -*-

import numpy as np
from .spectrum import Spectrum, unify_mz
from .spectrum_io import hdf5_load
from .spectrum_utils import ThresholdedPeakFiltering
from copy import deepcopy
from sklearn.metrics import zero_one_loss, f1_score, precision_score, recall_score

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

def spectrum_to_matrix(spectra):
    """
    Convert an array of spectra to a ndarray
    :param spectra: The spectra to extract
    :return: ndarray of the peak intensities
    """
    new_spectra = deepcopy(spectra)
    unify_mz(new_spectra)

    data = []
    for s in new_spectra:
        data.append(s.intensity_values)

    return np.asarray(data)

def extract_tags(spectra):
    tags = []

    for s in spectra:
        if("_Non_Infected_" in s.metadata["file"]):
            tags.append(0)
        else:
            tags.append(1)

    return np.asarray(tags)

def evaluate_learner(y_true, y_pred):
    results = {}
    results["zero_one_loss"] = zero_one_loss(y_true, y_pred)
    results["f1_score"] = f1_score(y_true, y_pred)
    results["precision"] = precision_score(y_true, y_pred)
    results["recall"] = recall_score(y_true, y_pred)
    return results
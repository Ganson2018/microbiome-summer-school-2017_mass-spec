# -*- coding: utf-8 -*-

from __future__ import print_function, division, absolute_import, unicode_literals
import numpy as np
from bisect import bisect_left
from copy import deepcopy
from .spectrum import Spectrum

def copy_spectrum_with_new_intensities(spectrum, new_intensity_values):
    """
    Copies a spectrum and replaces its intensity values.

    Parameters:
    -----------
    spectrum: Spectrum
        The spectrum to copy
    new_intensity_values: array_like, dtype=float, shape=n_peaks
        The new intensity values

    Note:
    -----
    * This is more efficient than deepcopying the spectrum and modifying its intensity values.
    * This ensures that the metadata is deepcopied
    """
    metadata = deepcopy(spectrum.metadata)
    # XXX: The mz_values and intensity_values are copied in the constructor. No need to copy here.
    return Spectrum(mz_values=spectrum.mz_values, intensity_values=new_intensity_values,
                    mz_precision=int(spectrum.mz_precision), metadata=metadata)

def copy_spectrum_with_new_mz_and_intensities(spectrum, new_mz_values, new_intensity_values):
    """
    Copies a spectrum and replaces its mz and intensity values.

    Parameters:
    -----------
    spectrum: Spectrum
        The spectrum to copy
    new_mz_values: array_like, dtype=float, shape=n_peaks
        The new mz values
    new_intensity_values: array_like, dtype=float, shape=n_peaks
        The new intensity values

    Note:
    -----
    * This is more efficient than deepcopying the spectrum and modifying its mz and intensity values.
    * This ensures that the metadata is deepcopied
    """
    metadata = deepcopy(spectrum.metadata)
    # XXX: The mz_values and intensity_values are copied in the constructor. No need to copy here.
    return Spectrum(mz_values=new_mz_values, intensity_values=new_intensity_values,
                    mz_precision=int(spectrum.mz_precision), metadata=metadata)

def binary_search_for_left_range(mz_values, left_range):
    """
    Return the index in the sorted array where the value is larger or equal than left_range
    :param mz_values:
    :param left_range:
    :return:
    """
    l = len(mz_values)
    if mz_values[l-1] < left_range :
        raise ValueError("No value bigger than %s" % left_range)
    low = 0
    high = l -1
    while low <= high:
        mid = low +int(((high-low)//2))
        if mz_values[mid] >= left_range:
            high = mid - 1
        else:
            low = mid + 1
    return high+1


def binary_search_for_right_range(mz_values, right_range):
    """
    Return the index in the sorted array where the value is smaller or equal than right_range
    :param mz_values:
    :param right_range:
    :return:
    """
    l = len(mz_values)
    if mz_values[0] > right_range :
        raise ValueError("No value smaller than %s" % right_range)
    low = 0
    high = l - 1
    while low <= high:
        mid = low +int(((high-low)//2))
        if mz_values[mid] > right_range:
            high = mid - 1
        else:
            low = mid + 1
    return low-1

def binary_search_find_values(mz_values, left, right):
    return mz_values[left:right+1]

def binary_search_mz_values(spectrum, mz, window):
    """
    Find the values in an centered interval
    :param spectrum: A list of values
    :param mz: The centered points of the search
    :param window: The intervale
    :return: A list of values in the range mz +/- intervale
    """
    right = binary_search_for_right_range(spectrum, mz+(mz*window/1000000.0))
    left = binary_search_for_left_range(spectrum, mz-(mz*window/1000000.0))
    return spectrum[left:right+1]

def take_closest_lo(myList, myNumber, lo=0):
    #http://stackoverflow.com/questions/12141150/from-list-of-integers-get-number-closest-to-a-given-value
    """
    Assumes myList is sorted. Returns closest value to myNumber.

    If two numbers are equally close, return the smallest number.
    """
    pos = bisect_left(myList, myNumber, lo=lo)
    if pos == 0:
        return myList[0], pos
    if pos == len(myList):
        return myList[-1], pos-1
    before = myList[pos - 1]
    after = myList[pos]
    if after - myNumber < myNumber - before:
       return after, pos
    else:
       return before, pos-1

def take_closest(my_list, my_number):
    # http://stackoverflow.com/questions/12141150/from-list-of-integers-get-number-closest-to-a-given-value
    """
    Assumes myList is sorted. Returns closest value to myNumber.

    If two numbers are equally close, return the smallest number.
    """
    pos = bisect_left(my_list, my_number)
    if pos == 0:
        return my_list[0]
    if pos == len(my_list):
        return my_list[-1]
    before = my_list[pos - 1]
    after = my_list[pos]
    if after - my_number < my_number - before:
        return after
    else:
        return before

class PreprocessorMixin:
    """
    A mixin class for the spectrum pre-processing algorithms.
    """

    def __init__(self):
        pass

    def fit(self, spectra_list):
        """
        Fit the pre-processing algorithm based on a training sample of spectra.

        Parameters
        ----------
        spectra_list: array-like, type=Spectrum, shape=[n_spectra]
            The list of training spectra.
        """
        pass

    def transform(self, spectra_list):
        """
        Transform a list of spectra based on the fitted parameters.

        Parameters
        ----------
        spectra_list: array-like, type=Spectrum, shape=[n_spectra]
            The list of spectra to transform.

        Returns
        -------
        transformed_spectra_list: array-like, type=Spectrum, shape=[n_spectra]
            The list of transformed spectra.
        """
        raise NotImplementedError()

    def fit_transform(self, spectra_list):
        """
        Fit the pre-processing algorithm based on a training sample of spectra and transform the spectra based
        on the fitted parameters.

        Parameters
        ----------
        spectra_list: array-like, type=Spectrum, shape=[n_spectra]
            The list of spectra to transform.

        Returns
        -------
        transformed_spectra_list: array-like, type=Spectrum, shape=[n_spectra]
            The list of transformed spectra.
        """
        self.fit(spectra_list)
        return self.transform(spectra_list)

class ThresholdedPeakFiltering(PreprocessorMixin):
    """
    A pre-processor for removing the peaks that are less intense than a given threshold.
    """
    def __init__(self, threshold=1.0, remove_mz_values=True):
        """
        Constructor.

        Parameters
        ----------
        threshold: float, default=1.0
                   The intensity threshold. All peaks that have an intensity value less or equal to this threshold will
                   be discarded.

        remove_mz_values : bool, default=True
                   Specifies if the m/z values where the intensity was below the threshold should be removed.
        """
        self.threshold = threshold
        self.remove_mz_values = remove_mz_values

    def transform(self, spectra_list):
        """
        Filter peaks for a list of spectra.

        Parameters
        ----------
        spectra_list: array-like, type=Spectrum, shape=[n_spectra]
            The list of spectra to transform.

        Returns
        -------
        transformed_spectra_list: array-like, type=Spectrum, shape=[n_spectra]
            The list of transformed spectra.
        """

        spectra_list = np.array(spectra_list)
        for i, spectrum in enumerate(spectra_list):
            if not self.remove_mz_values:
                intensity_values = deepcopy(spectra_list[i].intensity_values)
                intensity_values[intensity_values <= self.threshold] = 0.0
                spectra_list[i] = copy_spectrum_with_new_intensities(spectrum, intensity_values)
            else:
                keep_mask = spectra_list[i].intensity_values > self.threshold
                spectra_list[i] = copy_spectrum_with_new_mz_and_intensities(spectrum,
                                                                            spectra_list[i].mz_values[keep_mask],
                                                                            spectra_list[i].intensity_values[keep_mask])
        return spectra_list

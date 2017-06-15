# -*- coding: utf-8 -*-

from __future__ import print_function, division, absolute_import, unicode_literals
import h5py as h
import json
from .spectrum import Spectrum

def hdf5_load(file_name, metadata=True):
    """
    Loads spectra from a HDF5 file.

    Parameters:
    -----------
    file_name: str
        The path to the file to load.

    metadata: boolean
        Defaults to True. Boolean to check if we load the metadata along with the spectrum data.

    Returns:
    -------
    spectra: list of Spectrum
        The list of spectra extracted form the file.
    """
    file = h.File(file_name, "r")

    mz_precision = file["precision"][...]
    mz_values = file["mz"][...]
    spectra_intensity_dataset = file["intensity"]

    if metadata and "metadata" in file:
        spectra_metadata_dataset = file['metadata']
    else:
        spectra_metadata_dataset = [None] * spectra_intensity_dataset.shape[0]

    spectra = []
    for spectrum_intensity_values, spectrum_metadata in zip(spectra_intensity_dataset, spectra_metadata_dataset):
        try:
            spectrum_metadata = json.loads(spectrum_metadata.decode("utf-8")) if not spectrum_metadata is None else None
        except AttributeError:
            spectrum_metadata = json.loads(spectrum_metadata) if not spectrum_metadata is None else None
        spectra.append(Spectrum(mz_values=mz_values, intensity_values=spectrum_intensity_values,
                                mz_precision=mz_precision, metadata=spectrum_metadata))
    file.close()

    return spectra
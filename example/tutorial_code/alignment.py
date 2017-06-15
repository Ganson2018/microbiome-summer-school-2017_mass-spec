# -*- coding: utf-8 -*-

from __future__ import print_function, division, absolute_import, unicode_literals
import numpy as np
from .spectrum import Spectrum
from .spectrum_utils import take_closest, binary_search_mz_values
from subprocess import call
from os.path import join
from os import remove



class Mass_Spectra_Aligner():

    def __init__(self, window_size=10):
        self.window_size = window_size
        self.reference_mz = []

    def fit(self, spectra):
        self._train(spectra)

    def _train(self, spectra):
        """
        Fill the reference_mz attribute with possible m/z values.
        :param spectra: A set of spectrum object.
        :return: Nothing
        """
        path = "tutorial_code/cpp_extensions"
        self._write_mz_values_to_file(spectra, path)

        call([str(join(path, "alignment")),
                  "temp_spectra.csv",
                  str(self.window_size)])

        self.reference_mz = self._read_reference_from_file(path)

    def transform(self, spectra):
        new_spectra = []
        for i, s in enumerate(spectra):
            new_spectra.append(self._apply(s))
        return np.asarray(new_spectra)

    def _apply(self, spec):
        # Find closest point that is not outside possible window
        # If point: change mz
        # Else: keep or discard m/z?
        aligned_mz = []
        aligned_int = []
        nf_mz = []
        nf_int = []
        for i, mz in enumerate(spec.mz_values):
            possible_matches = []
            try:
                possible_matches = binary_search_mz_values(self.reference_mz, mz,
                                                           float(self.window_size))
            except ValueError:
                nf_mz.append(mz)
                nf_int.append(spec.intensity_values[i])
                continue
            if (len(possible_matches) > 1):
                possible_matches = [take_closest(possible_matches, mz)]

            if (len(possible_matches) == 1):
                aligned_mz.append(possible_matches[0])
                aligned_int.append(spec.intensity_values[i])
            else:
                aligned_mz.append(mz)
                aligned_int.append(spec.intensity_values[i])
                nf_mz.append(mz)
                nf_int.append(spec.intensity_values[i])

        return Spectrum(np.asarray(aligned_mz), np.asarray(aligned_int),
                        spec.mz_precision, spec.metadata)

    def _write_mz_values_to_file(self, spectra, path):
        filename = "temp_spectra.csv"
        f = open(filename,"w")

        for s in spectra:
            line = ""
            for mz in s.mz_values:
                line += str(mz)
                line += ","
            line = line[:-1]
            line += "\n"
            f.write(line)

        f.close()

    def _read_reference_from_file(self, path):
        filename = "alignmentPoints.txt"

        f = open(filename,"r")
        line = f.readline().strip().split(" ")

        mz_values = []
        for mz in line:
            mz_values.append(round(float(mz),4))

        #clear temporary files
        #remove("temp_spectra.csv")
        #remove(filename)
        return np.asarray(mz_values)
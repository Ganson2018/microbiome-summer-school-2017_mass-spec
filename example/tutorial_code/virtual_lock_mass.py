# -*- coding: utf-8 -*-

from __future__ import print_function, division, absolute_import, unicode_literals
import numpy as np
from .spectrum_utils import copy_spectrum_with_new_mz_and_intensities
from .spectrum_utils import binary_search_for_left_range
from .spectrum_utils import binary_search_for_right_range, take_closest_lo
from .spectrum_utils import ThresholdedPeakFiltering

def is_window_vlm(spectrum_by_peak, window_start_idx, window_end_idx, n_spectra):
    # Check that the window contains the right number of peaks
    if (window_end_idx - window_start_idx + 1) == n_spectra:
        # Check that the window does not contain multiple peaks from some spectra
        window_spectra = spectrum_by_peak[window_start_idx : window_end_idx + 1]
        if len(np.unique(window_spectra)) != len(window_spectra):
            return False
        else:
            return True
    else:
        return False

class VirtualLockMassCorrector(object):

    def __init__(self, window_size, minimum_peak_intensity, max_skipped_points=None,
                 mode='flat', poly_degree=1):
        """
        Initiate a VirtualLockMassCorrector object.
        :param window_size: The distance from left to right in ppm
        :param minimum_peak_intensity: Minimum peak intensity to be considered by the algorithm
        :param max_skipped_points: Maximum number of points that can be skipped during the transform step. None=any.
        :param mode: How the transformation is applied before the first VLM and after the last VLM. [flat only]
        :param poly_degree: Degree of the function used to calculate correction ratio between two VLM.
        :return:
        """
        self.window_size = window_size
        self.window_size_ppm = 1.0 * window_size / 10**6
        self.minimum_peak_intensity = minimum_peak_intensity
        self._vlm_mz = None
        self.max_skipped_points = max_skipped_points
        self.mode = mode
        self.polynomial_degree = poly_degree

    def _compute_vlm_positions(self, peak_groups):
        """
        Tries to set the center of mass of each group as its center. If this shifts the center to a point that is more
        than w ppm from the first peak of the group, it is discarded.

        Note: assumes that the peak groups are sorted
        """
        vlm_mz_values = []
        for group in peak_groups:
            center_of_mass = np.mean(group)
            window_start = center_of_mass * (1 - self.window_size_ppm)
            window_end = center_of_mass * (1 + self.window_size_ppm)
            if window_start <= np.min(group) and window_end >= np.max(group):
                vlm_mz_values.append(center_of_mass)
        return np.array(vlm_mz_values)

    def _find_vlm_peak_groups(self, spectra):
        # List all peaks of all spectra
        peaks = np.concatenate(list(s.mz_values for s in spectra))
        spectrum_by_peak = np.concatenate(list(np.ones(len(s), dtype=np.uint) * i for i, s in enumerate(spectra)))

        # Sort the peaks in increasing order of m/z
        sorter = np.argsort(peaks)
        peaks = peaks[sorter]
        spectrum_by_peak = spectrum_by_peak[sorter]

        vlm_peak_groups = []

        # Start by considering the first window that contains the first peak
        window_start_idx = 0
        window_end_idx = np.searchsorted(peaks, peaks[0], side="right") - 1

        while window_start_idx < len(peaks):

            # Check if the current group of peaks matches the definition of a VLM
            if is_window_vlm(spectrum_by_peak, window_start_idx, window_end_idx, len(spectra)):
                vlm_peak_groups.append(peaks[window_start_idx : window_end_idx + 1])

            # Find the m/z of the first peak in the current group
            window_first_peak_mz = peaks[window_start_idx]

            # Check if there are peaks beyond the last peak of the group
            if window_end_idx < len(peaks) - 1:

                # The outer right peak is the peak following the last peak of the group in the list
                # We find the lower bound (in m/z) of the first window that contains this peak
                outer_right_peak_window_start_mz = (peaks[window_end_idx + 1] / (1 + self.window_size_ppm)) * (1 - self.window_size_ppm)

                # Case 1: There exists a window containing the first peak of the group and the outer right peak
                if outer_right_peak_window_start_mz <= window_first_peak_mz:
                    # We include the outer right peak in the group
                    window_end_idx = np.searchsorted(peaks, peaks[window_end_idx + 1], side='right') - 1

                # Case 2: There does not exist a window containing the first peak and the outer right peak simultaneously
                else:
                    # Since the condition is false, there necessarily exists a non-zero space between the first peak of
                    # the window and the lower bound of the first window where the outer right peak is included. We thus
                    # consider the window containing all the peaks in the group, except the first peak.
                    window_next_peak_idx = np.searchsorted(peaks, window_first_peak_mz, side='right')
                    window_start_idx = window_next_peak_idx

            else:
                # There are no peaks with a greater m/z than the last peak of the group. We simply remove the first peak.
                window_next_peak_idx = np.searchsorted(peaks, window_first_peak_mz, side='right')
                window_start_idx = window_next_peak_idx

        return vlm_peak_groups

    def _make_vlm_set_consistent(self, vlm_mz_values):
        """
        Rejects any VLMs for which the windows overlap

        """
        vlm_mz_values = np.asarray(vlm_mz_values)
        vlm_window_starts = vlm_mz_values * (1 - self.window_size_ppm)
        vlm_window_ends = vlm_mz_values * (1 + self.window_size_ppm)

        inconsistencies = np.where(vlm_window_starts[1:] <= vlm_window_ends[: -1])[0]

        rejection_mask = np.zeros(len(vlm_mz_values), dtype=np.bool)
        rejection_mask[inconsistencies] = True
        rejection_mask[inconsistencies + 1] = True

        return vlm_mz_values[~rejection_mask]

    def _preprocess_spectra(self, spectra):
        return ThresholdedPeakFiltering(threshold=self.minimum_peak_intensity, remove_mz_values=True).fit_transform(spectra)

    def _find_vlm_peaks(self, spectra):
        spectra = self._preprocess_spectra(spectra)
        peak_groups = self._find_vlm_peak_groups(spectra)
        vlm_mz_values = self._compute_vlm_positions(peak_groups)
        pre_vlm_count = len(vlm_mz_values)
        vlm_mz_values = self._make_vlm_set_consistent(vlm_mz_values)
        del pre_vlm_count
        return vlm_mz_values

    def _apply_correction(self, spectrum):
        """
        Apply the VLM to a spectrum
        :param spectrum: A pymspec spectrum to correct
        :return: A corrected pymspec spectrum.
        """
        if len(self._vlm_mz) <= 2:
            raise ValueError("There must be at least 3 points to use virtual lock-mass")

        # Correction is done on a copy of the spectrum. The original spectrum will not be modified.

        found_vlm, observed_mz = self._find_vlock_mass_in_spectra(spectrum) # Find the corresponding points
        correction_ratios = self._calculate_correction_ratios(found_vlm, observed_mz) # Calculate correction ratios at each VLM

        # Correct the points smaller than observed_mz[0]
        corrected_mz = self._correct_points_smaller_than(spectrum, observed_mz[0], correction_ratios[0])

        #Correct all points between observed_mz[0] and observed_mz[-1]
        index = 0
        while index < len(correction_ratios)-1:
            corrected_mz += self._correct_point_between(spectrum, observed_mz[index], observed_mz[index+1],
                                                        correction_ratios[index], correction_ratios[index+1])
            index += 1

        # Correct the points greater than observed_mz[-1]
        corrected_mz += self._correct_points_greater_than(spectrum, observed_mz[-1], correction_ratios[-1])

        # Simple verification that we still have the same number of points...
        if len(corrected_mz) != len(spectrum.mz_values):
            raise ValueError("There should be the same number of mz than in the initial spectrum: %s vs %s"
                             % (len(corrected_mz), len(spectrum.mz_values)))

        # Createa copy and return
        spect_copy = copy_spectrum_with_new_mz_and_intensities(spectrum, np.array(corrected_mz),
                                                               spectrum.intensity_values) # Use the same intensities
        return spect_copy

    def _calculate_correction_ratios(self, found_vlm, observed_mz):
        """
        Do some checks and return the correction for each combination of vlm and observed point.
        :param found_vlm: A list of VLM
        :param observed_mz: The mz from a spectrum corresponding to the VLM
        :return: A list of correction ratio
        """
        if len(observed_mz) <= 0 or len(found_vlm) <= 0:
            raise ValueError("There is no value in vlock_mass or observed_mz")
        if len(observed_mz) != len(found_vlm):
            raise ValueError("v_lock_mass and observed_mz have not the same amount of values")
        correction_ratios = []
        for i, v_mz in enumerate(found_vlm):
            o_mz = observed_mz[i]
            if v_mz <= 0 or o_mz <= 0:
                raise ValueError("Cannot calculate ratio for a null or nagative mz")
            ratio = np.float(v_mz / o_mz)
            correction_ratios.append(ratio)
        return correction_ratios

    def _find_vlock_mass_in_spectra(self, spectrum):
        """
        Search each vlm in a spectrum and return the list of vlm found and their correspondance in the spectrum.
        :param spectrum: A pymspec spectrum
        :return: two lists: The vlm found in the spectrum and their correspondance
        """
        preprocessed_spect = ThresholdedPeakFiltering(threshold=self.minimum_peak_intensity,
                                                      remove_mz_values=True).fit_transform([spectrum])[0]
        observed_mz = []
        vlm_found = []
        number_skipped_points = 0
        for vlm in self._vlm_mz:
            peak = -1
            intensity = -1
            last_index = 0
            try:
                best_match, position = take_closest_lo(preprocessed_spect.mz_values, vlm, lo=last_index)
                mz_difference = abs(best_match - vlm) # Check if the vlm is in the window.
                if mz_difference > vlm * self.window_size_ppm: # self.window_size is from center to side, not side to side.
                    raise ValueError("A VLM was not found in the appropriate window")
                last_index = position
                observed_mz.append(best_match)
                vlm_found.append(vlm)
            except ValueError as error:
                if self.max_skipped_points is None:
                    pass #If none, any VLM can be unfound.
                else:
                    number_skipped_points += 1
                    if number_skipped_points > self.max_skipped_points:
                        raise error
        observed_mz = np.array(observed_mz)
        vlm_found = np.array(vlm_found)
        np.around(observed_mz, decimals=4)
        return vlm_found, observed_mz

    def _correct_points_smaller_than(self, spectrum, mz, ratio):
        """
        Will apply the correction ratio to every points <mz.
        No modification to correction ratio
        :param spectrum: the spectrum to correct
        :param mz: the observed mz of the first virtual lock mass
        :param ratio: the correction ratio of the first virtual lock mass
        :return: the corrected mz values of the spectrum, only those inferior to the first virtual lock mass
        """
        if mz <= 0 or ratio <= 0:
            raise ValueError("Mz and ratio cannot be null or negative")
        mz_list = spectrum.mz_values
        if self.mode == 'flat':
            right = binary_search_for_right_range(mz_list, mz)
            mz_to_be_corrected = mz_list[:right]
            corrected_mz = mz_to_be_corrected * ratio
        else:
            raise NotImplementedError("Use flat mode.")
        return corrected_mz.tolist()

    def _correct_points_greater_than(self, spectrum, mz, ratio):
        """
        :param spectrum: the spectrim to correct
        :param mz: the observed mz of the last virtual lock mass
        :param ratio: the correction ratio of the last virtual lock mass
        :return: the corrected mz values of the spectrum, only those superior to the last virtual lock mass
        """
        if mz <= 0 or ratio <= 0:
            raise ValueError("Mz and ratio cannot be null or negative")
        mz_list = spectrum.mz_values
        if self.mode == 'flat':
            left = binary_search_for_right_range(mz_list, mz)
            mz_to_be_corrected = mz_list[left:]
            corrected_mz = mz_to_be_corrected * ratio
        else:
            raise NotImplementedError("Use flat mode.")
        return corrected_mz.tolist()


    def _correct_point_between(self, spectrum, mz1, mz2, ratio1, ratio2):
        """
        :param spectrum: the spectrum to correct
        :param mz1: an observed mz of a virtual lock mass (smaller than the 2nd)
        :param mz2: an observed mz of a virtual lock mass (greater than the first)
        :param ratio1: correction ratio of mz1
        :param ratio2: correction ratio of mz2
        :return: the corrected mz values from the spectrum that are between mz1 and mz2
        """
        if mz1 <= 0 or mz2 <= 0 or ratio1 <= 0 or ratio2 <= 0:
            raise ValueError("Mz and ratios cannot be null or negative")
        function = self._create_correction_function(mz1, mz2, ratio1, ratio2)

        mz_list =spectrum.mz_values
        right = binary_search_for_right_range(mz_list, mz2)
        left = binary_search_for_left_range(mz_list, mz1)
        mz_to_be_corrected = mz_list[left:right]
        ratios = [function(mz) for mz in mz_to_be_corrected]
        corrected_mz = mz_to_be_corrected * ratios
        return corrected_mz.tolist()


    def _create_correction_function(self, mz1, mz2, ratio1, ratio2):
        """
        Create the y = m*x + b function for the 2 points in parameter
        :param mz1: lowest mz
        :param mz2: highest mz
        :param ratio1: correction ratio at mz1
        :param ratio2: correction ratio at mz2
        :return: a numpy function that can correct the values between mz1 and mz2
        :raises: ValueError is an mz or ratio is <= 0
        """
        if mz1 <= 0 or mz2 <= 0 or ratio1 <= 0 or ratio2 <= 0:
            raise ValueError("Mz and ratios cannot be null or negative")
        if mz1 > mz2:
            raise ValueError("mz2 must be greater than mz1")
        if self.polynomial_degree == 1:
            m = (ratio2 - ratio1) / (mz2 - mz1)
            b = ratio2 - (m * mz2)
            function = lambda x: m * x + b

        else:
            x = np.array([mz1, mz2])
            y= np.array([ratio1, ratio2])
            z = np.polyfit(x, y, self.polynomial_degree)
            function = np.poly1d(z)
        return function

    def fit(self, spectra):
        """
        TODO

        """
        self._vlm_mz = self._find_vlm_peaks(spectra)


    def transform(self, spectra):
        """
        TODO

        """
        if self._vlm_mz is None:
            raise RuntimeError("The VLM corrector must be fitted before applying a correction.")
        return np.asarray([self._apply_correction(spectrum) for spectrum in spectra])
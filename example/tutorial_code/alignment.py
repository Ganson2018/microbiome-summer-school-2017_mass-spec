# -*- coding: utf-8 -*-

from __future__ import print_function, division, absolute_import, unicode_literals
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import fcluster
import fastcluster as fc
from itertools import chain
import numpy as np
from .spectrum import Spectrum
from .spectrum_utils import take_closest, binary_search_mz_values

class Mass_Spectra_Aligner():

    def __init__(self, min_mz=50, max_mz=1200, window_size=15):
        self.min_mz = min_mz
        self.max_mz = max_mz
        self.max_distance = window_size
        self.reference_mz = []

    def fit(self, train_set):
        self._train(train_set)

    def _train(self, train_set, auto_optimizer=False):
        """
        Fill the reference_mz attribute with possible m/z values.
        :param train_set: A set of pymspec object.
        :return: Nothing
        """
        possible_mz = list(chain(mz for spect in train_set for mz in spect.mz_values))
        possible_mz = np.sort(possible_mz)

        # Took some code generated during ATP by Alex Drouin
        # Split the list of unique m/z values into blocks
        # Note: if a peak is too far from its neighbor to possibly cluster with it, there is no need to consider them in
        #       the same clustering. The same applies for all peaks after the neighbor, as they are sorted.
        ppm_at_mz = possible_mz * float(self.max_distance*1) / 10**6  # 1x themax distance allowed in a cluster.
        d_next = np.hstack((np.abs(possible_mz[:-1] - possible_mz[1:]), [0]))  # The distance to the next peak
        tmp = np.where(d_next > ppm_at_mz)[0]
        block_ends = np.hstack((tmp, [len(possible_mz) - 1]))
        block_starts = np.hstack(([0], tmp + 1))

        # For each block, perform a hierarchical clustering
        mz_cluster_idx = np.zeros(possible_mz.shape[0], dtype=np.uint)
        if auto_optimizer:
            small= []
            ok = []
            big= []
        for start_idx, stop_idx in zip(block_starts, block_ends):
            block_mz_values = possible_mz[start_idx:stop_idx+1]
            block_start_mz = possible_mz[start_idx]
            block_stop_mz = possible_mz[stop_idx]

            if start_idx == stop_idx:
                if not auto_optimizer:
                    self.reference_mz.append(block_start_mz)
                continue

            # Compute the distance between each m/z value
            if len(block_mz_values)<100000:
                D = pdist(block_mz_values.reshape(-1, 1), metric="euclidean")

                # Compute the clustering distance threshold
                block_cluster_threshold = np.mean(block_mz_values * self.max_distance/10**6)  # Use mean window size

                # Clustering using fastcluster. (it is very fast!)
                clusters = fcluster(fc.linkage(D, method='complete'), criterion="distance",
                                    t=block_cluster_threshold)
                uniq_clusters = np.unique(clusters)
                for cluster_id in uniq_clusters:
                    cluster_grouper = np.where(clusters == cluster_id)[0]
                    points_in_cluster = block_mz_values[cluster_grouper]
                    if auto_optimizer:
                        if len(points_in_cluster) == len(train_set):
                           ok.append(np.round(np.average([mz for mz in points_in_cluster]), decimals=4))
                           self.reference_mz.append(np.round(np.average([mz for mz in points_in_cluster]), decimals=4))
                        elif len(points_in_cluster) > len(train_set):
                           big.append(np.round(np.average([mz for mz in points_in_cluster]), decimals=4))
                        elif len(points_in_cluster) < len(train_set):
                           small.append(np.round(np.average([mz for mz in points_in_cluster]), decimals=4))
                        #self.reference_mz.append(np.round(np.average([mz for mz in points_in_cluster]), decimals=4))
                    elif not auto_optimizer:
                        self.reference_mz.append(np.round(np.average([mz for mz in points_in_cluster]), decimals=4))
            else:
                print("Splitting in sub-blocks and computing the distance between each pair of peaks using the m/z values")
                blocks = [block_mz_values]
                sub_blocks = []
                has_big_block = True
                while has_big_block:
                    has_big_block=False
                    for b in blocks:
                        if len(b) > 100000:
                            sub_blocks.append(b[0:len(b)//2])
                            sub_blocks.append(b[len(b)//2:])
                            has_big_block = True
                    if has_big_block:
                        blocks  = sub_blocks
                        sub_blocks = []
                for b in blocks:
                    D = pdist(b.reshape(-1, 1), metric="euclidean")

                    # Compute the clustering distance threshold
                    block_cluster_threshold = np.mean(b * self.max_distance/10**6)  # Use mean window size

                    # Clustering using fastcluster. (it is very fast!)
                    clusters = fcluster(fc.linkage(D, method='complete'), criterion="distance",
                                        t=block_cluster_threshold)
                    uniq_clusters = np.unique(clusters)
                    for cluster_id in uniq_clusters:
                        cluster_grouper = np.where(clusters == cluster_id)[0]
                        points_in_cluster = b[cluster_grouper]
                        if auto_optimizer:
                            if len(points_in_cluster) == len(train_set):
                               ok.append(np.round(np.average([mz for mz in points_in_cluster]), decimals=4))
                               self.reference_mz.append(np.round(np.average([mz for mz in points_in_cluster]), decimals=4))
                            elif len(points_in_cluster) > len(train_set):
                               big.append(np.round(np.average([mz for mz in points_in_cluster]), decimals=4))
                            elif len(points_in_cluster) < len(train_set):
                               small.append(np.round(np.average([mz for mz in points_in_cluster]), decimals=4))
                            #self.reference_mz.append(np.round(np.average([mz for mz in points_in_cluster]), decimals=4))
                        elif not auto_optimizer:
                            self.reference_mz.append(np.round(np.average([mz for mz in points_in_cluster]), decimals=4))
        if auto_optimizer:
            return small, ok, big
        else:
            self.reference_mz.sort()

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
                                                           float(self.max_distance))
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
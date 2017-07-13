#! /usr/bin/env python
# Time-stamp: <2015-07-10 13:50 christophe@pallier.org>

"""
Extract data from contrasts maps in the intersections of a priori ROIs
and subject-specific localizer masks.
"""

from glob import glob
import os
import os.path as op

import numpy as np
import nibabel
from nilearn.input_data import NiftiMapsMasker
from nilearn.masking import intersect_masks

from nilearn.masking import apply_mask
from scipy.stats import scoreatpercentile
from nilearn.plotting import plot_roi


def binarize_img(img, threshold):
    mask = img.get_data().copy()
    mask[mask < threshold] = 0.
    mask[mask >= threshold] = 1.
    return nibabel.Nifti1Image(mask, img.get_affine())

def get_mask_size(mask_img):
    return np.sum(mask_img.get_data())

def create_bestvoxels_mask(roi_img, localizer_img, toppercentile=25):
    """ select voxels within roi_img having the largest values in localizer_img """
    masked_data = apply_mask(localizer_img, roi_img)
    threshold = scoreatpercentile(masked_data, 100 - toppercentile)
    mask = binarize_img(localizer_img, threshold)
    return intersect_masks((roi_img, mask), threshold=1)


def create_localizer_mask(roi_img, localizer_img, loc_threshold):
    """ select voxels within roi_img that have a value above loc_threshold in localizer_img """
    locmask = binarize_img(localizer_img, loc_threshold)
    return intersect_masks((roi_img, locmask), threshold=1)

### Three methods to extract data from ROIs

def get_data_in_rois_method1(ROIs, subjects, contrasts, condir):
    """ returns the average contratst in each ROI and for each subject """
    masker = NiftiMapsMasker(ROIs)
    values = np.zeros((len(subjects), len(contrasts), len(ROIs)))
    for isub, sub in enumerate(subjects):
        conlist = [op.join(sub, condir, x) for x in contrasts]
        values[isub, :] = masker.fit_transform(conlist)
    return values


def get_data_in_rois_method2(ROIs, subjects, contrasts, condir, localizerf, threshold):
    """ returns, for individual subjects, the average contrasts values  in ROIs masked by individual localizers,
    thresholded at a fixed theshold"""
    values = np.zeros((len(subjects), len(contrasts), len(ROIs)))
    for isub, sub in enumerate(subjects):
        conlist = [op.join(sub, condir, x) for x in contrasts]
        localizer_img = nibabel.load(op.join(sub, localizerf))
        locmask = binarize_img(localizer_img, threshold)
        masker = NiftiMapsMasker(ROIs, locmask)
        values[isub, :] = masker.fit_transform(conlist)
    return values


def get_data_in_rois_method3(ROIs, subjects, contrasts, condir, localizerf, toppercentile):
    """ returns, for individual subjects, the average contrasts values  in ROIs masked by individual localizers,
    tresholded to keep a toppertcentil voxels in each ROI. """
    values = np.zeros((len(subjects), len(contrasts), len(ROIs)))
    print ROIs
    for isub, sub in enumerate(subjects):
        conlist = [op.join(sub, condir, x) for x in contrasts]
        localizer_img = nibabel.load(op.join(sub, localizerf))
        for iroi, roi in enumerate(ROIs):
            roi_img = nibabel.load(roi)
            locmask = create_bestvoxels_mask(roi_img, localizer_img, toppercentile)
            values[isub, :, iroi] = np.mean(apply_mask(conlist, locmask), axis=1)
    return values


##############

def ndarray2df(v):
    import pandas as pd

    df = pd.DataFrame(columns=['Subject', 'ROI', 'contrast', 'beta'])

    subj = [op.splitext(op.basename(fn))[0] for fn in subjects]
    con = [op.splitext(op.basename(fn))[0] for fn in contrasts]
    rois = [op.splitext(op.basename(fn))[0] for fn in ROIs]
    n1, n2, n3 = v.shape
    k=0
    for i1 in range(n1):
        for i2 in range(n2):
            for i3 in range(n3):
                df.loc[k] = pd.Series({'Subject': subj[i1],
                                       'contrast': con[i2],
                                       'ROI': rois[i3],
                                       'beta': v[i1, i2, i3]})
                k = k + 1
    return df


##############

if __name__ == '__main__':
 
    rootdir = os.getenv('ROOTDIR')
    if rootdir is None:
        rootdir = '/neurospin/unicog/protocols/IRMf/SyntMov_Fabre_Pallier_2014/scripts/python/ss_roi/testdata/'

    # Subjects' paths
    subjdir = op.join(rootdir, 'subjects')
    subjects = sorted(glob(op.join(subjdir, 'subj*')))

    # Contrast maps for each subject
    condir = 'analyse_smooth5/full_ancova_nbchar/'
    contrasts = ['scon_%04d.img' % x for x in (10, 11, 12, 13)]

    # location of individual localizer T map
    localizerf = 'analyse_smooth5/localizer_3/spmT_0001.img'
    THR_loc = 3.1  # statistical threshold for localizer's T-map

    # regions of interest (binary maps)
    roidir = op.join(rootdir, 'ROIs')
    ROIs = sorted(glob(op.join(roidir, '*.nii')))


    # extract data and save in csv files
    v1 = get_data_in_rois_method1(ROIs, subjects, contrasts, condir)
    df1 = ndarray2df(v1)
    df1.to_csv('method1.csv')

    v2 = get_data_in_rois_method2(ROIs, subjects, contrasts, condir, localizerf, THR_loc)
    df2 = ndarray2df(v2)
    df2.to_csv('method2.csv')

    v3 = get_data_in_rois_method3(ROIs, subjects, contrasts, condir, localizerf, 10)
    df3 = ndarray2df(v3)
    df3.to_csv('method3.csv')

    print 'you can now execture plot.R in R'

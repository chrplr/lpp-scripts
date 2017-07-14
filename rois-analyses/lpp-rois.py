#! /usr/bin/env python
# Time-stamp: <2017-07-13 16:56:08 cp983411>

"""
Extract data from contrasts maps in the intersections of a priori ROIs
and subject-specific localizer masks.
"""

import sys
from glob import glob
import os
import os.path as op
import pandas as pd

import numpy as np
import nibabel
from nilearn.input_data import NiftiMapsMasker
from nilearn.masking import intersect_masks

from nilearn.masking import apply_mask
from scipy.stats import scoreatpercentile
from nilearn.plotting import plot_roi



def basenames(files):
    return [op.splitext(x)[0] for x in [op.basename(op.splitext(f)[0]) for f in files]]

if __name__ == '__main__':
    rootdir = os.getenv('DATA_DIR')
    if rootdir is None:
        rootdir = '/home/jth99/lpp'

    images = sorted(glob(op.join(rootdir, '*effsize*.nii')))
    labels = basenames(images)
    u = [x.split('_') for x in labels]
    subj = [x[-1] for x in u]
    con = [x[0] for x in u]
    
    ROIs = sorted(glob(op.join('our-masks', '*.nii')))
    roi_names = basenames(ROIs)
    
    # extract data 
    masker = NiftiMapsMasker(ROIs)
    values = masker.fit_transform(images)

    # save it into a pandas DataFrame
    df = pd.DataFrame(columns=['subject', 'con', 'ROI', 'beta'])

    n1, n2 = values.shape
    k = 0
    for i1 in range(n1):
        for i2 in range(n2):
             df.loc[k] = pd.Series({'subject': subj[i1],
                                    'con': con[i1],
                                    'ROI': roi_names[i2],
                                    'beta': values[i1, i2]})
             k = k + 1
    df.to_csv('method1.csv', index=False)

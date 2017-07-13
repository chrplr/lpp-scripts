#! /usr/bin/env python
# Time-stamp: <2017-07-13 08:41:34 cp983411>

import os
import os.path as op
import glob

import pandas as pd
import nibabel
from nistats.second_level_model import SecondLevelModel
from nilearn import plotting
from scipy.stats import norm
import matplotlib.pyplot as plt


def create_one_sample_t_test(name, maps, smoothing_fwhm=8.0):
    model = SecondLevelModel(smoothing_fwhm=smoothing_fwhm)
    design_matrix = pd.DataFrame([1] * len(maps),
                                 columns=['intercept'])
    print(design_matrix)
    model = model.fit(maps,
                      design_matrix=design_matrix)
    z_map = model.compute_contrast(output_type='z_score')
    nibabel.save(z_map, "group_{}.nii.gz".format(name))

    p_val = 0.001
    z_th = norm.isf(p_val)
    z_th = 5.5
    display = plotting.plot_glass_brain(
        z_map, threshold=z_th,
        colorbar=True,
        plot_abs=False,
        display_mode='lzry',
        title=name)
    display.savefig("group_{}".format(name))

if __name__ == '__main__':
    DATA_DIR = os.getenv('DATA_DIR')
    assert(DATA_DIR is not None)
    cons = ('bottomup_o', 'f0_o', 'wordrate_o', 'mwe_o', 'freq_o', 'rms')
    for con in cons:
        mask = op.join(DATA_DIR, '%s_effsize*.nii.gz' % con)
        maps = glob.glob(mask)
        if maps == []:
            print("%s : no file with this mask" % mask)
        else:
            create_one_sample_t_test(con, maps)

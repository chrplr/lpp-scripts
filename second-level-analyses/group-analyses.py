#! /usr/bin/env python
# Time-stamp: <2017-06-17 17:32:32 cp983411>

import glob
import pandas as pd
from nilearn import plotting
from scipy.stats import norm
import matplotlib.pyplot as plt

from nistats.second_level_model import SecondLevelModel

def create_one_sample_t_test(name, maps, smoothing_fwhm=8.0):
    model = SecondLevelModel(smoothing_fwhm)
    design_matrix = pd.DataFrame([1] * len(maps),
                                 columns=['intercept'])
    model = model.fit(maps,
                                   design_matrix=design_matrix)
    z_map = model.compute_contrast(output_type='z_score')

    p_val = 0.001
    z_th = norm.isf(p_val)
    display = plotting.plot_glass_brain(
        z_map, threshold=z_th,
        colorbar=True,
        plot_abs=False,
        display_mode='z',
        title=name)
    display.savefig("group_{}".format(name))

if __name__ == '__main__':
    cons = ('bottomup_o', 'f0_o', 'wordrate_o', 'mwe_o', 'freq_o', 'rms')
    for con in cons:
        maps = glob.glob('{}_effsize*.nii.gz'.format(con))
        create_one_sample_t_test(con, maps)

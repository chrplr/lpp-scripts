#! /usr/bin/env python
# Time-stamp: <2017-07-18 21:32:05 cp983411>

import os
import os.path as op
import glob

import pandas as pd
import numpy as np
import nibabel as nib
from joblib import dump, load
from joblib import Parallel, delayed

import matplotlib.pyplot as plt

import nistats
from nistats.first_level_model import FirstLevelModel
from nistats.design_matrix import plot_design_matrix
from nilearn.plotting import plot_stat_map
from nilearn.plotting import plot_glass_brain

def process_subject(inputpath, subjid, dtx_mat, outputpath):
    subjglm = op.join(outputpath, "cache", "glm_{}".format(subjid))
    subjid = str(subjid)    
    if op.isfile(subjglm):
        print('Loading already saved model for subject %s' % subjid)
        fmri_glm = load(subjglm)  # the model has already been estimated
    else:  
        # else, we create and estimate it
        print('Creating model for subject %s' % subjid)
        imgs = sorted(glob.glob(op.join(inputpath, subjid, "analysis", "res*_medn_afw.nii")))
        if len(imgs) != 9:
            return
        
        fmri_glm = FirstLevelModel(
            t_r=2.0,
            hrf_model='spm',
            #mask='mask_ICV.nii',
            noise_model='ar1',
            period_cut=128.0,
            smoothing_fwhm=0,
            minimize_memory=True,
            #memory='/mnt/ephemeral/cache',
            memory=None,
            verbose=2,
            n_jobs=1)
    
        # creating and estimating the model
        fmri_glm = fmri_glm.fit(imgs, design_matrices=dtx_mat)
        # saving it as a pickle object
        dump(fmri_glm, subjglm)

    # creating the maps for each individual predictor
    # this assumes the same predictors for each session
    print('Computing contrasts for subject %s', subjid)
    contrasts = {}
    con_names = [i for i in dtx_mat[0].columns]
    ncon = len(con_names)
    con = np.eye(ncon)
    for i, name in enumerate(con_names):
        contrasts[name] = con[i,:]


    for name, val in contrasts.items():
        z_map = fmri_glm.compute_contrast(val, output_type='z_score')
        eff_map = fmri_glm.compute_contrast(val, output_type='effect_size')
        #std_map = fmri_glm.compute_contrast(val, output_type='stddev')
        nib.save(z_map, op.join(outputpath, '%s_%s_zmap.nii.gz' % (name, subjid)))
        nib.save(eff_map, op.join(outputpath, '%s_%s_effsize.nii.gz'% (name, subjid)))
        display = None
        display = plot_glass_brain(z_map, display_mode='lzry', threshold=3.1, colorbar=True, title=name)
        display.savefig(op.join(outputpath, '%s_%s_glassbrain.png' % (name, subjid)))
        display.close()

 

if __name__ == '__main__':
    DATA_DIR = os.getenv('DATA_DIR')  # where the invidual subjects directory are
    OUTPUT_DIR = os.getenv('OUTPUT_DIR')  # where the results will be  
    DESIGNMAT_DIR = os.getenv('DESIGNMAT_DIR')  # where the design matrices are
    
    if DATA_DIR is None:
        DATA_DIR = '/home/jth99/lpp'

    if OUTPUT_DIR is None:
        OUTPUT_DIR = '/home/cp623/lpp-individual-results'

    if not op.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
        
    if not op.isdir(op.join(OUTPUT_DIR, 'cache')):
        os.mkdir(op.join(OUTPUT_DIR, 'cache'))

    if DESIGNMAT_DIR is None:
        DESIGNMAT_DIR = '.'  # localdir
    
    design_files = sorted(glob.glob(op.join('dmtx_?_ortho.csv')))
    dtx_mat0 = [pd.read_csv(df) for df in design_files]
    dtx_mat = [ ((dtx - dtx.mean()) / dtx.std()) for dtx in dtx_mat0]
    for i, d in enumerate(dtx_mat):
        plt.plot(d)
        plt.savefig('dtx_plot_%s.png' % str(i + 1))
        plt.close()
        print('Run %d. Correlation matrix:' % (i + 1))
        print(np.round(np.corrcoef(d.T), 5))
        d['constant'] = np.ones(len(d))

    subjlist = [57, 58, 59, 61, 62, 63, 64, 65, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 86, 87, 88, 89, 91, 92, 93, 94, 95, 96, 97, 99, 100, 101, 103, 104]
    
    if os.getenv('SEQUENTIAL') is not None:
        for s in subjlist:
            process_subject(DATA_DIR, s, dtx_mat, OUTPUT_DIR)
    else:
        Parallel(n_jobs=-2)(delayed(process_subject)(DATA_DIR, s, dtx_mat, OUTPUT_DIR) for s in subjlist)

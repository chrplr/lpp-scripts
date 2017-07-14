#! /usr//bin/env python
# Time-stamp: <2017-06-15 14:31:04 cp983411>

import glob
import os.path as op
import numpy as np
import numpy.linalg as npl
from numpy import (corrcoef, around, array, dot, identity, mean)
from numpy import column_stack as cbind
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def ortho_proj(Y, M):
    """ returns the orthogonal component of Y to the space spanned by M and the constant vector 1 """
    if M.ndim == 1:   # M is a vector but needs to be a 2-D matrix
        M = M[:, np.newaxis]
    I = np.ones(len(M))
    I = I[:, np.newaxis]
    M2 = np.hstack((I, M))  # adding the constant 
    betas,_,_,_ = npl.lstsq(M2, Y)
    Xc = np.dot(M2, betas)  # colinear component "residuals"
    Xo = Y - Xc
    return Xo


for r, f in enumerate(glob.glob('dmtx_?.csv')):
    print("Run #%d:" % r)
    df = pd.read_csv(f, sep='\t')
    M1 = df.as_matrix().T
    print(around(corrcoef(M1), 2))

    display = sns.pairplot(df)
    fn, ext = op.splitext(f)
    display.savefig(fn + '_nonortho.png')
    
    X1 = df.rms - mean(df.rms)
    X2 = ortho_proj(df.f0, df.rms)
    X3 = ortho_proj(df.wordrate, cbind((df.rms, df.f0)))
    X4 = ortho_proj(df.freq, cbind((df.rms, df.f0, df.wordrate)))
    X5 = ortho_proj(df.mwe, cbind((df.rms, df.f0, df.wordrate)))
    X6 = ortho_proj(df.bottomup, cbind((df.rms, df.f0, df.wordrate)))


    M2 = cbind((X1, X2, X3, X4, X5, X6))
    newdf = pd.DataFrame(data=M2,
                         columns=['rms', 'f0_o', 'wordrate_o', 'freq_o', 'mwe_o', 'bottomup_o'])
    fname, ext  = op.splitext(f)
    newfname = fname + '_ortho' + ext
    newdf.to_csv(newfname, index=False)
    display = sns.pairplot(newdf)
    display.savefig(fn + '_ortho.png')

    print(around(corrcoef(M2.T), 2))
    plt.close('all')

    

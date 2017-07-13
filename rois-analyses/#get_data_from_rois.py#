
#! /usr/bin/env python
# Time-stamp: <2015-11-19 15:11 christophe@pallier.org>


"""
Extracts voxels from masks (ROIs) in a series of maps,
creating one text file per mask
"""
 
import glob
import os
import os.path as op
import nibabel
import numpy as np
from collections import OrderedDict

def get_rootdir():
    rootdir = os.getenv('ROOTDIR')
    if rootdir is None:
        rootdir = '/home/jth99/lpp'
    return rootdir


def get_rois():
    """
    return a dictionary roi_name:path_of_corresponding_mask_file
    """


    rois = "aSTS.nii  IFGoper.nii  IFGtri.nii  pSTS.nii  TPJ.nii  AngG.nii  dPrC.nii  IFGorb.nii   MTG.nii     SMA.nii   TP.nii".split()

    roi_path = op.join(get_rootdir(), 'rois-analyses/ROIs-masks')
    frois = [op.join(roi_path, '%s' % x) for x in rois]
    assert len(frois) != 0

    return OrderedDict(zip(rois, frois))


def get_maps_conditions_group_analysis():
    """
    returns an OrderedDict name:path_imgfile
    """
    from collections import OrderedDict

    condir  = op.join(get_rootdir(), '??/analysis/spm12/snl')
    conlist = [op.join(condir, 'con_%04d.nii' % x) for x in range(1, 7)]  # 6 con
    maps = [op.join(condir, con) for con in conlist]
    assert len(maps) != 0
    names = """
wordrate
freq
bottomup
mwe
rms
f0
""".split()

    return OrderedDict(zip(names, maps))


def extract_data_in_roi(scans, roi):
    """
    returns the values of voxels in scans that are inside the roi, as a matrix    (rows=voxels, columns=scans). 
    scans : list of 3D img files,
    roi : string, filename of mask file
    note: the current code assumes that mask and the scans have the same shape
    """
    mask = nibabel.load(roi).get_data() > 0
    data = np.zeros([mask.shape[0], mask.shape[1], mask.shape[2], len(scans)])
    for i in range(len(scans)):
        assert os.path.isfile(scans[i])
        img = nibabel.load(scans[i]).get_data()
        assert img.shape == mask.shape
        data[:, :, :, i] = img
    return data[mask, :]


def save_data_from_rois(maps, rois, prefix=''):
    """
    extract data from the scans listed in maps, in each roi
    from the dictionary rois, and save in one text file per roi

    maps: ordereddict names -> files
    roi : ordereddict names -> files
    prefix: prefix to be added in front of filenames
    """
    for nroi, froi in rois.iteritems():
        activations = extract_data_in_roi(maps.values(), froi)
        np.savetxt('%s%s.csv' % (prefix, nroi), activations,
                   delimiter=',',
                   header=",".join(maps.keys()), comments='')


if __name__ == '__main__':
    maps = get_maps_conditions_group_analysis()
    rois = get_rois()
    save_data_from_rois(maps, rois, prefix='all_')

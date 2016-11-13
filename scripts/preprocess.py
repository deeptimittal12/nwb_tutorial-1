#!/usr/bin/env python

import h5py
import numpy as np
import buzsaki_hc as bhc
import os.path as osp
import h5py
import matplotlib.pyplot as plt

RAWPATH = '/Users/smackesey/stm/data/crcns_hc/hc3/ec014.468'
RAWPOSPATH = osp.join(RAWPATH, 'ec014.468.whl')
INFILE = '/Users/smackesey/stm/wrk2/nwb_buz_nb/ec014.468.nwb'
OUTFILE = '/Users/smackesey/stm/wrk2/nwb_buz_nb/ec014.468.pp.h5'

pos = np.reshape( np.fromfile(RAWPOSPATH, sep=' '), (-1, 4) )[:-1]
pos = pos[:,:2]
data = h5py.File(INFILE, 'r')
outdata = h5py.File(OUTFILE, 'a')

# pos = data['/processing/position/Position/all/data']
# lfp = data['/processing/lfp/LFP/all/data']
# ca1_lfp = lfp[:,:64]
#
# from IPython import embed; embed()

# ds_lfp = bhc.downsample(ca1_lfp, 1250.0, 39.0625, True)
# ds_lfp = outdata['ds_lfp']

# from IPython import embed; embed()
# norm_lfp = bhc.normalize_channels(ds_lfp)
# filt_lfp = bhc.bandpass_filter(ds_lfp, 5.0, 11.0, 39.0625)

# from IPython import embed; embed()

# outdata['lfp_final'] = ds_lfp
# outdata['pos'] = pos

# from IPython import embed; embed()
lfp = outdata['lfp_final']

from IPython import embed; embed()

drop_indices = [ i for i in range(pos.shape[0])
    if pos[i][0] == -1 ]
clean_lfp = np.delete(lfp, drop_indices, axis=0)
clean_pos = np.delete(pos, drop_indices, axis=0)

from IPython import embed; embed()


# plt.plot(pos[:,0], pos[:,1])
# plt.show()

# rot_pos, rot_neg_one = hc2.rotate_pos_data(pos_file_content)
# hc2.replace_head_neg_ones_with_nan(rot_pos, rot_neg_one)
# trial_indices_obj = hc2.get_trial_indices(rot_pos[:,0], MIDDLE_ROT_TRACK)

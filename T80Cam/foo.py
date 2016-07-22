from skimage import io, transform

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import os

offset = np.load('/Volumes/TiagoHD2/Documents/data/T80S/20160503/register_offset.npy')

flist = np.loadtxt('/Volumes/TiagoHD2/Documents/data/T80S/20160503/ofile.lis',dtype='S')


flist = flist[2:29]
ox = offset[0][2:29]-offset[0][2]
oy = offset[1][2:29]-offset[1][2]

for i,img in enumerate(flist):
# i = len(flist)-1
# img = flist[i]

    hdu = fits.open(img)
    offset = transform.SimilarityTransform(translation=(ox[i], oy[i]))
    img0_warped = transform.warp(hdu[0].data, inverse_map=offset)
    hdu[0].data = img0_warped

    path = os.path.dirname(img)
    fname = os.path.basename(img)
    print 'Writing registered image to %s' % 'r'+fname
    hdu.writeto(os.path.join(path,'r'+fname))

# import pyds9 as ds9
#
# d = ds9.ds9()
#
# d.set_np2arr(img0_warped)


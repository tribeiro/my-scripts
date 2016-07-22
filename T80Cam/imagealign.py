
import sys,os
import numpy as np
from astropy.io import fits
import image_registration

def main(argv):

    flist = np.loadtxt('/Volumes/TiagoHD2/Documents/data/T80S/20160503/ofile.lis',dtype='S')

    refimg = flist[0]
    offset = np.zeros((2,len(flist)))

    img1 = fits.getdata(refimg)

    for i in range(1,len(flist)):
        print 'Working on %s' % flist[i]
        img2 = fits.getdata(flist[i])
        reg = image_registration.chi2_shift(img1,img2)
        offset[0][i] = reg[0]
        offset[1][i] = reg[1]

    np.save('/Volumes/TiagoHD2/Documents/data/T80S/20160503/register_offset.npy',offset)

    print 'done'
    
    return 0

if __name__ == '__main__':
    main(sys.argv)
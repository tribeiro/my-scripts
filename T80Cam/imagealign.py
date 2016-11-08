
import sys,os
import numpy as np
from astropy.io import fits
import imreg_dft as ird

def main(argv):

    flist = np.loadtxt('/Users/tiago/Documents/T80S/imagealign.lis',dtype='S')

    refimg = flist[0]
    offset = np.zeros((2,len(flist)))

    img1 = fits.getdata(refimg)
    ix,iy = img1.shape
    img1 = img1[ix/2-500:ix/2+500,iy/2-500:iy/2+500]

    for i in range(1,len(flist)):
        print 'Working on %s' % flist[i]
        img2 = fits.getdata(flist[i])[ix/2-500:ix/2+500,iy/2-500:iy/2+500]

        result = ird.translation(img1, img2) #, constraints={'tx': (100,0), 'ty': (100,0)})
        tvec = result["tvec"].round(4)
        print tvec
        # reg = image_registration.chi2_shift(img1,rebin(img2,(nx/4,ny/4)))
        # offset[0][i] = reg[0]
        # offset[1][i] = reg[1]

    # np.save('/Users/tiago/Documents/T80S/register_offset.npy',offset)

    print 'done'
    
    return 0

if __name__ == '__main__':
    main(sys.argv)
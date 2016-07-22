import sys, os
import numpy as np
import pylab as py
from astropy.io import fits

def main(argv):

    specfile = "/Volumes/TiagoHD2/Documents/template/s_coelho14_sed/t08000_g+1.5_p00p00_sed.fits"
    hdu = fits.open(specfile)

    wave = 10.**(hdu[0].header['CRVAL1']+np.arange(0,len(hdu[0].data))*hdu[0].header['CD1_1'])

    mask = np.bitwise_and(wave > 6530,
                          wave < 6590)
    py.semilogx(wave,
            hdu[0].data)

    line = hdu[0].data[mask]
    line -= line[0]
    line *= -1

    for scale in [2.0,5.0,10.]:
        flux = hdu[0].data
        flux[mask]+=line*scale

        py.semilogx(wave,
                    flux)

    py.show()

if __name__ == '__main__':
    main(sys.argv)
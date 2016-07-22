
import sys,os
import numpy as np
import pylab as py
from astropy.io import fits

def main(argv):

    _path = os.path.expanduser('~/iCloud/Dropbox/Documents/Jana')

    sdss_spec = 'alespec-0404-51812-0141.fits'
    jplus_spec = 'alespec-0404-51812-0141.JPLUS'

    jplus_system = {'F348': (3485., 508.),
                    'F378': (3785., 168.),
                    'F395': (3950., 100.),
                    'F410': (4100., 200.),
                    'F430': (4300., 200.),
                    'F515': (5150., 200.),
                    'F660': (6600., 125.),
                    'F861': (8610., 400.),
                    'g_sdss': (4750., 1500.),
                    'i_sdss': (7725., 1550.),
                    'r_sdss': (6250., 1500.),
                    'z_sdss': (9150., 1700.)}

    # for filtername in jplus_system.keys():
    #     fdef = jplus_system[filtername]
    #     py.plot([fdef[0]-fdef[1],fdef[0]-fdef[1],
    #              fdef[0]+fdef[1],fdef[0]+fdef[1]],
    #             [0.,1.,1.,0.],
    #             'r-')

    spec = fits.open(os.path.join(_path,sdss_spec))
    jpspec = np.loadtxt(os.path.join(_path,jplus_spec),dtype='S')
    jspec_dict = {}
    for flux in jpspec:
        jspec_dict[flux[1]] = flux[2]

    print jspec_dict

    wave = np.arange(len(spec[0].data))*spec[0].header['CDELT1']+spec[0].header['CRVAL1']
    py.plot(wave,spec[0].data/spec[0].data.max())

    data = np.zeros((3,len(jspec_dict)))

    for i,band in enumerate(jspec_dict.keys()):
        data[0][i],data[1][i],data[2][i] = jplus_system[band][0],jspec_dict[band],jplus_system[band][1]
    print data
    py.errorbar(data[0],
                data[1]/spec[0].data.max(),
                xerr=data[2]/2.,
                fmt='ro')

    py.show()


    return 0


if __name__ == '__main__':
    main(sys.argv)
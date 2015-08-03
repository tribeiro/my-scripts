#! /usr/bin/env python

__author__ = 'tiago'

'''
    Make tilling pattern for S-PLUS.
'''

import sys,os
import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
from APLUS_Pointings import check_inside_survey
import matplotlib.cm as cm
import pylab as py
import healpy as H

def main(argv):

    theta = 1.42 * np.pi /180. # FoV size in radians
    a = 2. * np.tan(theta / 2.) # Size projected in the sky

    n = 0 # Zones in the sky (Dec) 0 = equator

    deltaN = 0.

    splusS = []
    scriptS = ''

    splusN = []
    scriptN = ''

    NTileS = 0
    NTileN = 0

    splusLimits_S = [ {'ra_min' : 0.0*u.hourangle,
                       'ra_max' : 4.0*u.hourangle,
                       'dec_max' : -10.0*u.degree,
                       'dec_min' : -30.0*u.degree},

                      {'ra_min' : 21.5*u.hourangle,
                       'ra_max' : 23.99*u.hourangle,
                       'dec_max' : -10.0*u.degree,
                       'dec_min' : -45.0*u.degree},

                       {'ra_min' : 0.0*u.hourangle,
                       'ra_max' : 6.0*u.hourangle,
                       'dec_max' : -30.0*u.degree,
                       'dec_min' : -80.0*u.degree},

                      {'ra_min' : 20.0*u.hourangle,
                       'ra_max' : 23.99*u.hourangle,
                       'dec_max' : -45.0*u.degree,
                       'dec_min' : -80.0*u.degree}
    ]

    splusLimits_N = [ {'ra_min' : 10.*u.hourangle,
                       'ra_max' : 13.5*u.hourangle,
                       'dec_max' : 0.0*u.degree,
                       'dec_min' : -25.0*u.degree},
                      {'ra_min' : 10.5*u.hourangle,
                       'ra_max' : 14.5*u.hourangle,
                       'dec_max' : 15.0*u.degree,
                       'dec_min' : 00.0*u.degree},
                      {'ra_min' : 12.0*u.hourangle,
                       'ra_max' : 14.5*u.hourangle,
                       'dec_max' : 30.0*u.degree,
                       'dec_min' : 15.0*u.degree}
    ]


    NSIDE = 32
    raMap = np.zeros(H.nside2npix(NSIDE))
    decMap = np.zeros(H.nside2npix(NSIDE))
    surveyMap = np.zeros(H.nside2npix(NSIDE)) #np.ma.masked_array(x, mask=[0, 0, 0, 1, 0])


    for i in range(H.nside2npix(NSIDE)):

        raMap[i],decMap[i] = H.pix2ang(NSIDE,i)

    raMap -= np.pi/2.
    decMap -= np.pi
    for area in splusLimits_S:
        print area['ra_min'].to(u.radian),area['ra_max'].to(u.radian),area['dec_min'].to(u.radian),area['dec_max'].to(u.radian)
        ra_tmpMap = np.bitwise_and( raMap > area['ra_min'].to(u.radian).value,
                                    raMap < area['ra_max'].to(u.radian).value)
        dec_tmpMap = np.bitwise_and( decMap > area['dec_min'].to(u.radian).value,
                                     decMap < area['dec_max'].to(u.radian).value)
        mask = np.bitwise_and(ra_tmpMap,
                              dec_tmpMap)
        surveyMap[mask] = 1.

    _path = os.path.expanduser('~/Develop/SMAPs/')

    file_area = 'lambda_sfd_ebv.fits'
    map_area = H.read_map(os.path.join(_path, file_area))
    H.mollview(map_area, coord=['G', 'E'], cmap=cm.gray_r, max=1, cbar=False, notext=True,
               title='J-PAS/J-PLUS/S-PLUS Survey Area',hold=True)

    surveyMap = H.ma(surveyMap)#,surveyMap==0)
    surveyMap.mask = surveyMap==0
    # H.mollview(surveyMap, cmap=cm.gray_r, cbar=False, notext=True,
    #            title='J-PAS/J-PLUS/S-PLUS Survey Area',hold=True)

    H.graticule()

    py.show()

    return 0

if __name__ == '__main__':
    main(sys.argv)

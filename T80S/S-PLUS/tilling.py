#! /usr/bin/env python

__author__ = 'tiago'

'''
    Make tilling pattern for S-PLUS.
'''

import sys,os
import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord

def main(argv):

    theta = 2.0 * np.pi /180. # FoV size in radians
    a = 2. * np.tan(theta / 2.) # Size projected in the sky

    n = 0 # Zones in the sky (Dec) 0 = equator

    deltaN = 0.

    splus = ''
    script = ''

    NTile = 1

    while deltaN < 75.*np.pi/180.:

        delta0 = deltaN - theta/2.
        mn = np.floor( 2. * np.pi * np.cos(delta0) / theta ) + 1.0 # number of cells on zone n

        dalpha = 24. / mn

        alpha = np.arange(0.,24.,dalpha)

        for a in alpha:
            c = SkyCoord(ra=a*u.hourangle,
                         dec=-deltaN*u.radian,
                         frame='icrs')
            if c.dec > -10.*u.degree or c.dec < -70.*u.degree:
                print 'Skipping tile@ %s...'%c.to_string('hmsdms',sep=':')
            elif c.dec > -18.*u.degree and c.ra < 180.*u.degree:
                print 'Skipping tile@ %s...'%c.to_string('hmsdms',sep=':')
            elif c.dec > -18*u.degree and c.ra < 320*u.degree:
                print 'Skipping tile@ %s...'%c.to_string('hmsdms',sep=':')
            elif c.ra > 105.*u.degree and c.ra < 295*u.degree:
                print 'Skipping tile@ %s...'%c.to_string('hmsdms',sep=':')
            elif c.dec < -60.*u.degree and ( (c.ra > 105.*u.degree) and (c.ra < 300.*u.degree)):
                print 'Skipping tile@ %s...'%c.to_string('hmsdms',sep=':')
            elif c.dec > -45*u.degree and ( (c.ra > 65*u.degree) and (c.ra < 240*u.degree)):
                print 'Skipping tile@ %s...'%c.to_string('hmsdms',sep=':')
            elif c.dec > -35*u.degree and ( (c.ra > 40*u.degree) and c.ra < 240*u.degree):
                print 'Skipping tile@ %s...'%c.to_string('hmsdms',sep=':')
            else:
                print 'Adding tile@ %s...'%c.to_string('hmsdms',sep=':')
                splus += 'SPLUS%05i %s\n'%(NTile,c.to_string('hmsdms',sep=':'))
                script+='get FoV(T80Cam) %s\nset color=red\n'%c.to_string('hmsdms',sep=':')
                NTile+=1

        deltaN = (np.arctan(np.tan(deltaN + theta/2.)*np.cos(dalpha)) + theta/2.)

    fp = open('/Users/tiago/Dropbox/Documents/T80S/S-PLUS/script_splus_south.ajs','w')
    fp.write(script)
    fp.close()

    fp = open('/Users/tiago/Dropbox/Documents/T80S/S-PLUS/splus_tiles_south.txt','w')
    fp.write(splus)
    fp.close()

    return 0

if __name__ == '__main__':
    main(sys.argv)
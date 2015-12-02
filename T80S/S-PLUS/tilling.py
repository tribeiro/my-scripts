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

def main(argv):

    theta = 1.42 * np.pi /180. # FoV size in radians
    a = 2. * np.tan(theta / 2.) # Size projected in the sky

    n = 0 # Zones in the sky (Dec) 0 = equator

    deltaN = 0.

    splusS = []
    scriptS = ''

    splusN = []
    scriptN = ''

    s82 = []
    scriptS82 = ''

    NTileS = 0
    NTileN = 0
    NTilesS82 = 0

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

    stripe82 = [{'ra_min' : 20*u.hourangle,
                 'ra_max' : 24*u.hourangle,
                 'dec_max' : +2.*u.degree,
                 'dec_min' : -2.*u.degree} ,
                {'ra_min' : 0.*u.hourangle,
                 'ra_max' : 4*u.hourangle,
                 'dec_max' : +2.*u.degree,
                 'dec_min' : -2.*u.degree} ,
                ]

    area = 0.

    for reg in splusLimits_S:
        area += np.abs( (np.sin(reg['dec_max'].to(u.radian)) - np.sin(reg['dec_min'].to(u.radian)))*u.radian * (reg['ra_max'].to(u.radian) - reg['ra_min'].to(u.radian)) )

    for reg in splusLimits_N:
        area += np.abs( (np.sin(reg['dec_max'].to(u.radian)) - np.sin(reg['dec_min'].to(u.radian)))*u.radian * (reg['ra_max'].to(u.radian) - reg['ra_min'].to(u.radian)) )

    print 'Total area: %s'%area.to(u.degree**2)

    area = 0.

    for reg in stripe82:
        area += np.abs( (np.sin(reg['dec_max'].to(u.radian)) - np.sin(reg['dec_min'].to(u.radian)))*u.radian * (reg['ra_max'].to(u.radian) - reg['ra_min'].to(u.radian)) )

    print 'Stripe 82 area: %s'%area.to(u.degree**2)
    # return 0

    # while deltaN < 10.*np.pi/180.:
    for deltaN in [0.70*np.pi/180.]:
        delta0 = deltaN - theta/2.
        mn = np.floor( 2. * np.pi * np.cos(delta0) / theta ) + 1.0 # number of cells on zone n

        dalpha = 24. / mn

        alpha = np.arange(0.,24.,dalpha)

        for a in alpha:
            c1 = SkyCoord(ra=a*u.hourangle,
                         dec=-deltaN*u.radian,
                         frame='icrs')
            c2 = SkyCoord(ra=a*u.hourangle,
                         dec=deltaN*u.radian,
                         frame='icrs')

            if check_inside_survey(c1.ra,c1.dec,splusLimits_S):
                #print 'Adding tile@ %s...'%c.to_string('hmsdms',sep=':')
                splusS.append(c1.to_string('hmsdms',sep=':'))
                scriptS+='get FoV(T80Cam) %s\nset color=red\n'%c1.to_string('hmsdms',sep=':')
                NTileS+=1

            if check_inside_survey(c2.ra,c2.dec,splusLimits_S):
                #print 'Adding tile@ %s...'%c.to_string('hmsdms',sep=':')
                splusS.append(c2.to_string('hmsdms',sep=':'))
                scriptS+='get FoV(T80Cam) %s\nset color=red\n'%c2.to_string('hmsdms',sep=':')
                NTileS+=1

            if check_inside_survey(c1.ra,c1.dec,splusLimits_N):
                splusN.append(c1.to_string('hmsdms',sep=':'))
                scriptN+='get FoV(T80Cam) %s\nset color=blue\n'%c1.to_string('hmsdms',sep=':')
                NTileN+=1

            if check_inside_survey(c2.ra,c2.dec,splusLimits_N):
                splusN.append(c2.to_string('hmsdms',sep=':'))
                scriptN+='get FoV(T80Cam) %s\nset color=blue\n'%c2.to_string('hmsdms',sep=':')
                NTileN+=1

            if check_inside_survey(c1.ra,c1.dec,stripe82):
                s82.append(c1.to_string('hmsdms',sep=':'))
                scriptS82+='get FoV(T80Cam) %s\nset color=blue\n'%c1.to_string('hmsdms',sep=':')
                NTilesS82+=1

            # if c2.dec.to(u.radian).value > theta and check_inside_survey(c2.ra,c2.dec,stripe82):
            if check_inside_survey(c2.ra,c2.dec,stripe82):
                s82.append(c2.to_string('hmsdms',sep=':'))
                scriptS82+='get FoV(T80Cam) %s\nset color=blue\n'%c2.to_string('hmsdms',sep=':')
                NTilesS82+=1


            '''
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
            '''

        deltaN = (np.arctan(np.tan(deltaN + theta/2.)*np.cos(dalpha/2.)) + theta/2.)

    fp = open(os.path.expanduser('~/Dropbox/Documents/T80S/S-PLUS/script_splus_south.ajs'),'w')
    fp.write(scriptS)
    fp.close()

    fp = open(os.path.expanduser('~/Dropbox/Documents/T80S/S-PLUS/script_splus_north.ajs'),'w')
    fp.write(scriptN)
    fp.close()

    fp = open(os.path.expanduser('~/Dropbox/Documents/T80S/S-PLUS/script_stripe82.ajs'),'w')
    fp.write(scriptS82)
    fp.close()

    fp = open(os.path.expanduser('~/Dropbox/Documents/T80S/S-PLUS/splus_tiles.txt'),'w')
    NTile = 1

    for tile in splusS:
        fp.write('SPLUS_%04i %s\n'%(NTile,tile))
        NTile+=1

    for tile in splusN:
        fp.write('SPLUS_%04i %s\n'%(NTile,tile))
        NTile+=1


    fp.close()

    fp = open(os.path.expanduser('~/Dropbox/Documents/T80S/S-PLUS/stripe82_tiles.txt'),'w')
    NTile = 1

    for tile in s82:
        fp.write('STRIPE82_%04i %s\n'%(NTile,tile))
        NTile+=1

    fp.close()

    return 0

if __name__ == '__main__':
    main(sys.argv)
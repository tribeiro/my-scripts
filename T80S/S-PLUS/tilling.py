#! /usr/bin/env python

__author__ = 'tiago'

'''
    Make tilling pattern for S-PLUS.
'''

import sys,os
import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
from APLUS_Pointings import check_inside_survey, check_inside_survey_gal

def around_ecliptic(coord, distance):
    ecliptic = SkyCoord(ra = coord.ra, dec = 20.*u.degree*np.sin(coord.ra.to(u.rad).value))
    return coord.separation(ecliptic).to(u.degree).value < distance

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

    smc = []
    scriptSMC = ''

    ecliptic = []
    scriptEcliptic = ''

    ecliptic = []
    scriptGalactic = ''

    chimera_sched_SMC = '''programs:

  - name: CALIB
    pi: Tiago Ribeiro   # (optional)
    priority: 1         # (optional)
    actions:'''

    chimera_sched_action = '''
      - action: point
        ra: \"{ra}\"
        dec: \"{dec}\"
      - action: autofocus
        start: 100
        step: 0
        filter: R
        exptime: 10
      - action: expose
        frames: 12
        exptime: 13
        imageType: OBJECT
        shutter: OPEN
        filter: G
        objectName: SMC grid {ngrid}
        filename: "SMC-$DATE-$TIME"
      - action: expose
        frames: 12
        exptime: 20
        imageType: OBJECT
        shutter: OPEN
        filter: R
        objectName: SMC grid {ngrid}
        filename: "SMC-$DATE-$TIME"
      - action: expose
        frames: 3
        exptime: 26
        imageType: OBJECT
        shutter: OPEN
        filter: I
        objectName: SMC grid {ngrid}
        filename: "SMC-$DATE-$TIME"
'''

    NTileS = 0
    NTileN = 0
    NTilesS82 = 0
    NTilesSMC = 0
    splusLimits_S = [ {'ra_min' : 21.7*u.hourangle,
                       'ra_max' : 23.99*u.hourangle,
                       'dec_max' :   1.0*u.degree,
                       'dec_min' : -15.0*u.degree},

                      {'ra_min' : 21.0*u.hourangle,
                       'ra_max' : 23.99*u.hourangle,
                       'dec_max' : -15.0*u.degree,
                       'dec_min' : -30.0*u.degree},

                        {'ra_min' : 0.0*u.hourangle,
                       'ra_max' : 2.*u.hourangle,
                       'dec_max' : -15.0*u.degree,
                       'dec_min' : -30.0*u.degree},

                       {'ra_min' : 0.0*u.hourangle,
                       'ra_max' : 2.7*u.hourangle,
                       'dec_max' : -30.0*u.degree,
                       'dec_min' : -60.0*u.degree},

                      {'ra_min' : 20.0*u.hourangle,
                       'ra_max' : 23.99*u.hourangle,
                       'dec_max' : -30.0*u.degree,
                       'dec_min' : -60.0*u.degree},

                       {'ra_min' : 0.0*u.hourangle,
                       'ra_max' : 5.4*u.hourangle,
                       'dec_max' : -60.0*u.degree,
                       'dec_min' : -80.0*u.degree},

                      {'ra_min' : 18.6*u.hourangle,
                       'ra_max' : 23.99*u.hourangle,
                       'dec_max' : -60.0*u.degree,
                       'dec_min' : -80.0*u.degree}

    ]

    splusLimits_N = [ {'ra_min' : 10.*u.hourangle,
                       'ra_max' : 12.*u.hourangle,
                       'dec_max' :  20.0*u.degree,
                       'dec_min' : -25.0*u.degree},

                      {'ra_min' : 12.0*u.hourangle,
                       'ra_max' : 14.0*u.hourangle,
                       'dec_max' :  30.0*u.degree,
                       'dec_min' : -15.0*u.degree}
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

    SMC = [{'ra_min': (0. + 15 / 60.) * u.hourangle,
            'ra_max': 6.5 * u.hourangle,
            'dec_max': -68.5 * u.degree,
            'dec_min': -75. * u.degree},
           {'ra_min': 4.5 * u.hourangle,
            'ra_max': 6.5 * u.hourangle,
            'dec_max': -62. * u.degree,
            'dec_min': -70. * u.degree}
           ]

    Galactic = [{'l_min' : 240.,
                 'l_max' : 300.,
                 'b_min' : -20.,
                 'b_max' : +20.}]

    area = 0.

    # for reg in splusLimits_S:
    #     area += np.abs( (np.sin(reg['dec_max'].to(u.radian)) - np.sin(reg['dec_min'].to(u.radian)))*u.radian * (reg['ra_max'].to(u.radian) - reg['ra_min'].to(u.radian)) )
    #
    # for reg in splusLimits_N:
    #     area += np.abs( (np.sin(reg['dec_max'].to(u.radian)) - np.sin(reg['dec_min'].to(u.radian)))*u.radian * (reg['ra_max'].to(u.radian) - reg['ra_min'].to(u.radian)) )
    #
    # print 'Total area: %s'%area.to(u.degree**2)
    #
    # area = 0.
    #
    # for reg in stripe82:
    #     area += np.abs( (np.sin(reg['dec_max'].to(u.radian)) - np.sin(reg['dec_min'].to(u.radian)))*u.radian * (reg['ra_max'].to(u.radian) - reg['ra_min'].to(u.radian)) )

    for reg in SMC:
        area += np.abs( (np.sin(reg['dec_max'].to(u.radian)) - np.sin(reg['dec_min'].to(u.radian)))*u.radian * (reg['ra_max'].to(u.radian) - reg['ra_min'].to(u.radian)) )

    print 'Stripe 82 area: %s'%area.to(u.degree**2)
    # return 0

    while deltaN < 85.*np.pi/180.:
    # for deltaN in [0.70*np.pi/180.]:
        delta0 = deltaN - theta/2.
        mn = np.floor( 2. * np.pi * np.cos(delta0) / theta ) + 1.0 # number of cells on zone n

        dalpha = 24. / mn

        alpha = np.arange(0.,24.,dalpha)
        print '->',deltaN,85.*np.pi/180.

        for a in alpha:
            c1 = SkyCoord(ra=a*u.hourangle,
                         dec=-deltaN*u.radian,
                         frame='icrs')
            c2 = SkyCoord(ra=a*u.hourangle,
                         dec=deltaN*u.radian,
                         frame='icrs')

            if check_inside_survey(c1.ra,c1.dec,splusLimits_S):
                #print 'Adding tile@ %s...'%c.to_string('hmsdms',sep=':')
                # splusS.append(c1.to_string('hmsdms',sep=':'))
                splusS.append(c1.to_string())
                scriptS+='get FoV(T80Cam) %s\nset color=red\n'%c1.to_string('hmsdms',sep=':')
                NTileS+=1

            if check_inside_survey(c2.ra,c2.dec,splusLimits_S):
                #print 'Adding tile@ %s...'%c.to_string('hmsdms',sep=':')
                # splusS.append(c2.to_string('hmsdms',sep=':'))
                splusS.append(c2.to_string())
                scriptS+='get FoV(T80Cam) %s\nset color=red\n'%c2.to_string('hmsdms',sep=':')
                NTileS+=1

            if check_inside_survey(c1.ra,c1.dec,splusLimits_N):
                # splusN.append(c1.to_string('hmsdms',sep=':'))
                splusN.append(c1.to_string())
                scriptN+='get FoV(T80Cam) %s\nset color=blue\n'%c1.to_string('hmsdms',sep=':')
                NTileN+=1

            if check_inside_survey(c2.ra,c2.dec,splusLimits_N):
                splusN.append(c2.to_string())
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

            if check_inside_survey(c1.ra,c1.dec,SMC):
                smc.append(c1.to_string('hmsdms',sep=':'))
                scriptSMC+='get FoV(T80Cam) %s\nset color=blue\n'%c1.to_string('hmsdms',sep=':')
                NTilesSMC+=1
                chimera_sched_SMC+=chimera_sched_action.format(ra = c1.ra.to_string(sep=':',unit=u.hourangle),
                                                           dec = c1.dec.to_string(sep=':'),
                                                           ngrid = NTilesSMC)

            if check_inside_survey(c2.ra,c2.dec,SMC):
                smc.append(c2.to_string('hmsdms',sep=':'))
                scriptSMC+='get FoV(T80Cam) %s\nset color=blue\n'%c2.to_string('hmsdms',sep=':')
                NTilesSMC+=1

            if check_inside_survey_gal(c1.galactic.l.value,c1.galactic.b.value,Galactic):
                scriptGalactic+='get FoV(T80Cam) %s\nset color=blue\n'%c1.to_string('hmsdms',sep=':')

            if check_inside_survey_gal(c2.galactic.l.value,c2.galactic.b.value,Galactic):
                scriptGalactic+='get FoV(T80Cam) %s\nset color=blue\n'%c2.to_string('hmsdms',sep=':')

            if around_ecliptic(c1, 2):
                # smc.append(c1.to_string('hmsdms',sep=':'))
                scriptEcliptic+='get FoV(T80Cam) %s\nset color=blue\n'%c1.to_string('hmsdms',sep=':')

            if around_ecliptic(c2, 2):
                scriptEcliptic+='get FoV(T80Cam) %s\nset color=blue\n'%c2.to_string('hmsdms',sep=':')

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

        newdeltaN = (np.arctan(np.tan(deltaN + theta/2.)*np.cos(dalpha/2.)) + theta/2.)
        if newdeltaN < deltaN:
            break
        else:
            deltaN = newdeltaN
        # deltaN = (np.arctan(np.tan(deltaN + theta/2.)*np.cos(dalpha/2.)) + theta/2.)

    # fp = open(os.path.expanduser('~/iCloud/DropboxDocuments/T80S/S-PLUS/script_splus_south.ajs'),'w')
    # fp.write(scriptS)
    # fp.close()
    #
    # fp = open(os.path.expanduser('~/iCloud/DropboxDocuments/T80S/S-PLUS/script_splus_north.ajs'),'w')
    # fp.write(scriptN)
    # fp.close()
    #
    # fp = open(os.path.expanduser('~/iCloud/DropboxDocuments/T80S/S-PLUS/script_stripe82.ajs'),'w')
    # fp.write(scriptS82)
    # fp.close()
    fp = open(os.path.expanduser('~/iCloud/Dropbox/Documents/T80S/S-PLUS/script_ecliptic.ajs'),'w')
    fp.write(scriptEcliptic)
    fp.close()

    fp = open(os.path.expanduser('~/iCloud/Dropbox/Documents/T80S/S-PLUS/script_galactic.ajs'),'w')
    fp.write(scriptGalactic)
    fp.close()

    fp = open(os.path.expanduser('~/iCloud/Dropbox/Documents/T80S/S-PLUS/script_smc.ajs'),'w')
    fp.write(scriptSMC)
    fp.close()

    fp = open(os.path.expanduser('~/iCloud/Dropbox/Documents/T80S/S-PLUS/smc_grid_test_sched.yaml'),'w')
    fp.write(chimera_sched_SMC)
    fp.close()

    fp = open(os.path.expanduser('~/iCloud/Dropbox/Documents/t80s/s-plus/smc_tiles.txt'),'w')
    NTile = 1

    for tile in smc:
        fp.write('MC%04i %s\n'%(NTile,tile))
        NTile+=1
    fp.close()

    import sampy
    cli1 = sampy.SAMPIntegratedClient(metadata = {"samp.name":"Client 1",
                                            "samp.description.text":"Test Client 1",
                                            "cli1.version":"0.01"})
    message = {"samp.mtype": 'script.aladin.send', 'samp.params' : {'script' : scriptSMC}}
    cli1.connect()
    cli1.notifyAll(message)

    # fp = open(os.path.expanduser('~/iCloud/Dropbox/Documents/t80s/s-plus/splus_tiles.txt'),'w')
    # NTile = 1
    #
    # for tile in splusS:
    #     fp.write('SPLUS_%04i %s\n'%(NTile,tile))
    #     NTile+=1
    #
    # for tile in splusN:
    #     fp.write('SPLUS_%04i %s\n'%(NTile,tile))
    #     NTile+=1
    #
    #
    # fp.close()

    # fp = open(os.path.expanduser('~/iCloud/DropboxDocuments/T80S/S-PLUS/stripe82_tiles.txt'),'w')
    # NTile = 1
    #
    # for tile in s82:
    #     fp.write('STRIPE82_%04i %s\n'%(NTile,tile))
    #     NTile+=1
    #
    # fp.close()

    return 0

if __name__ == '__main__':
    main(sys.argv)
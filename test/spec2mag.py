#!/usr/bin/env python

'''
Convert spectroscopic flux to magnitudes in a list of bands.
'''

import sys,os
import numpy as np
from magal.photometry.syntphot import spec2filter
import logging as log

log.basicConfig(format='%(levelname)s:%(asctime)s::%(message)s',
                    level=log.DEBUG)

def main(argv):
    from optparse import OptionParser

    parser = OptionParser()

    parser.add_option('--speclist',
                      help = 'List of spectra to be convolved with filter curves.',
                      type='string')

    parser.add_option('--filterlist',
                      help = 'List of filters to be used.',
                      type='string')

    opt, args = parser.parse_args(argv)

    splist = np.loadtxt(opt.speclist,
                        dtype='S',ndmin=1)
    flist = np.loadtxt(opt.filterlist,
                        dtype='S')

    for spname in splist:
        spdata = np.load(spname)
        magdata = np.zeros(len(flist),dtype= [('name','S16'),
                                              ('lambda0',np.float),
                                              ('dlamb',np.float),
                                              ('mag',np.float)])

        path,ext = os.path.splitext(spname)
        magname = path+'_mag.npy'

        for iff,fname in enumerate(flist):
            fdata = np.load(fname)
            mag = spec2filter(fdata,
                              spdata)
            magdata['name'][iff] = fname
            magdata['lambda0'][iff] = np.sum(fdata['wl']*fdata['transm'])/np.sum(fdata['transm'])
            magdata['dlamb'][iff] = np.std(fdata['wl']*fdata['transm'])
            magdata['mag'][iff] = mag[0]

        log.info('%s -> %s ...' % (spname, magname))

        np.save(magname,
                magdata)


    return 0

if __name__ == '__main__':

    main(sys.argv)
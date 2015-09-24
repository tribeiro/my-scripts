#! /usr/bin/env python

'''
Compute image statistics (min,max,mean,std) using numpy.
'''

import sys,os
import numpy as np
from astropy.io import fits as pyfits
import logging
import time
from multiprocessing.pool import Pool

logging.basicConfig(format='%(levelname)s:%(asctime)s::%(message)s',
                    level=logging.DEBUG)

log = logging.getLogger('imstat')

def main(argv):

    from optparse import OptionParser

    parser = OptionParser()

    parser.add_option('--regions',
                      help = 'A text file specifying image regions to compute statistics. If none is given, use entire image. Format is x0 x1 y0 y1',
                      type='string')
    parser.add_option('--keywords',
                      help = 'Add these header keywords to the output. Separated by "," no spaces.',
                      type='string')
    parser.add_option('--parallelism',
                      help = 'Number of pools to run in parallel (default=1, no parallelism).',
                      type=np.int,default=1)
    parser.add_option('-o','--output',
                      help = 'Output name.',
                      type='string')

    opt, args = parser.parse_args(argv)

    nimages = len(args[1:])

    dtype = [('filename','30S'),
             ('x0',np.int),
             ('x1',np.int),
             ('y0',np.int),
             ('y1',np.int),
             ('min',np.float),
             ('mean',np.float),
             ('max',np.float),
             ('std',np.float)]

    keys = None
    if opt.keywords:
        keys = opt.keywords.split(",")
        for key in keys:
            dtype.append((key,'72S')) # Fits standard specify that 71 is the maximum length of a header keyword value

    regions = None
    nreg = 1
    if opt.regions:
        regions = np.loadtxt(opt.regions)
        nreg = len(regions)

    outData = np.zeros(nimages*nreg,dtype=dtype)

    def stat(index):

        try:
            log.debug('Working on index %i'%index)
            hdu = pyfits.open(args[index+1])

            def calc_stat(i):
                outData['filename'][i] = os.path.basename(args[index+1])
                outData['x0'][i] = x0
                outData['x1'][i] = x1
                outData['y0'][i] = y0
                outData['y1'][i] = y1
                outData['min'][i] = np.min(hdu[0].data[y0:y1,x0:x1])
                outData['mean'][i] = np.mean(hdu[0].data[y0:y1,x0:x1])
                outData['max'][i] = np.max(hdu[0].data[y0:y1,x0:x1])
                outData['std'][i] = np.std(hdu[0].data[y0:y1,x0:x1])

                if keys is not None:
                    for key in keys:
                        outData[key][i] = hdu[0].header[key]

            if regions is not None:
                for reg in range(nreg):
                    x0,x1,y0,y1 = regions[reg]
                    calc_stat(index*nreg+reg)
            else:
                x0 = 0
                x1 = len(hdu[0].data)
                y0 = 0
                y1 = len(hdu[0].data)
                reg = 0
                calc_stat(index)
        except Exception,e:
            log.exception(e)

    log.info('Processing %i files with %i regions...'%(nimages,nreg))

    for i in range(nimages):
        # log.debug('Reading in %s'%args[i+1])
        # hdu = pyfits.open(args[i+1])
        stat(i)
        # pool.apply_async(stat,(i,))

    for i in range(len(outData)):
        line = ''
        for val in outData[i]:
            line += '%s '%val
        log.info(line)

    if opt.output:
        log.info('Saving output to %s'%opt.output)
        np.save(opt.output,
                outData)

    return 0

if __name__ == '__main__':

    main(sys.argv)
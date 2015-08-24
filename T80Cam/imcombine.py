#! /usr/bin/env python

'''
Combine a set of input images with median algorithm using numpy
'''

import sys,os
import numpy as np
from astropy.io import fits as pyfits
import logging
import datetime as dt

logging.basicConfig(format='%(levelname)s:%(asctime)s::%(message)s',
                    level=logging.DEBUG)


def main(argv):

    from optparse import OptionParser

    parser = OptionParser()

    parser.add_option('-o','--output',
                      help = 'Output root name.'
                      ,type='string')

    opt, args = parser.parse_args(argv)

    nimages = len(args[1:])
    hdu = pyfits.open(args[1])
    sizex,sizey = hdu[0].data.shape
    logging.debug('Stack size: %ix%ix%i'%(nimages,sizex,sizey))
    img_stack = np.zeros((nimages,sizex,sizey),dtype=hdu[0].data.dtype)

    hdu[0].header['COMMENT'] = 'IMCOMBINE: %s'%dt.datetime.now()
    hdu[0].header['COMMENT'] = 'IMCOMBINE: Combining %i images with median algorithm.'%nimages

    for i in range(nimages):
        logging.info('Reading in %s'%args[i+1])
        hdu[0].header['COMMENT'] = 'IMCOMBINE: %s.'%args[i+1]
        img_stack[i] += pyfits.getdata(args[i+1])
    hdu[0].data = np.median(img_stack,axis=0)

    logging.info('Saving output to %s'%opt.output)
    hdu.writeto(opt.output,verify='silentfix+warn')

    return 0

if __name__ == '__main__':

    main(sys.argv)
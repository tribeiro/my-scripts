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
                      help = 'Output root name.',
                      type='string')

    opt, args = parser.parse_args(argv)

    nimages = len(args[1:])
    hdu = pyfits.open(args[1])
    sizex, sizey = hdu[0].data.shape
    img_stack = np.zeros((nimages,sizex,sizey),dtype=hdu[0].data.dtype)

    header_comments = ["IMCOMBINE: %s"%dt.datetime.now(),
                       "IMCOMBINE: Combining %i images with median algorithm"%nimages,
                       "IMCOMBINE: IMAGE    MEAN    MIN    MAX    STD"]

    for i in range(nimages):
        logging.info('Reading in %s'%args[i+1])
        img_stack[i] += pyfits.getdata(args[i+1])
        header_comments.append("IMCOMBINE: %s  %.2f  %.2f  %.sf  %.2f"%(args[i+1],
                                                                        np.mean(img_stack[i]),
                                                                        np.min(img_stack[i]),
                                                                        np.max(img_stack[i]),
                                                                        np.std(img_stack[i])))

    logging.info("Processing...")
    output_hdu = pyfits.PrimaryHDU(np.median(img_stack,axis=0))

    for comment in header_comments:
        output_hdu.header["COMMENT"] = comment
    output_hdulist = pyfits.HDUList([output_hdu])
    #hdu[0].data = np.median(img_stack,axis=0)

    logging.info('Saving output to %s'%opt.output)
    output_hdulist.writeto(opt.output)

    return 0

if __name__ == '__main__':

    main(sys.argv)
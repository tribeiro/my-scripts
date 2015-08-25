#! /usr/bin/env python

'''
Perform arithmetics on input images using numpy
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

    parser.add_option('--im1',
                      help = 'First image.',
                      type='string')

    parser.add_option('--im2',
                      help = 'Second image or number.',
                      type='string')

    parser.add_option('--operator',
                      help = 'A math operator. One of +, -, * /',
                      type='string')

    parser.add_option('-o','--output',
                      help = 'Output root name.',
                      type='string')

    opt, args = parser.parse_args(argv)

    img1 = pyfits.open(opt.im1)
    img2 = pyfits.open(opt.im2)

    sizex, sizey = img1[0].data.shape
    output_data = img1[0].data - img2[0].data

    # header_comments = ["IMARITH: %s"%dt.datetime.now(),
    #                    "IMARITH: Combining %i images with median algorithm"%nimages,
    #                    "IMARITH: IMAGE    MEAN    MIN    MAX    STD"]

    output_hdu = pyfits.PrimaryHDU(output_data)
    
    # for comment in header_comments:
    #     output_hdu.header["COMMENT"] = comment
    output_hdulist = pyfits.HDUList([output_hdu])
    #hdu[0].data = np.median(img_stack,axis=0)

    logging.info('Saving output to %s'%opt.output)
    output_hdulist.writeto(opt.output)

    return 0

if __name__ == '__main__':

    main(sys.argv)
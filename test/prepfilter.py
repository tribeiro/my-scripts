#!/usr/bin/env python

'''
Convert filter transmission curve from ascii to npy in order to be readable by magal spec2filter function.
'''

import sys,os
import numpy as np
import logging

logging.basicConfig(format='%(levelname)s:%(asctime)s::%(message)s',
                    level=logging.DEBUG)

def main(argv):

    from optparse import OptionParser

    parser = OptionParser()

    opt, args = parser.parse_args(argv)

    for fname in args[1:]:
        data = np.loadtxt(fname,
                          unpack=True)
        fc = np.array( zip( data[0], data[1]), dtype = [ ('wl', np.float) , ('transm', np.float) ])
        np.save(fname.replace('.res',
                              '.npy'),
                fc)

    return 0

if __name__ == '__main__':

    main(sys.argv)
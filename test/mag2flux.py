#!/usr/bin/env python

'''
Convert from mag_nu to flux_lambda.
'''

import sys,os
import numpy as np
from scipy import constants
import logging

logging.basicConfig(format='%(levelname)s:%(asctime)s::%(message)s',
                    level=logging.DEBUG)

def main(argv):

    from optparse import OptionParser

    parser = OptionParser()

    opt, args = parser.parse_args(argv)

    for spec in args[1:]:
        ospec = spec.replace('.dat','.npy')
        logging.debug(' %s -> %s...' % (spec,ospec))

        data = np.loadtxt(spec,
                          unpack=True)
        f_nu = 10**(-0.4 * (data[1] + 48.590))
        f_lambda =  (constants.c * 1e10) / data[0]**2. * f_nu

        sp = np.array(zip(data[0],f_lambda,data[1],data[2]),dtype=[('wl',np.int32),
                                                                   ('flux',np.float),
                                                                   ('mag',np.float),
                                                                   ('dlam',np.int32)])
        np.save(ospec,
                sp)

    return 0


if __name__ == '__main__':

    main(sys.argv)
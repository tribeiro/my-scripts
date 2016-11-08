#! /usr/bin/env python

'''
Compute image statistics (min,max,mean,std) using numpy.
'''

import sys,os
import numpy as np
from astropy.io import fits as pyfits
import logging
from fits_reduce.util.overscancorr import OverscanCorr

import time

logging.basicConfig(format='%(levelname)s:%(asctime)s::%(message)s',
                    level=logging.DEBUG)

log = logging.getLogger('norm_flat')

class NormSection(OverscanCorr):

    def __init__(self,*args,**kwargs):
        OverscanCorr.__init__(self,*args,**kwargs)

    def gain(self):
        gain_img = np.zeros_like(self.ccd.data,dtype=np.float)

        for subarr in self._ccdsections:
            # print scan_level
            gain_img[subarr.section] += subarr.gain

        newdata = np.zeros_like(self.ccd.data,dtype=np.float) + self.ccd.data
        newdata /= gain_img
        self.ccd.data = newdata

        import pyds9 as ds9

        d = ds9.ds9()

        # print self._ccdsections[0].parallel_scans[1]
        # d.set_np2arr(newdata)
        d.set_np2arr(gain_img)

    def norm(self):
        newdata = np.zeros_like(self.ccd.data,dtype=np.float) + self.ccd.data
        newdata /= np.median(self.ccd.data)
        self.ccd.data = newdata

    def get_avg(self, filename):
        level = np.zeros((self._parallelports,self._serialports))
        for subarr in self._ccdsections:
            level[subarr.parallel_index][subarr.serial_index] = np.median(self.ccd.data[subarr.section])
        np.save(level,filename)
        return

    def linearize(self,coeffs, saturation = 60e3):
        lin_corr_img = np.zeros_like(self.ccd.data,dtype=np.float64)
        for i in range(0,len(self._ccdsections)):
            subarr = self._ccdsections[i]
            log.info('Linearizing region %i x %i...' % (subarr.parallel_index,subarr.serial_index))
            ppol = np.poly1d(coeffs[subarr.parallel_index][subarr.serial_index])
            lin_corr_img[subarr.section] = ppol(self.ccd.data[subarr.section]/32767.)

        mask = np.bitwise_and(lin_corr_img > 0.,
                              self.ccd.data < saturation)

        # mask = np.bitwise_and(lin_corr_img == 0.,
        #                       self.ccd.data > saturation)
        lin_corr_img[mask] = 1.

        newdata = self.ccd.data / lin_corr_img

        # newdata = self.ccd.data / lin_corr_img
        self.ccd.data = newdata

    def linearize_slow(self, coeffs, saturation = 60e3):


        def pol(coeff,arr):
            rarr = np.zeros_like(arr,dtype=np.float64)
            for i,c in enumerate(coeff[::-1]):

                if i == 0:
                    rarr =  rarr + c
                else:
                    tmparr = np.zeros_like(arr,dtype=np.float64) + c*arr
                    for d in range(1,i):
                        tmparr = tmparr*arr
                    rarr= rarr + tmparr
            return rarr

        lin_corr_img = np.zeros_like(self.ccd.data,dtype=np.float64)
        import pyds9 as ds9

        d = ds9.ds9()

        # print self._ccdsections[0].parallel_scans[1]
        # d.set_np2arr(newdata)

        # d.set_np2arr(lin_corr_img)


        for i in range(0,len(self._ccdsections)):
            subarr = self._ccdsections[i]
            ppol = np.poly1d(coeffs[subarr.parallel_index][subarr.serial_index])

            lin_corr_img[subarr.section] += pol(coeffs[subarr.parallel_index][subarr.serial_index],
                                               self.ccd.data[subarr.section])
            tmp_lin_corr = np.zeros_like(lin_corr_img[subarr.section])
            tmp_section = self.ccd.data[subarr.section]
            print 'starting slow'
            for ii in range(len(tmp_lin_corr)):
                for jj in range(len(tmp_lin_corr[ii])):
                    tmp_lin_corr[ii][jj] = ppol(np.float64(tmp_section[ii][jj]))
            print 'done'
            # sys.exit(0)
            lin_corr_img[subarr.section] = tmp_lin_corr
            # level_start[i] = np.median(self.ccd.data[subarr.section][:,:10])
            # level_end[i] = np.median(self.ccd.data[subarr.section][:,-10:])
            d.set_np2arr(tmp_lin_corr)
        d.set_np2arr(lin_corr_img)
        mask = np.bitwise_and(lin_corr_img > 0.,
                              self.ccd.data < saturation)

        # mask = np.bitwise_and(lin_corr_img == 0.,
        #                       self.ccd.data > saturation)
        # lin_corr_img[mask] = 1.

        newdata = self.ccd.data / lin_corr_img
        self.ccd.data = newdata

    def norm_section(self):
        norm_img = np.zeros_like(self.ccd.data,dtype=np.float) + 1

        import pyds9 as ds9

        d = ds9.ds9()

        level_start = np.zeros_like(self._ccdsections)
        level_end = np.zeros_like(self._ccdsections)
        n_gain = np.zeros_like(self._ccdsections) + 1.0 / np.median(self.ccd.data)
        for i in range(0,len(self._ccdsections),2):
            subarr = self._ccdsections[i]
        # for i,subarr in enumerate(self._ccdsections):
            # print scan_level
            # norm_img[subarr.section] = np.median(self.ccd.data[subarr.section])
            # d.set_np2arr(self.ccd.data[subarr.section]) #[:,-10:])
            # return
            level_start[i] = np.median(self.ccd.data[subarr.section][:,:2])
            level_end[i] = np.median(self.ccd.data[subarr.section][:,-2:])

        for i in range(1,len(self._ccdsections),2):
            subarr = self._ccdsections[i]
        # for i,subarr in enumerate(self._ccdsections):
            # print scan_level
            # norm_img[subarr.section] = np.median(self.ccd.data[subarr.section])
            # d.set_np2arr(self.ccd.data[subarr.section]) #[:,-10:])
            # return
            level_start[i] = np.median(self.ccd.data[subarr.section][:,:10])
            level_end[i] = np.median(self.ccd.data[subarr.section][:,-10:])

        for i in range(2,len(level_start),2):
            n_gain[i] = n_gain[i-2] * level_end[i-2] / level_start[i]

        for i in range(3,len(level_start),2):
            n_gain[i] = n_gain[i-2] * level_end[i-2] / level_start[i]

        print n_gain

        for i,subarr in enumerate(self._ccdsections):
            # print scan_level
            norm_img[subarr.section] = n_gain[i]

        newdata = np.zeros_like(self.ccd.data,dtype=np.float) + self.ccd.data
        newdata *= norm_img
        self.ccd.data = newdata

        import pyds9 as ds9

        d = ds9.ds9()

        # print self._ccdsections[0].parallel_scans[1]
        # d.set_np2arr(newdata)
        d.set_np2arr(norm_img)


def main(argv):

    from optparse import OptionParser

    parser = OptionParser()

    parser.add_option('-f','--filename',
                      help = 'Input image name.',
                      type='string')

    parser.add_option('-c','--config',
                      help = 'Configuration file.',
                      type='string')

    parser.add_option('-o','--output',
                      help = 'Output name.',
                      type='string')

    opt, args = parser.parse_args(sys.argv)

    logging.basicConfig(format='%(levelname)s:%(asctime)s::%(message)s',
                        level=logging.DEBUG)

    logging.info('Reading in %s' % opt.filename)

    overcorr = NormSection()

    overcorr.read('%s' % opt.filename)

    logging.info('Loading configuration from %s' % opt.config)

    overcorr.loadConfiguration(opt.config)

    # overcorr.show()

    # logging.info('Applying overscan...')
    #
    # overcorr.overscan()

    # logging.info('Gain...')
    #
    # overcorr.gain()

    # logging.info('Normalizing...')
    #
    # overcorr.norm()

    # logging.info('Trimming...')
    #
    overcorr.linearize(np.load(os.path.expanduser('~/Documents/linearity/model1_20160801/linearity_coeff.npy')))

    ccdout = overcorr.trim()

    if opt.output is not None:
        logging.info('Saving result to %s...' % opt.output)

        ccdout.write(opt.output)
        # overcorr.get_avg(opt.output.replace('.fits','.npy'))

if __name__ == '__main__':
    main(sys.argv)
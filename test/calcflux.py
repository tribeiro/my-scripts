
import sys, os
import numpy as np
import pylab as py
from astropy.io import fits

def main(argv):

    specfile = '/Volumes/TiagoHD2/Documents/template/s_coelho14_sed.lis'
    speclis = np.loadtxt(specfile,dtype='S')

    filters = np.array([('g', 4803., 1409., 0.),
                        ('r',6254., 1388., 0.),
                        ('halpha', 6600., 138., 0.),
                        ('i', 7668., 1535., 0.)],dtype = [('filter','S7'),
                                                          ('y0' , np.float),
                                                          ('dy' , np.float),
                                                          ('flux',np.float)])

    flux = np.zeros(len(speclis),dtype = [('g_0',np.float),
                                          ('r_0',np.float),
                                          ('halpha_0',np.float),
                                          ('i_0',np.float),
                                          ('g_2',np.float),
                                          ('r_2',np.float),
                                          ('halpha_2',np.float),
                                          ('i_2',np.float),
                                          ('g_5',np.float),
                                          ('r_5',np.float),
                                          ('halpha_5',np.float),
                                          ('i_5',np.float),
                                          ('g_10',np.float),
                                          ('r_10',np.float),
                                          ('halpha_10',np.float),
                                          ('i_10',np.float),
                                          ('teff',np.float),
                                          ('logg',np.float),
                                          ('z','S6')])

    for si,s in enumerate(speclis):
        print '-> %s [' % os.path.basename(s),

        hdu = fits.open(s)

        wave = 10.**(hdu[0].header['CRVAL1']+np.arange(0,len(hdu[0].data))*hdu[0].header['CD1_1'])
        lmask = np.bitwise_and(wave > 6530,
                               wave < 6590)

        flux['teff'][si] = hdu[0].header['TEFF']
        flux['logg'][si] = hdu[0].header['LOG_G']
        flux['z'][si] = hdu[0].header['Z']
        # py.plot(wave,hdu[0].data)

        for scale in [0.,2.,5.,10.]:

            nflux = hdu[0].data

            line = nflux[lmask]
            line -= line[0]
            line *= -1
            line *= scale

            nflux[lmask] += line
            # py.plot(wave,nflux)


            for i in range(len(filters)):
                print '%s_%i' % (filters['filter'][i],scale),
                mask = np.bitwise_and(wave > filters['y0'][i] - filters['dy'][i]/2.,
                                      wave < filters['y0'][i] + filters['dy'][i]/2.)

                #
                # for scale in [2.0,5.0,10.]:
                #     flux = hdu[0].data
                #     flux[mask]+=line*scale

                # filters['flux'][i] = np.mean(hdu[0].data[mask])
                flux['%s_%i' % (filters['filter'][i],scale)][si] = np.mean(nflux[mask])
        # py.show()
        # return 0
        print ']'

    np.save('/Users/tiago/Documents/Develop/my-scripts/test/flux_test.npy',flux)

        # np.save(s.replace('.fits','_test.npy'),filters)
    # py.semilogx(wave,hdu[0].data)
    # py.semilogx(filters['y0'],filters['flux'],'o')
    #
    # py.show()

    return 0

if __name__ == '__main__':
    main(sys.argv)
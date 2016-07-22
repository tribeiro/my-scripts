
import sys, os
import numpy as np
import pylab as py


def main(argv):

    fluxfile = '/Users/tiago/Documents/Develop/my-scripts/test/flux_test.npy'

    data = np.load(fluxfile)

    trange = [[3.40,3.80],
              [3.80,4.15],
              [4.15,4.40],
              ]
    scales = [0.,2.,5.,10.]

    colors = 'rgbc'

    # symbols = ['o','*','x','^']

    # for i in range(len(trange)):
    #     mask = np.bitwise_and(data['teff'] > 10**trange[i][0],
    #                           data['teff'] < 10**trange[i][1])
    mask = np.zeros(len(data)) == 0
    for si,scale in enumerate(scales):
        print scale,colors[si]
        py.plot(data['r_%i' % scale][mask]-data['halpha_%i' % scale][mask],
                data['halpha_%i' % scale][mask],colors[si]+'.')

    py.show()

    return 0

if __name__ == '__main__':

    main(sys.argv)
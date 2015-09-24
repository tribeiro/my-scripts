
import sys,os
import numpy as np
import pylab as py
import logging
from astropy import units
from scipy.optimize import fsolve

logging.basicConfig(format='%(asctime)s.%(msecs)d %(origin)s %(levelname)s %(name)s %(filename)s:%(lineno)d %(message)s',
                    level=logging.DEBUG)

def main(argv):

    from optparse import OptionParser

    parser = OptionParser()

    parser.add_option('-f','--filename',
                      help = 'File with measured Zernike coefficients (output of donut).'
                      ,type='string')

    opt, args = parser.parse_args(argv)

    center = np.array([4608,4616]) * units.pixel # X,Y center of the CCD in pixels
    pscale = 0.548 * units.arcsec / units.pixel # place scale in arcsec/pixel

    infmt = [('fits','S20'), ('xc', np.int), ('yc',np.int),
             ('flux',np.float),('chi2',np.float),('seeing',np.float)]

    zern = np.loadtxt(opt.filename,unpack=True,dtype='S')
    ncoef = zern.shape[0]-6

    for n in range(ncoef):
        infmt.append(('Z%i'%(n+1),np.float))

    zern = np.loadtxt(opt.filename,dtype=infmt)

    zNames = {'Z2':'X Tilt',
              'Z3': 'Y Tilt',
            'Z4':'Focus',
            'Z5':'Oblique Astigmatism',
            'Z6':'Vertical Astigmatism',
            'Z7':'Comma Y',
            'Z8':'Comma X'}
    zVals = {}

    for z in zNames.keys():
        zVals[z] = zern[z]*units.micrometer
        # print zern[z]

    B = np.array([-9.41,18.35,-6.6]) * units.micrometer / units.degree / units.degree

    AlphaX = np.zeros(len(zern)) * units.degree
    AlphaY = np.zeros(len(zern)) * units.degree

    for i in range(len(zern)):

        theta_x = (zern['xc'][i]*units.pixel - center[0]) * pscale
        theta_y = (zern['yc'][i]*units.pixel - center[1]) * pscale

        print 'Working on entry %i'%(i+1)
        # print theta_x.to(units.degree),theta_y.to(units.degree)

        def equations(alpha):
            alpha_x,alpha_y = alpha * units.degree
            alpha_x = alpha_x.to(units.degree)
            alpha_y = alpha_y.to(units.degree)
            t_x = theta_x.to(units.degree)
            t_y = theta_y.to(units.degree)
            eq71 = (B[0]*(t_x**2. - t_y**2) + B[1]*(t_x*alpha_x-t_y*alpha_y)+B[2]*(alpha_x**2-alpha_y**2))
            eq72 = (2.*B[0]*t_x*t_y) + (B[1]*(t_x*alpha_x - t_y*alpha_y)) + (2.*B[2]*alpha_x*alpha_y)

            val1 = eq71.to(units.millimeter)-zVals['Z5'][i]
            val2 = eq72.to(units.millimeter)-zVals['Z6'][i]

            return (val1.value,val2.value)

        # print zVals['Z4']#, np.array([0,0])*units.arcsec
        # print equations(np.array([0,0]))
        init = [1,1]
        if i > 0:
            init = [AlphaX[i-1].value,AlphaY[i-1].value]

        ax, ay =  fsolve(equations, (init,))
        AlphaX[i] = ax * units.degree
        AlphaY[i] = ay * units.degree
    #
    # print ax,ay
    # print equations([ax,ay])
    print ' Theta_x  Theta_y  Alpha_x  Alpha_y  Z5    Z6'
    theta_x = (zern['xc']*units.pixel - center[0]) * pscale
    theta_y = (zern['yc']*units.pixel - center[1]) * pscale

    for i in range(len(zern)):

        print '%+8.3f %+8.3f %+8.3f %+8.3f %+8.3f %+8.3f'%(theta_x[i].to(units.degree).value,
                             theta_y[i].to(units.degree).value,
                             AlphaX[i].value,
                             AlphaY[i].value,
                                                           zVals['Z5'][i].value,
                                                           zVals['Z6'][i].value)

    py.plot(theta_x.to(units.degree).value,AlphaX.value,'o')
    py.plot(theta_y.to(units.degree).value,AlphaY.value,'o')
    py.show()
    return 0

if __name__ == '__main__':
    main(sys.argv)
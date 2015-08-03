#! /usr/bin/env python

__author__ = 'tiago'

import sys,os
import pylab as py
import numpy as np
from astropy.table import Table

def main(argv):

    _path = '/Volumes/public/camera/images/'

    refT = 'SICoolingTemperature.CSV'
    refP = 'SICoolingPressure_export.CSV'

    # tempFiles = ['SICooling2Temperature.CSV','SICooling3Temperature.CSV','SICooling5Temperature.CSV']
    # presFiles = ['SICooling2Pressure.CSV','SICooling3Pressure.CSV','SICooling5Pressure.CSV']

    tempFiles = ['SICooling14Temperature.CSV','SICooling13Temperature.CSV','SICooling5Temperature.CSV']
    presFiles = ['SICooling14Pressure.CSV','SICooling13Pressure.CSV', 'SICooling5Pressure.CSV']

    discard = [00,0,0,100]

    ####################################################################################################################

    temp = Table.read(os.path.join(_path,refT),format='ascii')
    press= Table.read(os.path.join(_path,refP),format='ascii')

    #t1_0 = temp['Time'][np.argmax(temp['CCD 0 CCD Temp.'])] # Cooling starts

    Tref = 0. # Reference temperature.

    refindex = np.argmin( np.abs(temp['CCD 0 CCD Temp.']-Tref) )
    t1_0 = temp['Time'][refindex]

    ####################################################################################################################

    fig = py.figure(1)

    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)

    ax1.plot((temp['Time']-t1_0)*24.,temp['CCD 0 CCD Temp.'])
    ax1.grid()

    ax2.plot((press['Time']-t1_0)*24.,press['Chamber Pressure'])
    ax2.grid()

    for indx,tfile in enumerate(tempFiles):
        print 'Reading %s...'%tfile

        t = Table.read(os.path.join(_path,tfile),format='ascii')[discard[indx]:]
        p = Table.read(os.path.join(_path,presFiles[indx]),format='ascii')[discard[indx]:]
        refindex = np.argmin( np.abs(t['CCD 0 CCD Temp.']-Tref) )
        t1_ref = t['Time'][refindex]
        ax1.plot((t['Time']-t1_ref)*24.,t['CCD 0 CCD Temp.'])
        ax2.plot((p['Time']-t1_ref)*24.,p['Chamber Pressure'])

    py.show()

    return 0

if __name__ == '__main__':
    main(sys.argv)
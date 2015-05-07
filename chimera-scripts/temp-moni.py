#!/usr/bin/env python

################################################################################

__author__ = 'Ribeiro, T.'

################################################################################

import sys
import os
import time
import numpy as np
import datetime as dt
import copy

from chimera.core.cli import ChimeraCLI, action
from chimera.core.callback import callback
from chimera.util.position import Position
from chimera.util.coord import Coord
from chimera.util.output import blue, green, red
from chimera.core.site import datetimeFromJD
from chimera.core.exceptions import ObjectNotFoundException

import plotly.plotly as py
from plotly.graph_objs import Data,Scatter,Figure
import plotly.tools as tls

################################################################################

currentFrame = 0
currentFrameExposeStart = 0
currentFrameReadoutStart = 0

################################################################################

class MoniT (ChimeraCLI):

    ############################################################################

    def __init__(self):
        ChimeraCLI.__init__(self, "MoniT",
                            "Monitor telescope temperature", 0.0, port=9010)

        '''
        Make intra/extra focal observations in a grid of alt/az.
        '''


        self.addHelpGroup("RUN", "Start/Stop/Info")
        self.addHelpGroup("TELESCOPE", "Telescope")

        self.addInstrument(name="telescope",
                           cls="Telescope",
                           required=True,
                           help="Telescope instrument to be used. If blank, try to guess from chimera.config",
                           helpGroup="TELESCOPE")
        self.addParameters(dict(name="utime", long="updatetime", type=float,
                        help="How long it will wait before reading in new data (in seconds).",default=30.,
                        metavar="utime"))
        self.addParameters(dict(name="maxpoints", long="maxpoints", type=int,
                        help="Maximum number of points to plot. Set to -1 for unlimited.",default=-1,
                        metavar="maxpoints"))

        self.stream_ids = tls.get_credentials_file()['stream_ids']
        self._ns = 4 # number of sensors
        self._sindex = [1,2,3,4] # sensor index
        self.streams = [None,None,None,None]
        self.traces = [None,None,None,None]
        self.tlabels = ['M1 Temperature','M2 Temperature','Front Rod','Tube Rod']

        if len(self.stream_ids) < 4:
            raise IOError('At least 4 PlotLy tokens are required to stream the data. Add them to your credentials, see https://plot.ly/python/streaming-tutorial/')

    ############################################################################

    def initLy(self):

        for i in range(len(self.streams)):
            # Configure streams
            self.streams[i] = py.Stream(self.stream_ids[i])

            # Initialize traces
            self.traces[i] = Scatter(x=[], y=[], name=self.tlabels[i],
                     stream=dict(token=self.stream_ids[i]))

        self.data = Data(self.traces)

        self.fig = Figure(data=self.data)

        now = dt.datetime.now()

        self.year,self.month,self.day = now.year,now.month,now.day

        self.unique_url = py.plot(fig,filename='T80S_TM_%04i%02i%02i'%(self.year,
                                                                       self.month,
                                                                       self.day)) #,fileopt='extended')

        self.openStreams()

    ############################################################################

    def openStreams(self):
        for i in range(len(self.streams)):
            self.streams[i].open()

    ############################################################################

    def closeStreams(self):
        for i in range(len(self.streams)):
            self.streams[i].close()

    ############################################################################

    @action(help="Start monitoring temperature", helpGroup="RUN", actionGroup="RUN")
    def start(self, options):

        x = [dt.datetime.now()]
        sensors = self.telescope.getSensors()

        tm1 = [sensors[1][1]]
        tm2 = [sensors[2][1]]
        tfr = [sensors[3][1]]
        ttr = [sensors[4][1]]

        #print x[0],tm1[0]

        # Get credentials from plotly configfile.
        #cr = py.get_credentials()
        maxpoints = options.maxpoints
        if maxpoints < 0:
            maxpoints = None

        trace1 = Scatter(x=[], y=[], name='M1 Temperature',
                 stream=dict(token='jh645553at',maxpoints=options.maxpoints))
        trace2 = Scatter(x=[], y=[], name='M2 Temperature',
                 stream=dict(token='2scawy54a0',maxpoints=options.maxpoints))
        trace3 = Scatter(x=[], y=[], name='Front Rod',
                 stream=dict(token='xqevutbl2z',maxpoints=options.maxpoints))
        trace4 = Scatter(x=[], y=[], name='Tube Rod',
                 stream=dict(token='d6vddg44xl',maxpoints=options.maxpoints))

        fig = Figure(data=[trace1,trace2,trace3,trace4])

        py.plot(fig,filename='T80S_TM') #,fileopt='extended')

        s1 = py.Stream('2scawy54a0')
        s2 = py.Stream('jh645553at')
        s3 = py.Stream('xqevutbl2z')
        s4 = py.Stream('d6vddg44xl')

        s1.open()
        s2.open()
        s3.open()
        s4.open()

        s1.write(dict(x=x[-1],
                      y=tm1[-1]
                      ))
        s2.write(dict(x=x[-1],
                      y=tm2[-1]
                      ))
        s3.write(dict(x=x[-1],
                      y=tfr[-1]
                      ))
        s4.write(dict(x=x[-1],
                      y=ttr[-1]
                      ))


        fp = open('temp-moni.txt','w')


        while True:

            time.sleep(options.utime)

            x.append(dt.datetime.now())
            sensors = None
            while not sensors:
                sensors = self.telescope.getSensors()
                time.sleep(0.5)

            print sensors
            tm1.append(sensors[1][1])
            tm2.append(sensors[2][1])
            tfr.append(sensors[3][1])
            ttr.append(sensors[4][1])
            fp.write('%s %f %f %f %f\n'%(x[-1],tm1[-1],tm2[-1],tfr[-1],ttr[-1]))
            fp.flush()

            if options.maxpoints > 0 and len(x) > options.maxpoints:
                x.pop(0)
                tm1.pop(0)
                tm2.pop(0)
                tfr.pop(0)
                ttr.pop(0)
            print x[-1],tm1[-1]

            s1.write(dict(x=x[-1],
                          y=tm1[-1]
                          ))
            s2.write(dict(x=x[-1],
                          y=tm2[-1]
                          ))
            s3.write(dict(x=x[-1],
                          y=tfr[-1]
                          ))
            s4.write(dict(x=x[-1],
                          y=ttr[-1]
                          ))

        return 0



################################################################################
def main():
    cli = MoniT()
    cli.run(sys.argv)
    cli.wait()

################################################################################

if __name__ == '__main__':

    main()

################################################################################
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
from plotly.graph_objs import Data, Scatter, Figure
import plotly.tools as tls

################################################################################

currentFrame = 0
currentFrameExposeStart = 0
currentFrameReadoutStart = 0

################################################################################

class MoniT(ChimeraCLI):
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
                                help="How long it will wait before reading in new data (in seconds).", default=30.,
                                metavar="utime"))
        self.addParameters(dict(name="maxpoints", long="maxpoints", type=int,
                                help="Maximum number of points to plot. Set to -1 for unlimited.", default=-1,
                                metavar="maxpoints"))

        self.stream_ids = tls.get_credentials_file()['stream_ids']
        self._ns = 4  # number of sensors
        self._sindex = [2, 4, 6, 8]  # sensor index
        self.streams = [None, None, None, None]
        self.traces = [None, None, None, None]
        self.tlabels = ['M1 Temperature', 'M2 Temperature', 'Front Rod', 'Tube Rod']

        if len(self.stream_ids) < 4:
            raise IOError(
                'At least 4 PlotLy tokens are required to stream the data. Add them to your credentials, see https://plot.ly/python/streaming-tutorial/')

    ############################################################################

    def initLy(self):

        now = dt.datetime.now()

        self.year, self.month, self.day = now.year, now.month, now.day

        for i in range(len(self.streams)):
            # Configure streams
            self.streams[i] = py.Stream(self.stream_ids[i])

            # Initialize traces
            self.traces[i] = Scatter(x=[], y=[], name=self.tlabels[i],
                                     stream=dict(token=self.stream_ids[i]))

        self.data = Data(self.traces)

        self.fig = Figure(data=self.data)

        self.unique_url = py.plot(self.fig, filename='T80S_TM_%04i%02i%02i' % (self.year,
                                                                          self.month,
                                                                          self.day))  # ,fileopt='extended')

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

    def getData(self):

        sensors = self.telescope.getSensors()
        #print sensors
        data = [dt.datetime.now()]
        for i in range(self._ns):
            data.append(sensors[self._sindex[i]][1])
        return data

    ############################################################################

    def streamData(self, data):

        for i in range(self._ns):
            self.streams[i].write(dict(x=data[0],
                                       y=data[i+1]
                                       ))
    ############################################################################

    def initDB(self):

        filename = 'T80S_TempMonitor_%i%i%i.txt' % (self.year, self.month, self.day)
        mode = 'w'
        if os.path.exists(filename):
            mode = 'a'
        return open(filename, mode)


    ############################################################################

    @action(help="Start monitoring temperature", helpGroup="RUN", actionGroup="RUN")
    def start(self, options):

        self.initLy()

        fp = self.initDB()

        while True:

            data = self.getData()
            self.out(green('[MoniT]:') + ' %s %s %s %s %s' % (data[0], data[1], data[2], data[3], data[4]))
            fp.write('%s %s %s %s %s\n' % (data[0], data[1], data[2], data[3], data[4]))
            fp.flush()

            try:
                self.streamData(data)
            except:
                self.err(red('[MoniT]:') + ' Failed to stream the data. Trying to open streams again.')
                try:
                    self.openStreams()
                    self.streamData(data)
                except:
                    fp.close()
                    self.exit(red('[MoniT]:') + ' Failed to stream the data. Giving up...', -1)
                finally:
                    pass
            finally:
                time.sleep(options.utime)

            # Check if date changed. If yes, start new streams
            if self.year != data[0].year or self.month != data[0].month or self.day != data[0].day:
                fp.close()
                self.closeStreams()
                self.initLy()
                fp = self.initDB()

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
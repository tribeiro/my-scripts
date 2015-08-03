__author__ = 'tiago'

#!/usr/bin/env python

################################################################################

import sys
import os
import time
import numpy as np
import datetime as dt
import copy

from chimera.core.cli import ChimeraCLI, action, ParameterType
from chimera.core.callback import callback
from chimera.util.position import Position
from chimera.util.coord import Coord,CoordUtil
from chimera.util.output import blue, green, red
from chimera.core.site import datetimeFromJD
from chimera.core.exceptions import ObjectNotFoundException

################################################################################

currentFrame = 0
currentFrameExposeStart = 0
currentFrameReadoutStart = 0

################################################################################

class TestDPT_PB (ChimeraCLI):

    ############################################################################

    def __init__(self):
        ChimeraCLI.__init__(self, "m2test",
                            "Scheduler controller", 0.0, port=9010)

        '''
        Make intra/extra focal observations in a grid of alt/az.
        '''

        self.addHelpGroup("RUN", "Start/Stop/Info")
        self.addHelpGroup("TELESCOPE", "Telescope")
        self.addHelpGroup("CAMERA", "Camera")
        self.addHelpGroup("OBSERVATORY", "Observatory")

        self.addController(name="site",
                           cls="Site",
                           required=True,
                           help="Observing site",
                           helpGroup="OBSERVATORY")

        self.addInstrument(name="telescope",
                           cls="Telescope",
                           required=True,
                           help="Telescope instrument to be used. If blank, try to guess from chimera.config",
                           helpGroup="TELESCOPE")

        self.addInstrument(name="camera",
                           cls="Camera",
                           help="Camera instrument to be used. If blank, try to guess from chimera.config",
                           helpGroup="CAMERA", required=True)


    ############################################################################

    @action(help="Start observations", helpGroup="RUN", actionGroup="RUN")
    def start(self, options):

        filename = "$DATE-$TIME.fits"

        site = self.site

        dome = None
        try:
            dome = self.camera.getManager().getProxy("/Dome/0")
        except ObjectNotFoundException:
            pass

        @callback(self.localManager)
        def exposeBegin(request):
            global currentFrame, currentFrameExposeStart
            currentFrameExposeStart = time.time()
            currentFrame += 1
            self.out(40 * "=")
            self.out("[%03d/%03d] [%s]" %
                     (currentFrame, options.frames, time.strftime("%c")))
            self.out("exposing (%.3fs) ..." % request["exptime"], end="")

        @callback(self.localManager)
        def exposeComplete(request, status):
            global currentFrameExposeStart
            if status == CameraStatus.OK:
                self.out("OK (took %.3f s)" %
                         (time.time() - currentFrameExposeStart))

        @callback(self.localManager)
        def readoutBegin(request):
            global currentFrameReadoutStart
            currentFrameReadoutStart = time.time()
            self.out("reading out and saving ...", end="")

        @callback(self.localManager)
        def readoutComplete(image, status):
            global currentFrame, currentFrameExposeStart, currentFrameReadoutStart

            if status == CameraStatus.OK:
                self.out("OK (took %.3f s)" %
                         (time.time() - currentFrameExposeStart))

                self.out(" (%s) " % image.compressedFilename(), end="")
                self.out("OK (took %.3f s)" %
                         (time.time() - currentFrameReadoutStart))
                self.out("[%03d/%03d] took %.3fs" % (currentFrame, options.frames,
                                                     time.time() - currentFrameExposeStart))

                if ds9:
                    ds9.set("scale mode 99.5")
                    ds9.displayImage(image)

                image.close()

        self.camera.exposeBegin += exposeBegin
        self.camera.exposeComplete += exposeComplete
        self.camera.readoutBegin += readoutBegin
        self.camera.readoutComplete += readoutComplete

        if dome:
            @callback(self.localManager)
            def syncBegin():
                self.out("=" * 40)
                self.out("synchronizing dome slit ...", end="")

            @callback(self.localManager)
            def syncComplete():
                self.out("OK")

            dome.syncBegin += syncBegin
            dome.syncComplete += syncComplete

        global currentFrame

        # obj1 = "TYC 7388-1093-1 - dpt - PB"
        # radec1 = Position.fromRaDec('17:33:36.601','-37:06:13.665')
        # exptime1 = 5.0

        obj1 = "HD 206025 - dpt - PB"
        radec1 = Position.fromRaDec('21:40:42.920' , '-48:42:58.400' )
        exptime1 = 1.

        obj2 = "HD 204287 - dpt - PB"
        radec2 = Position.fromRaDec('21:29:14.470', '-50:19:00.600')
        exptime2 = 1.

        for i in range(10):

            msg1 = '[%i] ra/dec - object 1: %s @ %s'%(i,obj1,radec1)
            msg2 = '[%i] ra/dec - object 2: %s @ %s'%(i,obj2,radec2)
            self.out('='*len(msg1))
            self.out(msg1)

            # continue

            self.out('Slewing')
            self.telescope.slewToRaDec(radec1)
            # center on PiggyBack
            self.out('Offset E')
            self.telescope.moveEast(Coord.fromAS(1580))
            self.out('Offset S')
            self.telescope.moveSouth(Coord.fromAS(972))

            self.out('Acquiring')
            self.camera.expose(exptime=exptime1,
                                  frames=1,
                                  interval=0.,
                                  filename=filename,
                                  type='OBJECT',
                                  binning=None,
                                  window=None,
                                  shutter='OPEN',
                                  compress=False,
                                  wait_dome=True,
                                  object_name=obj1)

            currentFrame = 0

            self.out(msg2)
            self.out('Slewing')
            self.telescope.slewToRaDec(radec2)
            # center on PiggyBack
            self.out('Offset E')
            self.telescope.moveEast(Coord.fromAS(1580))
            self.out('Offset S')
            self.telescope.moveSouth(Coord.fromAS(972))

            self.out('Acquiring')
            self.camera.expose(exptime=exptime2,
                                  frames=1,
                                  interval=0.,
                                  filename=filename,
                                  type='OBJECT',
                                  binning=None,
                                  window=None,
                                  shutter='OPEN',
                                  compress=False,
                                  wait_dome=True,
                                  object_name=obj2)

            self.out('='*len(msg1))

        #self.wait(abort=True)
    ############################################################################

    def __abort__(self):
        self.out("\naborting... ", endl="")

        # copy self.camera Proxy because we are running from a different
        # thread (yes, Pyro is tricky!)
        cam = copy.copy(self.camera)
        cam.abortExposure()

    ############################################################################

################################################################################
def main():
    cli = TestDPT_PB()
    cli.run(sys.argv)
    cli.wait()

################################################################################

if __name__ == '__main__':

    main()

################################################################################
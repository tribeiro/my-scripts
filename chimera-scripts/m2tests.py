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

class M2Test (ChimeraCLI):

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
        self.addHelpGroup("FOCUS", "Focus")

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

        self.addHelpGroup("FOCUS", "Focus")
        self.addInstrument(name="focuser",
                           cls="Focuser",
                           required=True,
                           helpGroup="FOCUS",
                           help="Focuser instrument to be used")

        self.addParameters(dict(name="minalt", long="minaltitude", type=float,
                                help="Minimum altitude in the grid.",default=30.,
                                metavar="minalt"))
        self.addParameters(dict(name="maxalt", long="maxaltitude", type=float,
                                help="Maximum altitude in the grid.",default=80.,
                                metavar="maxalt"))
        self.addParameters(dict(name="stepalt", long="stepaltitude", type=float,
                        help="Maximum altitude in the grid.",default=10.,
                        metavar="stepalt"))
        self.addParameters(dict(name="minaz", long="minazimuth", type=float,
                                help="Minimum azimuth in the grid.",default=10.,
                                metavar="minaz"))
        self.addParameters(dict(name="maxaz", long="maxazimuth", type=float,
                                help="Maximum azimuth in the grid.",default=360.,
                                metavar="maxaz"))
        self.addParameters(dict(name="stepaz", long="stepazimuth", type=float,
                        help="Maximum azimuth in the grid.",default=90.,
                        metavar="stepaz"))
        self.addParameters(dict(name="exptime", long="exptime", type=float,
                        help="Exposure time",default=30.,
                        metavar="exptime"))
        self.addParameters(dict(name="stepfocus", long="stepfocus", type=int,
                        help="Step in focus",default=400,
                        metavar="stepfocus"))
        self.addParameters(dict(name="frames", long="frames", type=int,
                        help="Number of frames per position",default=1,
                        metavar="frames"))

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

        gridAlt = np.arange(options.minalt,options.maxalt,options.stepalt)
        gridAz  = np.arange(options.minaz,options.maxaz,options.stepaz)

        global currentFrame

        for alt in gridAlt:
            for az in gridAz:
                altAz = Position.fromAltAz(Coord.fromD(alt),
                                           Coord.fromD(az))
                #self.out('alt/az: %s '%(altAz))
                radec = site.altAzToRaDec(altAz)
                self.out('alt/az: %s -> ra/dec: %s'%(altAz,radec))
                self.telescope.slewToRaDec(radec)

                self.camera.expose(exptime=options.exptime,
                                      frames=1,
                                      interval=0.,
                                      filename=filename,
                                      type='OBJECT',
                                      binning=None,
                                      window=None,
                                      shutter='OPEN',
                                      compress=False,
                                      wait_dome=True,
                                      object_name='%s M2 Test Focus 0.0'%altAz)

                currentFrame = 0

                self.focuser.moveOut(options.stepfocus)

                self.camera.expose(exptime=options.exptime,
                                      frames=1,
                                      interval=0.,
                                      filename=filename,
                                      type='OBJECT',
                                      binning=None,
                                      window=None,
                                      shutter='OPEN',
                                      compress=False,
                                      wait_dome=True,
                                      object_name='%s M2 Test Focus +%i'%(altAz,options.stepfocus))

                currentFrame = 0

                self.focuser.moveIn(options.stepfocus*2.)

                self.camera.expose(exptime=options.exptime,
                                      frames=1,
                                      interval=0.,
                                      filename=filename,
                                      type='OBJECT',
                                      binning=None,
                                      window=None,
                                      shutter='OPEN',
                                      compress=False,
                                      wait_dome=True,
                                      object_name='%s M2 Test Focus -%i'%(altAz,options.stepfocus))

                currentFrame = 0

                self.focuser.moveOut(options.stepfocus)

        #self.wait(abort=True)
    ############################################################################

    def __abort__(self):
        self.out("\naborting... ", endl="")

        # copy self.camera Proxy because we are running from a differente
        # thread (yes, Pyro is tricky!)
        cam = copy.copy(self.camera)
        cam.abortExposure()

    ############################################################################

################################################################################
def main():
    cli = M2Test()
    cli.run(sys.argv)
    cli.wait()

################################################################################

if __name__ == '__main__':

    main()

################################################################################
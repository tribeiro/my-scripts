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
        ''
        self.addHelpGroup("RUN", "Start/Stop/Info")
        self.addHelpGroup("TELESCOPE", "Telescope")

        self.addInstrument(name="telescope",
                           cls="Telescope",
                           required=True,
                           help="Telescope instrument to be used. If blank, try to guess from chimera.config",
                           helpGroup="TELESCOPE")
    ############################################################################

    @action(help="Start monitoring temperature", helpGroup="RUN", actionGroup="RUN")
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

################################################################################
def main():
    cli = MoniT()
    cli.run(sys.argv)
    cli.wait()

################################################################################

if __name__ == '__main__':

    main()

################################################################################
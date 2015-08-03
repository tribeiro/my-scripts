#!/usr/bin/env python

################################################################################

import sys
import os
import time
import numpy as np
import datetime as dt
import copy

from chimera.core.cli import ChimeraCLI, action, ParameterType
from chimera.controllers.imageserver.imagerequest import ImageRequest
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

class Test (ChimeraCLI):

    ############################################################################

    def __init__(self):
        ChimeraCLI.__init__(self, "test",
                            "", 0.0, port=9010)

        '''
        '''

        self.addHelpGroup("RUN", "Start/Stop/Info")
        self.addHelpGroup("TELESCOPE", "Telescope")
        self.addHelpGroup("CAMERA", "Camera")
        self.addHelpGroup("OBSERVATORY", "Observatory")

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

    @action(help="Start", helpGroup="RUN", actionGroup="RUN")
    def start(self, options):

        import StringIO

        output = StringIO.StringIO()

        ir = ImageRequest(frames = 1,
                          exptime = 2.0,
                          shutter = "OPEN",
                          type = "OBJECT",
                          filename = output,
                          object_name = 'foo',
                          wait_dome=False)

        self.camera.expose(ir)

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
    cli = Test()
    cli.run(sys.argv)
    cli.wait()

################################################################################

if __name__ == '__main__':

    main()

################################################################################
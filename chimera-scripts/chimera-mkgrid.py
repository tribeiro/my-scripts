#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# chimera - observatory automation system
# Copyright (C) 2006-2007  P. Henrique Silva <henrique@astro.ufsc.br>

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.


from chimera.core.cli import ChimeraCLI, action, ParameterType

from chimera.util.coord import Coord
from chimera.util.position import Position
from chimera.util.simbad import Simbad

from chimera.core.callback import callback
from chimera.core.exceptions import ObjectTooLowException, ObjectNotFoundException
from chimera.interfaces.telescope import SlewRate, TelescopeStatus
from chimera.interfaces.camera import CameraStatus

import sys
import copy
import time
import numpy as np

# TODO: Abort, skip_init/init

################################################################################

currentFrame = 0
currentFrameExposeStart = 0
currentFrameReadoutStart = 0

################################################################################


class ChimeraMkgrid (ChimeraCLI):

    def __init__(self):
        ChimeraCLI.__init__(
            self, "chimera-mkgrig", "Telescope controller", 0.1, port=9004)

        self.localSlew = False

        self.addHelpGroup("OBSERVATORY", "Observatory")
        self.addController(name="site",
                           cls="Site",
                           required=True,
                           help="Observing site",
                           helpGroup="OBSERVATORY")


        self.addHelpGroup("TELESCOPE", "Telescope")
        self.addInstrument(name="telescope",
                           cls="Telescope",
                           required=True,
                           help="Telescope instrument to be used. If blank, try to guess from chimera.config",
                           helpGroup="TELESCOPE")

        self.addHelpGroup("CAM", "Camera and Filter Wheel configuration")
        self.addInstrument(name="camera",
                           cls="Camera",
                           help="Camera instrument to be used. If blank, try to guess from chimera.config",
                           helpGroup="CAM", required=True)

        self.addInstrument(name="wheel",
                           cls="FilterWheel",
                           help="Filter Wheel instrument to be used. If blank, try to guess from chimera.config",
                           helpGroup="CAM")

        self.addHelpGroup("FOCUS", "Focus")
        self.addInstrument(name="focuser",
                           cls="Focuser",
                           required=True,
                           helpGroup="FOCUS",
                           help="Focuser instrument to be used")

        self.addHelpGroup("COORDS", "Coordinates")
        self.addParameters(dict(name="alt_min",
                                type="string",
                                helpGroup="COORDS",
                                help="Minimum altitude of the grid."),
                           dict(name="ha_step",
                                type="string",
                                helpGroup="COORDS",
                                help="Hour angle grid step (in hours, at equator)."),
                           dict(
                               name="dec_start",
                               type="string",
                               helpGroup="COORDS",
                               help="Declination."),
                           dict(
                               name="dec_end",
                               type="string",
                               helpGroup="COORDS",
                               help="Declination."),
                           dict(name="dec_step",
                                type="string",
                                helpGroup="COORDS",
                                help="Declination grid step (in degrees)."),
                           dict(
                               name="epoch",
                               type="string",
                               default="J2000",
                               helpGroup="COORDS",
                               help="Epoch"),)
        self.addHelpGroup("EXPOSE", "Exposure control")
        self.addParameters(dict(name="frames",
                                short="n",
                                type="int",
                                default=1,
                                helpGroup="EXPOSE",
                                help="Number of frames"),
                           dict(name="exptime",
                                short="t",
                                type="string",
                                default=1,
                                helpGroup="EXPOSE",
                                help="Integration time in seconds for each frame"),)

        self.addHelpGroup("DISPLAY", "Display configuration")
        self.addParameters(dict(name="disable_display",
                                long="disable-display",
                                type=ParameterType.BOOLEAN,
                                helpGroup="DISPLAY",
                                help="Don't try to display image on DS9. default is display for exptime >= 5"),
                           dict(name="force_display",
                                long="force-display",
                                type=ParameterType.BOOLEAN,
                                helpGroup="DISPLAY",
                                help="Always display image on DS9 regardless of exptime."))

        self.addHelpGroup("OUTPUT", "Output configuration")
        self.addParameters(dict(name="output",
                                short="o",
                                long="output",
                                type="string",
                                helpGroup="OUTPUT",
                                help="Output file name. Store filename,HA,Dec,check."))

        self.addHelpGroup("RUN", "Start/Stop/Info")

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

        dec_start = Coord.fromDMS(options.dec_start)
        dec_end = Coord.fromDMS(options.dec_end)
        dec_step = Coord.fromDMS(options.dec_step)
        alt0 = Coord.fromDMS(options.alt_min)
        ha_step = np.float(Coord.fromHMS(options.ha_step).toH())

        total_pts = 0
        for dec in np.arange(dec_start.D,dec_end.D,dec_step.D):
            dd = Coord.fromD(dec)

            # print alt0.toD(),Coord.fromD(site["latitude"]).toD(), (dd.toD()),np.float( ( alt0.toD()+Coord.fromD(site["latitude"]).toD() ) / (90. + dd.toD()) )
            # ha0 = Coord.fromR(np.abs( np.arccos( np.float( ( alt0.toD()+Coord.fromD(site["latitude"]).toD() ) / (90. + dd.toD()) ) ) ) )

            ha0 = Coord.fromD(alt0.D-np.abs(Coord.fromD(site["latitude"]).toD()-dd.toD()))

            step = ha_step/np.abs(np.cos( np.float(dd.toD()-Coord.fromD(site["latitude"]).toD() )*np.pi/180.))
            npts = 2*ha0.toH()/step
            npts = int(npts) if int(npts) > 1 else 1
            total_pts+=npts
            # self.out("HA: %s"%ha0.toHMS())
            # self.out('Step: %f / %f / %i cos(%f) = %f'%(ha_step,step,npts,dd.toD()-Coord.fromD(site["latitude"]).toD(),
            #                                             np.cos( np.float(dd.toD()-Coord.fromD(site["latitude"]).toD() )*np.pi/180.)))

            if npts > 1:
                ha_grid = np.linspace(-np.float(ha0.toH()),np.float(ha0.toH()),npts)
            else:
                ha_grid = [0.]
            # if len(ha_grid) < 3:
            #     self.out('HA grid @ dec %s too small. Skipping...'%dd.toDMS())
            #     continue

            for HA in ha_grid:
                self.out('Ha/Dec: %s %s'%(Coord.fromH(HA).toHMS(),
                                          dd.toDMS()))
            # self.out("")

        self.out('Total pointings: %i'%total_pts)
        return

        for HA in gridHA:

            hha = Coord.fromH(HA)
            ra = lst+hha
            if ra.H < 0.:
                ra=Coord.fromH(24+ra.H)

            radec = Position.fromRaDec(ra.toHMS(),options.dec)
            self.out("Ra/Dec: %s"%(radec))
            try:
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
                      object_name='M2 Control Law')

            except ObjectTooLowException, e:
                self.err("ERROR: %s" % str(e))
                self.exit()


        return

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
    cli = ChimeraMkgrid()
    cli.run(sys.argv)
    cli.wait()

################################################################################

if __name__ == '__main__':

    main()

################################################################################
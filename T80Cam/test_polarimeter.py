
import logging
from chimera_t80cam.instruments.ebox.fsufilters.filterwheelsdrv import FSUFilterWheel
log = logging.getLogger(name=__name__)

class MyFakeChimera:
        def __init__(self):
                self.par = dict(
                        filter_wheel_model="Solunia",
                        waitMoveStart=0.5,
                        plc_ams_id="5.18.26.30.1.1",
                        plc_ams_port=801,
                        plc_ip_adr="192.168.100.1",
                        plc_ip_port=48898,
                        pc_ams_id="5.18.26.31.1.1",
                        pc_ams_port=32788,
                        plc_timeout=5)
                self.log = log

        def __getitem__(self, item):
                return self.par[item]


par = MyFakeChimera()

fsu = FSUFilterWheel(par)

print fsu.get_pos()


print fsu._vread1 .read()
print fsu._vread10.read()
print fsu._vread11.read()
print fsu._vread12.read()
print fsu._vread20.read()
print fsu._vread21.read()
print fsu._vread22.read()
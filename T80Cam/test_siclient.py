
import time
import threading
from si.client import SIClient
from si.imager import Imager
from si.commands.camera import *
import logging

logging.basicConfig(format='%(levelname)s:%(asctime)s::%(message)s',
                    level=logging.DEBUG)

client = SIClient('192.168.30.103',2055)
client.connect()

# for i in range(5):
#     logging.debug('loop %i' % i)
#     time.sleep(1)

# lines = client.executeCommand(
#             GetStatusFromCamera())

# client.executeCommand(SetExposureTime(0.))
# # client.executeCommand(Acquire())
# client.executeCommand(Acquire())
# client.executeCommand(SaveImage("teste01"))
# client.executeCommand(Acquire())
# client.executeCommand(SaveImage("teste02"))


exposeThread1 = threading.Thread(target=client.executeAcquire,
                                args=(SetExposureTimeAndAcquire(0.),))
exposeThread2 = threading.Thread(target=client.executeAcquire,
                                args=(SetExposureTimeAndAcquire(0.),))

client.exposeComplete.acquire()
logging.info("Starting thread and waiting for exposure to complete.")
exposeThread1.start()
client.exposeComplete.wait()
client.exposeComplete.release()
logging.info("Exposure complete. Waiting for read out to complete.")
exposeThread1.join()

client.exposeComplete.acquire()
logging.info("Starting thread and waiting for exposure to complete.")
exposeThread2.start()
client.executeCommand(SaveImage("teste01"))

client.exposeComplete.wait()
client.exposeComplete.release()
logging.info("Exposure complete. Waiting for read out to complete.")
exposeThread2.join()
client.executeCommand(SaveImage("teste02"))

# exposeThread2.start()
# exposeThread2.join()

# client.executeAcquire(SetExposureTimeAndAcquire(5.))
#
# logging.debug('Exposure 1 ended')
#
# client.executeCommand(SetExposureTimeAndAcquire(20.))

# for i in range(5):
#     logging.debug('loop %i' % i)
#     time.sleep(1)

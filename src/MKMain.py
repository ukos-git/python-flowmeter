#!/usr/bin/env python
import time

from MKArduino import MKArduino
from MKFlowMain import MKFlow

# Create threads
arduino = MKArduino()
#ethanol = MKFlow('/dev/ttyUSB2', '/dev/ttyUSB3', 0)
#argon   = MKFlow('/dev/ttyUSB0', '/dev/ttyUSB1', 1)

# Add threads to List
threads = []
threads.append(arduino)
#threads.append(ethanol)
#threads.append(argon)

# Start Threads
for t in threads:
    print "starting ..."
    t.start()
    print "started."

try:
    #threads[0].startDebug()
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    # close threads
    for t in threads:
        print "stoping ..."
        t.stop()
        print "stoped."
    raise

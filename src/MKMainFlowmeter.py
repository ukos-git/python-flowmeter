#!/usr/bin/env python
import time

from MKFlowMain import MKFlow

ethanol = MKFlow('/dev/ttyUSB2', '/dev/ttyUSB3', 0)
argon   = MKFlow('/dev/ttyUSB0', '/dev/ttyUSB1', 1)

threads = []
threads.append(ethanol)
threads.append(argon)

for t in threads:
    print "starting ..."
    t.start()
    t.debug()
    print "started."

try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    for t in threads:
        print "stoping ..."
        t.stop()
        print "stoped."
    raise

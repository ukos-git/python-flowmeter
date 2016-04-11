#!/usr/bin/env python
import subprocess

def runProcess(exe):
    p = subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while(True):
        retcode = p.poll() #returns None while subprocess is running
        line = p.stdout.readline()
        yield line
        if(retcode is not None):
            break
for line in runProcess('socat -x /dev/ttyUSB2,raw,echo=0,b38400,crnl /dev/ttyUSB3,raw,echo=0,b38400,crnl'.split()):
    print line

#!/usr/bin/env python

import subprocess
import threading

class MKFlowSocat:
    def __init__(self, port1, port2):
        self.buffer = []
        self.port1 = port1
        self.port2 = port2

    def start(self):
        try:
            self.alive = True
            self.thread = threading.Thread(target=self.loop)
            self.thread.daemon = True # never care about it anymore
            self.thread.start()
        except:
            print 'error stopping thread'

    def stop(self):
        try:
            self.close()
        except:
            print 'error stopping thread'
        else:
            self.alive = False

    def join(self):
        self.thread.join()

    def open(self):
        exe = 'socat -x %s,raw,echo=0,b38400,crnl %s,raw,echo=0,b38400,crnl' % (self.port1, self.port2)
        self.popen = subprocess.Popen(exe.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def close(self):
        try:
            self.popen.terminate()
            self.popen.wait()
        except:
            print "error closing socat"
            raise

    def loop(self):
        for line in iter(self.popen.stdout.readline, b''):
            self.buffer.append(line)

    def read(self):
        if self.buffer[0][0] == "<" or self.buffer[0][0] == ">":
            return self.buffer.pop(0), self.buffer.pop(0)
        elif len(self.buffer[0]) == 0:
            # message 1 is empty. pop two messages
            return self.buffer.pop(0), self.buffer.pop(0)
        else:
            # message 1 is missing in rpi's socat
            return '', self.buffer.pop(0)

    def isReady(self):
        size = self.bufferSize()
        if size > 30:
            self.buffer = [self.buffer[-1]]
            print "buffer overflow"
            return True
        return size > 0

    def bufferSize(self):
        return len(self.buffer)

    def isAlive(self):
        return self.alive

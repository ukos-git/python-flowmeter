#!/usr/bin/env python
#import struct                  # imports struct API ???
import os                       # imports file system functions like open()
import time                     # sleep
import MKFlowMessage            # Message analyis class
# Main Class
class MKFlowInput():
    def __init__(self):
        self.logfile = '/home/matthias/Documents/programs/python/swnt-reactor/data/log/bridge/testing/log2.log'
        self.openmode='r'
        self.message1 = ''
        self.message2 = ''
        self.fsoOpen    = False
        self.ready = False
        self.selfTest()

    def open(self):
        if (not self.fsoOpen):
            try:
                self.fso = open(self.logfile, self.openmode)
            except:
                self.close()
                raise ValueError('cannot open log file at ' + self.logfile)
            else:
                self.fsoOpen = True

    def close(self):
        if self.fsoOpen:
            try:
                self.fso.close()
            except:
                raise ValueError('cannot close log file at ' + self.logfile)
            else:
                self.fsoOpen = False

    def write(self, strWrite):
        self.open()
        self.fso.write(strWrite)
        self.fso.write('\n')
        self.close()

    def getMessage(self):
        try:
            message2 = ''
            counter = 0
            while self.readOut() and counter < 100:
                Message = self.Message(self.message1, self.message2)
                if Message.isInvalid:
                    counter += Message.getLength()
                    Message.setLength(counter)
                    message2 += self.message2
                    Message.reprocess(self.message1, message2)
                if not Message.isInvalid:
                    return Message
            if counter == 99:
                raise ValueError('Too many invalid Bytes')
        except:
            raise
            raise ValueError('Message Invalid or EOF reached')
            return None

    def isValid(self):
        try:
            if not self.message1:
                raise ValueError('message1 invalid')
            if not self.message2:
                raise ValueError('message2 invalid')
        except:
            # no raise here. message is invalid.
            return False
        else:
            return True

    def setLogFile(self,filename):
        self.logfile = filename

    def readOut(self):
        self.read()
        while not self.isReady():
            print "read failed. sleeping ..."
            time.sleep(0.1)
            self.read()
        # reset "ready-flag" at message readout
        self.ready = False
        if self.isValid():
            return True
        else:
            return False


    def read(self):
        try:
            if not self.ready:
                self.open()
                self.message1 = self.fso.readline()
                self.message2 = self.fso.readline()
        except:
            # no raise here. we are not ready.
            self.ready = False
            self.close()
        else:
            self.ready = True


    def isReady(self):
        if self.ready:
            return True
        else:
            return False

    def isAlive(self):
        return self.alive

    def kill(self):
        self.alive = False

    def selfTest(self):
        try:
            self.open()
            self.close()
        except:
            self.alive = False
        else:
            self.alive = True

    # shortcut
    class Message(MKFlowMessage.MKFlowMessage):
        class Invalid(MKFlowMessage.MKFlowInvalid):
            pass
        class Error(MKFlowMessage.MKFlowError):
            pass
        class Status(MKFlowMessage.MKFlowStatus):
            pass
        class Request(MKFlowMessage.MKFlowRequest):
            pass
        class Sent(MKFlowMessage.MKFlowSent):
            pass
        #class SetRequest(MKFlowMessage.MKFlowSetRequest):
        #    pass
# end MKFlow

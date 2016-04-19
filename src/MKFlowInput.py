#!/usr/bin/env python
#import struct                  # imports struct API ???
import os                       # imports file system functions like open()
import time                     # sleep
import subprocess               # socat
import MKFlowMessage            # Message analyis class
from MKFlowSocat import MKFlowSocat
from MKFlowLogFile import MKFlowLogFile
# Main Class
class MKFlowInput():
    def __init__(self):
        self.reset()

    def reset(self):
        self.message1 = ''
        self.message2 = ''
        self.socat = False
        self.log = False
        self.port1 = ''
        self.port2 = ''

    def setLogFile(self,filename):
        self.input = MKFlowLogFile(filename)
        self.start()

    def setBridge(self, port1, port2):
        self.input = MKFlowSocat(port1, port2)
        self.start()

    def start(self):
        self.input.open()
        self.input.start()

    def stop(self):
        self.input.stop()

    def readOut(self):
        while not self.input.isReady():
            time.sleep(0.1)
        self.message1, self.message2 = self.input.read()

    def getMessage(self):
        try:
            Message = self.Message()
            self.readOut()
            Message.process(self.message2, self.message1)
            if Message.isInvalid:
                # try next message. maybe they belong together
                message_buffer = self.message2
                self.readOut()
                Message.process(self.message2, self.message1)
                if Message.isInvalid:
                    message_buffer += self.message2
                    Message.process(message_buffer, self.message1)
                    if Message.isInvalid:
                        print "--- buffer ---"
                        print message_buffer
                        print "---        ---"
                        raise
        except:
            self.input.stop()
            raise
        else:
            return Message

    def isAlive(self):
        return self.input.isAlive()

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


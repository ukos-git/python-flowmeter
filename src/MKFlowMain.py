#!/usr/bin/env python
import threading

from MKFlowInput import MKFlowInput
from MKFlowCommunication import MKFlowCommunication
from MKDatabase import MKDatabase

class MKFlow():
    def __init__(self, port1 = '/dev/ttyUSB2', port2 = '/dev/ttyUSB3', instrument = 0):
        self.Input = MKFlowInput()
        self.Storage = MKFlowCommunication()
        self.Database = MKDatabase()
        self.Input.setBridge(port1, port2)
        #self.Input.setLogFile('/home/matthias/Documents/programs/python/swnt-reactor/data/log/bridge/testing/log1.log')
        self.instrument = instrument
        self.debug = False

    def debug(self):
        self.debug = True

    def start(self):
        try:
            self.thread = threading.Thread(target=self.loop)
            self.thread.daemon = True
            self.thread.start()
        except:
            self.stop()
            raise

    def stop(self):
        self.Input.stop()

    def join(self):
        self.thread.join()

    def loop(self):
        while self.Input.isAlive():
            try:
                Message = self.Input.getMessage()
                SubMessage = Message.getSubType()
            except:
                break
            else:
                if not Message.isInvalid:
                    node = Message.getNode()
                    sequence = Message.getSequence()
                    Entity = self.Storage.Node(node).Sequence(sequence)
                    try:
                        if Message.isError:
                            Entity.setError(Message)
                        elif Message.isStatus:
                            Entity.setStatus(Message)
                        elif Message.isSent:
                            Entity.setAnswer(Message)
                        elif Message.isSentStatus:
                            Entity.setWriteRequest(Message)
                        elif Message.isRequest:
                            Entity.setReadRequest(Message)
                        else:
                            raise
                    except:
                        print "--- something happened ---"
                        try:
                            Message.stdout()
                            Submessage.stdout()
                            Entity.reset()
                        except:
                            raise
                    else:
                        # store if two messages are present in current Entity
                        # reset Entity afterwards.
                        try:
                            if self.debug:
                                print "Buffer: %i" % self.Input.input.bufferSize()
                                Entity.output()
                            #Entity.save(self.Database, self.instrument)
                            pass
                        except ValueError:
                            raise
                            pass
                        except:
                            raise
                else:
                    print "--- invalid ---"
                    SubMessage.stdoutShort(Message.stdoutShort())
                    pass


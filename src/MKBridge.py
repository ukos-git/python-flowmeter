#!/usr/bin/env python
from MKFlowInput import MKFlowInput
from MKFlowCommunication import MKFlowCommunication
from MKDatabase import MKDatabase

def main():
    Input = MKFlowInput()
    #Input.setLogFile('/home/matthias/Documents/programs/python/swnt-reactor/data/log/bridge/testing/log1.log')
    Input.setBridge('/dev/ttyUSB2', '/dev/ttyUSB3')
    Storage = MKFlowCommunication()
    Database = MKDatabase()
    while Input.isAlive():
        try:
            Message = Input.getMessage()
            SubMessage = Message.getSubType()
        except:
            raise # reraise for debug reasons
            break
        else:
            if not Message.isInvalid:
                node = Message.getNode()
                sequence = Message.getSequence()
                Entity = Storage.Node(node).Sequence(sequence)
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
                        Entity.output()
                        Entity.save(Database)
                    except ValueError:
                        raise
                        pass
                    except:
                        raise
            else:
                print "--- invalid ---"
                SubMessage.stdoutShort(Message.stdoutShort())
                pass
main()



#!/usr/bin/env python
from MKFlowInput import MKFlowInput
from MKFlowCommunication import MKFlowCommunication
from MKDatabase import MKDatabase

def main():
    Input = MKFlowInput()
    Input.setLogFile('/home/matthias/Documents/programs/python/swnt-reactor/data/log/bridge/testing/log1.log')
    Storage = MKFlowCommunication()
    Database = MKDatabase()
    while Input.isAlive():
        try:
            Message = Input.getMessage()
            SubMessage = Message.getSubType()
        except:
            Input.kill()
            break
        else:
            if not Message.isInvalid:
                node = Message.getNode()
                sequence = Message.getSequence()
                Entity = Storage.Node(node).Sequence(sequence)
                try:
                    if Message.isError:
                        Entity.setError(Message)
                    if Message.isStatus:
                        Entity.setStatus(Message)
                    if Message.isSent:
                        Entity.setAnswer(Message)
                    if Message.isSentStatus:
                        Entity.setWriteRequest(Message)
                    if Message.isRequest:
                        Entity.setReadRequest(Message)
                except:
                    print "--- something happened ---"
                    Message.stdout()
                    Submessage.stdout()
                    Entity.reset()
                else:
                    # store if two messages are present in current Entity
                    # reset Entity afterwards.
                    try:
                        #Entity.output()
                        Entity.save(Database)
                    except ValueError:
                        pass
                    except:
                        raise
            else:
                print "--- invalid ---"
                SubMessage.stdoutShort(Message.stdoutShort())
                pass
main()



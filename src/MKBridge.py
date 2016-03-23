#!/usr/bin/env python
from MKFlowInput import MKFlowInput

def main():
    Input = MKFlowInput()
    Input.setLogFile('/home/matthias/Documents/programs/python/swnt-reactor/data/log/bridge/testing/log2.log')
    i=0
    while Input.isAlive() and i < 10000:
        i+=1
        if Input.isReady():
            try:
                Message = Input.getMessage()
            except:
                Input.kill()
                pass
            else:
                if Message.isInvalid:
                    print "%i\t  --- invalid ---" % i
                    Message.stdout()
                    Message.Invalid.stdout()
                    print Message.Invalid.stdoutShort(Message.stdoutShort(i))
                    pass
                if Message.isError:
                    print "%i\t --- error ---" % i
                    Message.stdout()
                    Message.Error.stdout()
                    print Message.Error.stdoutShort(Message.stdoutShort(i))
                    pass
                if Message.isStatus:
                    print "%i\t --- status ---" % i
                    Message.stdout()
                    Message.Status.stdout()
                    print Message.Status.stdoutShort(Message.stdoutShort(i))
                    pass
                if Message.isSent:
                    print "%i\t --- send ---" % i
                    Message.stdout()
                    Message.Sent.stdout()
                    print Message.Sent.stdoutShort(Message.stdoutShort(i))
                    pass
                if Message.isRequest:
                    print "%i\t --- request ---" % i
                    Message.stdout()
                    Message.Request.stdout()
                    print Message.Request.stdoutShort(Message.stdoutShort(i))
                    pass                        
main()

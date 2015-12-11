#!/usr/bin/env python
from MKFlow import MKFlow

def main():
    Bridge = MKFlow()
    Bridge.setLogFile('/home/matthias/CVDapp/data/log/bridge/testing/log2.log')
    if not Bridge.isReady():
        print Bridge.getError()
    i=0
    while True and i<1000:
        i+=1
        try:
            Bridge.read()        
            Message = Bridge.getMessage()
        except:
            raise
            break
        else:
            if Message.isInvalid:
                #Message.stdout()
                #Message.Invalid.stdout()
                print Message.Invalid.stdoutShort(Message.stdoutShort(i))
                pass
            if Message.isError:
                #Message.stdout()
                #Message.Error.stdout()
                print Message.Error.stdoutShort(Message.stdoutShort(i))
                pass
            if Message.isStatus:
                #Message.stdout()
                #Message.Status.stdout()
                print Message.Status.stdoutShort(Message.stdoutShort(i))
                pass
            if Message.isSent:
                #Message.stdout()
                #Message.Sent.stdout()
                print Message.Sent.stdoutShort(Message.stdoutShort(i))
                pass
            if Message.isRequest:
                #Message.stdout()
                #Message.Request.stdout()
                print Message.Request.stdoutShort(Message.stdoutShort(i))
                pass                        
main()

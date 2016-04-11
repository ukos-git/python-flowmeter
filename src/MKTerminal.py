#!/usr/bin/env python

import sys, os, threading, time

if sys.version_info >= (3, 0):
    def character(b):
        return b.decode('latin1')
else:
    def character(b):
        return b

class MKConsole(object):
    def __init__(self):
        self.fd = sys.stdin.fileno()

    def getkey(self):
        c = os.read(self.fd, 1)
        return c

class MKTerminal(object):
    EXITCHARCTER = 'q'
    message = ''
    alive=False
    readyToSend=False
    readyToDisplay=False

    def __init__(self,echo=False):
        self.echo = echo
        self.Console = MKConsole()

    def start(self):
        self.alive = True
        self.readerthread = threading.Thread(target=self.read)
        self.readerthread.setDaemon(True) # never care about it anymore
        self.readerthread.start()
        self.writerthread = threading.Thread(target=self.write)
        self.writerthread.setDaemon(True) # never care about it anymore
        self.writerthread.start()

    def join(self):
        self.readerthread.join()

    def stop(self):
        self.alive = False

    def send(self,myChar):
        if myChar == '\n':
            self.readyToSend=True
        else:
            self.message+=myChar

    def read(self):
        while self.alive:
            try:
                b = self.Console.getkey()
                c = character(b)
                if c == self.EXITCHARCTER:
                    raise KeyboardInterrupt
                self.send(c)
                if self.echo == True:
                    sys.stdout.write(c)
                    sys.stdout.flush()
                time.sleep(0.1)
            except KeyboardInterrupt:
                self.stop()

    def write(self):
        while self.alive:
            if self.readyToDisplay:
                sys.stdout.write(self.printme)
                sys.stdout.flush()
                self.readyToDisplay=False
            time.sleep(0.1)

    def isAlive(self):
        return self.alive

    def isReady(self):
        return self.readyToSend

    def getMessage(self):
        message=self.message
        self.message=''
        self.readyToSend=False
        return message

    def display(self,text):
        self.readyToDisplay=True
        self.printme=text

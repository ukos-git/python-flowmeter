#!/usr/bin/env python
from __future__ import print_function
import threading
import time
import sys

from MKDatabase import MKDatabase
from MKParser import MKParser
from MKLogFile import MKLogFileHandler
from MKSerial import MKSerial

class MKArduino():
    def __init__(self, port = '/dev/ttyACM0'):
        self.Serial = MKSerial('arduino', port, 9600)
        self.Parser = MKParser()
        self.Database = MKDatabase()
        self.newFile = True
        self.setFile = False
        self.alive = False
        self.sleeping = False
        self.debugging = False

    def debug(self):
        self.debugging = True

    def start(self):
        try:
            self.Serial.start()
            self.thread = threading.Thread(target=self.loop)
            self.thread.daemon = True
            self.thread.start()
        except:
            self.stop()
            raise
        else:
            self.alive = True

    def stop(self):
        self.alive = False
        self.Serial.stop()

    def join(self):
        self.thread.join()

    def isAlive(self):
        return self.alive

    def loop(self):
        if self.debugging:
            print('entering loop ...')
        while self.isAlive():
            serialReady = self.Serial.isReady()
            databaseReady = self.Database.isReady()
            if not serialReady and not databaseReady:
                if self.debugging:
                    if not self.sleeping:
                        print('sleeping .', end = '')
                        self.sleeping = True
                    else:
                        print('.', end = '')
                    sys.stdout.flush()
                time.sleep(0.1)
            else:
                if self.debugging:
                    if self.sleeping:
                        print('.', end = '\n')
                        sys.stdout.flush()
                        self.sleeping = False
                    if serialReady:
                        print('serial ready with %i messages' % len(self.Serial.receiveBuffer))
                    if databaseReady:
                        print('database ready')
            if databaseReady:
                if self.debugging:
                    print('database ready ...')
                self.Serial.send(self.Database.getMessage())
            if serialReady:
                message = self.Serial.getMessage()
                self.Parser.input(message)
                oneline = self.Parser.oneline()
                if self.debugging:
                    print(oneline)
                if not self.Parser.isHeadline() and self.Parser.getStatus():
                    setData = self.Database.setData(self.Parser.get(2), self.Parser.get(5), self.Parser.get(8), self.Parser.get(11))
                    setSP = self.Database.setSetpoint(self.Parser.get(3), self.Parser.get(6), self.Parser.get(9), self.Parser.get(12))
                    if not setData or not setSP:
                        # database write failed. add message to buffer again
                        self.Serial.receive(message)
                if self.Database.isRecording():
                    if self.newFile:
                        print('starting new LogFile.')
                        self.Logfile = MKLogFileHandler('mkmain','log',True)
                        self.Logfile.open()
                        self.newFile = False
                        self.setFile = True
                    if self.setFile:
                        print('set FileName in Database')
                        if self.Database.setLogFile(self.Logfile.getLogFile()):
                            self.setFile = False
                    self.Logfile.write(oneline)
                else:
                    self.newFile = True


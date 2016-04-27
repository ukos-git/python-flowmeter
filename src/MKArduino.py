#!/usr/bin/env python
from __future__ import print_function
import threading
import time
import sys
from datetime import datetime

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
        self.verbose = 0

    def debug(self, verbose = 1):
        self.verbose = verbose

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

    def getPerformance(self):
        if self.verbose < 0:
            microsecond = datetime.now().microsecond
            print(self.perfCounter, "\t", int((microsecond - self.performance)/100)/10.0)
            self.performance = microsecond
            self.perfCounter += 1

    def resetPerformance(self):
        if self.verbose < 0:
            print('---')
            self.perfCounter = 0
            self.performance = datetime.now().microsecond
            self.getPerformance()

    def loop(self):
        if self.verbose > 1:
            print('entering loop ...')
        while self.isAlive():
            self.resetPerformance()
            serialReady = self.Serial.isReady()
            self.getPerformance()
            databaseReady = self.Database.isReady()
            self.getPerformance()
            if not serialReady and not databaseReady:
                if self.verbose > 0:
                    if not self.sleeping:
                        if self.verbose > 1:
                            print('sleeping .', end = '')
                        else:
                            print('.', end = '')
                        self.sleeping = True
                    else:
                        print('.', end = '')
                    sys.stdout.flush()
                self.getPerformance()
                time.sleep(0.1)
                self.getPerformance()
            else:
                if self.verbose > 0:
                    if self.sleeping:
                        print('.', end = '\n')
                        sys.stdout.flush()
                        self.sleeping = False
                    if serialReady:
                        print('serial ready with %i messages' % len(self.Serial.receiveBuffer))
                    if databaseReady:
                        print('database ready')
                self.getPerformance()
            if databaseReady:
                self.Serial.send(self.Database.getMessage())
            if serialReady:
                self.getPerformance()
                message = self.Serial.getMessage()
                self.getPerformance()
                self.Parser.input(message)
                self.getPerformance()
                oneline = self.Parser.oneline()
                self.getPerformance()
                if self.verbose > 2:
                    print(oneline)
                if self.Parser.getStatus():
                    self.getPerformance()
                    data = (self.Parser.get(2), self.Parser.get(5), self.Parser.get(8), self.Parser.get(11))
                    setpoint = (self.Parser.get(3), self.Parser.get(6), self.Parser.get(9), self.Parser.get(12))
                    setData = self.Database.setData(data, setpoint)
                    self.getPerformance()
                    if not setData:
                        if self.verbose > 2:
                            print("database write failed. add message to buffer again.")
                        self.Serial.receive(message)
                self.getPerformance()
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
                self.getPerformance()


#!/usr/bin/env python

import MKTerminal,MKSerial,MKParser,MKDatabase
from MKLogFile import MKLogFileHandler
import threading	# multithreading
import time			# sleep

#def transmitter(mySerial arduino, myTerminal terminal):

def main():
	def myTransmitter(arduino, terminal):
		#while arduino.isAlive() and terminal.isAlive():
		parser = MKParser.MKParser()
		database = MKDatabase.MKDatabase()
		newFile = True
		while True:
			if terminal.isReady():
				arduino.send(terminal.getMessage())
			if arduino.isReady():
				parser.input(arduino.getMessage())
				oneline = parser.oneline()
				if parser.getStatus():
					terminal.display(oneline)
					#terminal.display("")
				if not parser.isHeadline() and parser.getStatus():
					database.setData(parser.get(2), parser.get(5), parser.get(8), parser.get(11))
					database.setSetpoint(parser.get(3), parser.get(6), parser.get(9), parser.get(12))
				if database.isRecording():
					if newFile:
						logfile = MKLogFileHandler('mkmain','log',True)
						logfile.open()
						database.setLogFile(logfile.getLogFile())
						newFile = False
					logfile.write(oneline)
				else:
					newFile = True
			if database.isReady():
				arduino.send(database.getMessage())
			time.sleep(0.1)
	threads = []

	# Create new threads
	arduino = MKSerial.MKSerial('arduino','/dev/ttyACM0',9600)
	terminal = MKTerminal.MKTerminal()
	transmitter = threading.Thread(target=myTransmitter, args=(arduino,terminal))
	transmitter.setDaemon(True) # never care about it anymore

	# Add threads to thread list
	threads.append(arduino)
	threads.append(terminal)
	threads.append(transmitter)#append after arduino and terminal!

	# Start new Threads
	for t in threads:
		t.start()

	terminal.join()
main()

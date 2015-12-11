#!/usr/bin/env python

import MKTerminal,MKSerial,MKParser
import threading					# multithreading
from time import sleep

#def transmitter(mySerial arduino, myTerminal terminal):

def main():	
	def myTransmitter(arduino, terminal):
		#while arduino.isAlive() and terminal.isAlive():
		parser = MKParser.MKParser()
		while True:
			if terminal.isReady():
				arduino.send(terminal.getMessage())
			if arduino.isReady():
				terminal.display(parser.input(arduino.getMessage()))
				
	threads = []

	# Create new threads
	arduino = MKSerial.MKSerial('arduino','/dev/ttyACM0',9600)
	terminal = MKTerminal.MKTerminal()
	transmitter = threading.Thread(target=myTransmitter, args=(arduino,terminal))
	transmitter.setDaemon(True) # never care about it anymore
			
	# Add threads to thread list
	threads.append(arduino)	
	threads.append(terminal)	
	threads.append(transmitter)	#append after arduino and terminal!

	# Start new Threads
	for t in threads:
		t.start()

	terminal.join()
main()

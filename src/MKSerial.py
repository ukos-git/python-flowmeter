#!/usr/bin/env python

import serial						# imports pyserial API
import struct						# imports struct API
import sys							# sys.exit()
import threading					# multithreading
from MKLogFile import MKLogFileHandler

LF = serial.to_bytes([10])
CR = serial.to_bytes([13])
CRLF = serial.to_bytes([13, 10])
		
class MKSerial:	
	sendBuffer = ''
	receiveBuffer=''
	alive=False
	ready=False
	
	serialName='unnamed'	
	serialPort=''
	serialBaudrate = 9600
	newline=CRLF
	def __init__(self,serialName='arduino',serialPort='/dev/ttyACM0',serialBaudrate=9600):
		self.serialName = serialName
		self.serialPort = serialPort
		self.serialBaudrate = serialBaudrate
		
		self.openLogfiles()
		self.openSerial()
		#self.start() # automatically start threading
		
	def openLogfiles(self):		
		try:
			self.error = MKLogFileHandler(self.serialName,'error')
			self.error.open()
		except:
			print 'Error creating file: error.log'
			sys.exit(1)
		try:
			self.run = MKLogFileHandler(self.serialName,'run')
			self.log = MKLogFileHandler(self.serialName,'log')
			self.run.open()
			self.log.open()
		except:
			self.error.write('error opening log files')
			
	def openSerial(self):
		self.error.write('opening RS232 for ' + self.serialName + ' on Port ' + self.serialPort + ' with ' + str(self.serialBaudrate) + ' baud')
		try:
			self.serial = serial.Serial()
			self.serial.port     = self.serialPort
			self.serial.baudrate = self.serialBaudrate
			self.serial.timeout  = 3     # required so that the readline can exit.
		except self.serial.SerialException, e:
			self.error.write('error initializing serial class')
			sys.exit(1)
		try:
			self.serial.open()
			self.serial.setDTR(True)
			self.serial.setRTS(True)
		except self.serial.SerialException, e:
			self.error.write('Could not open serial port')
			sys.exit(1)
			
	def start(self):
		self.error.write('stopping thread')
		try:			
			self.alive = True
			self.thread = threading.Thread(target=self.infiniteloop)
			self.thread.daemon = True # never care about it anymore
			self.thread.start()
		except:
			self.error.write('error stopping thread')

	def join(self):
		self.thread.join()
		
	def stop(self):		
		self.error.write('stopping thread')
		try:		
			self.alive = False
			#self.join()
		except:
			self.error.write('error stopping thread')
		self.close()
					
	def close(self):
		self.error.write('closing serial connection')
		try:
			self.serial.setDTR(False)
			self.serial.setRTS(False)
			self.serial.close()
		except:
			self.error.write('error closing serial connection')
		
	def send(self,message):
		self.sendBuffer+=message
	
	def read(self):
		val = self.serial.readline();  #read line by line data from the serial file
		self.receiveBuffer+=val 	#clear from time to time!
		self.ready=True
		self.log.write(val)
		self.run.write(val)		
		
	def write(self):
		if not self.sendBuffer == '':
			self.error.write('sending message ' + self.sendBuffer)
			try:
				self.serial.write(self.sendBuffer)
				self.serial.write(self.newline)				
			except:
				self.error.write('error sending message')
			else:
				self.sendBuffer=''
				
	def infiniteloop(self):	
		self.error.write('starting infinite Loop on ' + self.serial.port)
		while (self.serial.isOpen() and self.alive):
			try:
				self.read()
				self.write()
			except:
				self.error.write('Exception in infinite Loop')
				self.stop()
				
	def isAlive(self):
		return self.alive
		
	def isReady(self):		
		return self.ready
		
	def getMessage(self):
		text = self.receiveBuffer
		self.receiveBuffer=''
		self.ready=False
		return text

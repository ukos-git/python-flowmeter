#!/usr/bin/env python
from MKLogFile import MKLogFileHandler
import sys

class MKParser:
	name = 'parser'
	message = ['time','Temperature','temp','spTemp','Pressure','press','spPress','Argon','argon','spArgon','EtOH','etoh','spEtoh']
	length = 0
	status = False
	def __init__(self):
		try:
			self.error = MKLogFileHandler(self.name,'error')
			self.error.open()
		except:
			print 'Error creating log-file: error.log'
			print self.error.getError()
			sys.exit(1)
		try:
			self.log = MKLogFileHandler(self.name,'run')
			self.log.open()
			self.log.setNewLine('\n')
		except:
			self.error.write('error opening log file')
	def input(self,strInput):
		#self.log.write('input received')
		if self.parse(strInput):
			# process content and save as array
			self.status = True
		else:
			self.error.write('length missmatch in string. Counting ' + str(self.length) + ' items')
			self.status = False
		return self.status
	def parse(self,strInput,intArduinoVersion=None):
		if intArduinoVersion is None:
			intArduinoVersion = 2
			# Default Version (from master thesis) is 2
		# strInput is the string that gets extracted
		# intArduinoVersion is the version
		success = False
		strInput = strInput.replace('\n','')
		extractMe = strInput.split("\t")
		self.length = len(extractMe)
		if intArduinoVersion == 2:
			if self.length == 23:
				self.message[0]=extractMe[0]
				self.message[2]=extractMe[2] # temp
				self.message[3]=extractMe[5] # sptemp
				self.message[5]=extractMe[9] # press
				self.message[6]=extractMe[12]# sppress
				self.message[8]=extractMe[14]# argon
				self.message[9]=extractMe[17]# spargon
				self.message[11]=extractMe[19]# etoh
				self.message[12]=extractMe[22]# spetoh
				success = True
		elif intArduinoVersion == 3:
			if self.length == 18:
				self.message[0]=extractMe[0]
				# self.message[1] = Temperature
				self.message[2]=extractMe[1] # temp
				self.message[3]=extractMe[4] # sptemp
				# self.message[4] = Pressure
				self.message[5]=extractMe[7] # press
				self.message[6]=extractMe[10]# sppress
				# self.message[7] = Argon
				self.message[8]=extractMe[11]# argon
				self.message[9]=extractMe[14]# spargon
				# self.message[10] = Argon
				self.message[11]=extractMe[15]# etoh
				self.message[12]=extractMe[18]# spetoh
				success = True
		return success
	def oneline(self):
		strReturn = ''
		for i in self.message:
			strReturn += i + '\t'
		strReturn += '\n'
		return strReturn
	def isHeadline(self):
		if self.get(2) == "temp":
			return True
		else:
			return False
	def getStatus(self):
		return self.status
	def get(self,position):
		return self.message[position]

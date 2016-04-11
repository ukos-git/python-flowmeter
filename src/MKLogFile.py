#!/usr/bin/env python

import struct						# imports struct API ???
import os							# imports file system functions like open()
import threading					# multithreading
from time import time
from datetime import datetime

class MKLogFileHandler:
	#path_general = os.getcwd() + '/'	#use current working dir path
	path_general	= '/var/local'
	path_log	= '/log'
	path_run	= '/run'
	path		= '/'

	file_run	= '_runtime.log'
	file_log	= '_dummyTIME.log'
	file_error	= '_error.log'

	ready = False
	separator	= '\t'
	newline		= ''
	timestamp_short = False

	error_message = ''

	def __init__(self,path = '',log_type = 'error', fulldate = False):
		self.path = '/' + path
		# update date
		if fulldate:
			self.file_log	= '_' + datetime.now().strftime("%Y%m%d-%H%M%S") + '.log'
		else:
			self.file_log	= '_' + datetime.now().strftime("%Y%m%d") + '.log'

		if  log_type == 'run':
			self.logfile = self.path_general + self.path_run + self.path + self.file_run
			self.openmode='w' #open run-time-log file, delete content first.
			self.timestamp_short = True
		elif log_type ==  'log':
			self.logfile = self.path_general + self.path_log + self.path + self.file_log
			self.openmode='w'
			self.timestamp_short = True
		elif log_type ==  'error':
			self.logfile    = self.path_general + self.path_run + self.path + self.file_error
			self.openmode	= 'w' #open todays log file to add content
			self.separator	= ':\t'
			self.newline	= '\n'


	def open(self):
		try:
			self.fso = open(self.logfile, self.openmode)
		except:
			self.error_message = 'cannot open log file at ' + self.logfile
			raise
		try:
			self.fso.close()
		except:
			self.error_message = 'cannot close log file at ' + self.logfile
			raise
		else:
			self.ready=True


	def timestamp(self):
		if self.timestamp_short:
			return str(time())
		else:
			return datetime.now().strftime("%Y-%m-%d %H:%M:%S") #use %f for microseconds

	def write(self, strWrite):
		with open(self.logfile, 'a') as fso:
			fso.write(self.timestamp())
			fso.write(self.separator)
			fso.write(strWrite)
			fso.write(self.newline)
			fso.close
	def setNewline(self, newline='\n'):
		self.newline = newline
	def getError(self):
		return self.error_message
	def getLogFile(self):
		return self.logfile

#!/usr/bin/env python

import MySQLdb
import os
import socket
import decimal

#cvd-client->rbBmSDP7fSKp87b5

class MKDatabase(object):
	ip = "132.187.77.177"
	sql = ""
	data = ""
	ready = False
	message = ""
	hostname = ""
	recording = False
	filename = ""

	def __init__(self):
		self.hostname = self.getHostname()
		self.ip = self.getIP()
		self.test()
		decimal.getcontext().prec = 2

	def open(self):
		dbHost = self.getIP()
		dbName = "cvd"
		if self.isRaspberry():
			dbUser = "cvd-server"
			dbPass = "Rsna3UTbWWS4TDm3"
		else:
			dbUser = "cvd-client"
			dbPass = "rbBmSDP7fSKp87b5"
		self.db = MySQLdb.connect(
			host = dbHost,
			user = dbUser,
			passwd = dbPass,
			db = dbName,
			)
	def close(self):
		self.db.close()

	def write(self):
		self.open()
		self.cursor = self.db.cursor()
		try:
                    self.cursor.execute(self.sql)
                    self.db.commit()
                    self.close()
		except:
                    self.db.rollback()
                    self.close()
                    raise

	def read(self):
		self.open()
		self.cursor = self.db.cursor()
		self.cursor.execute(self.sql)
		if not self.cursor.rowcount:
			self.data = ""
		else:
			self.data = self.cursor.fetchone()
		self.close

	def test(self):
		self.open()
		self.sql="SELECT VERSION()"
		self.read()
		self.close()
		print "MySQL version : %s " % self.data

	def getHostname(self):
		return socket.gethostname()

	def isRaspberry(self):
		if self.hostname == "":
			self.hostname = getHostname()
		if (self.hostname == "raspberrypi"):
			return True
		else:
			return False

	def getIP(self):
		if (self.hostname == "raspberrypi"):
			self.ip = 'localhost'
		else:
			while self.checkIP() == False:
				if self.ip == "132.187.77.177":
					self.ip = "132.187.77.184"
				else:
					self.ip = "132.187.77.177"
		return self.ip

	def checkIP(self):
		if os.system("ping -c 1 -W 1 " + self.ip + " > /dev/null") == 0:
			return True
		else:
			return False

        def createTables(self):
            self.createArduino()

        def createArduino(self):
            self.sql = """CREATE TABLE `runtime_arduino` (
                    `temperature` decimal(6,2) NOT NULL,
                    `pressure` decimal(6,2) NOT NULL,
                    `argon` decimal(6,2) NOT NULL,
                    `ethanol` decimal(6,2) NOT NULL,
                    `spTemperature` int(11) NOT NULL,
                    `spPressure` int(11) NOT NULL,
                    `spEthanol` int(11) NOT NULL,
                    `spArgon` int(11) NOT NULL
                    ) ENGINE=MEMORY DEFAULT CHARSET=latin1;"""
            self.write()

        def resetArduino(self):
            self.sql = """INSERT INTO `runtime_arduino`
                            (`temperature`, `pressure`, `argon`, `ethanol`, `spTemperature`, `spPressure`, `spEthanol`, `spArgon`)
                        VALUES
                            (23.00, 994.21, 0.00, 50.42, 0, 1000, 0, 0);"""
            self.write()

        def writeArduino(self):
            try:
                self.write()
            except:
                try:
                    temp = self.sql
                    self.createArduino()
                    self.resetArduino()
                    self.sql = temp
                    self.write()
                except:
                    raise
                else:
                    pass

	def setSetpoint(self, temperature, pressure, argon, ethanol):
		self.sql = """UPDATE `cvd`.`runtime_arduino`
			SET	`spTemperature` = %s,
				`spPressure`	= %s,
				`spEthanol`	= %s,
				`spArgon`	= %s
			LIMIT 1;"""  % (temperature, pressure, ethanol, argon)
		self.writeArduino()

	def setData(self, temperature, pressure, argon, ethanol):
		self.temperature = decimal.Decimal(temperature)
		self.pressure = decimal.Decimal(pressure)
		self.argon = decimal.Decimal(argon)
		self.ethanol = decimal.Decimal(ethanol)
		self.sql = """UPDATE `cvd`.`runtime_arduino`
			SET	`temperature`	= %s,
				`pressure`	= %s,
				`ethanol`	= %s,
				`argon`		= %s
			LIMIT 1;"""  % (self.temperature, self.pressure, self.ethanol, self.argon)
                self.writeArduino()

	def setMessage(self, message):
		self.sql = """UPDATE `cvd`.`message`
			SET	`text` = '%s',
				`ready` = 1
			LIMIT 1;"""  % (message)
		self.write()

	def setLogFile(self, filename):
		self.sql = """UPDATE `cvd`.`recording`
			SET	`filename` = '%s'
			WHERE `recording` = 1
			LIMIT 1;""" % (filename)
		self.write()
		self.filename = filename

	def isReady(self):
		self.sql = """SELECT `ready`, `text`
				FROM `cvd`.`message`
				LIMIT 1;"""
		self.read()
		if not len(self.data) == 2:
			self.data = (0,"")
		(self.ready, self.message) = self.data
		return self.ready

	def isRecording(self):
		self.sql = """SELECT `recording`, `filename`
			FROM `cvd`.`recording`
			WHERE `recording` = 1
			LIMIT 1;"""
		self.read()
		if not len(self.data) == 2:
			self.data = (0,"")
		(self.recording, self.filename) = self.data
		return self.recording

	def stopRecording(self):
		self.sql = """UPDATE `cvd`.`recording`
			SET	`recording` = 0
			WHERE `recording` = 1;"""
		self.write()

	def startRecording(self, filename):
		self.sql = """INSERT INTO `cvd`.`recording` (
			`id` ,`time` , `recording` , `filename` )
			VALUES (
			NULL , CURRENT_TIMESTAMP , 1, '%s')""" % (filename)
		self.write()

	def getLogFile(self):
		return self.filename

	def getMessage(self):
		if self.ready:
			# reset message and store in class
			self.sql = """UPDATE `cvd`.`message`
				SET	`ready` = 0,
					`text` = ''
				LIMIT 1;"""
			self.write()
			self.ready = False
			return self.message
		else:
			return ""

	def getAll(self):
		self.open()
		self.sql = "SELECT temperature, pressure, ethanol, argon, spTemperature, spPressure, spEthanol, spArgon from `cvd`.`runtime_arduino` LIMIT 1"
		self.read()
		(self.temperature, self.pressure, self.ethanol, self.argon, self.spTemperature, self.spPressure, self.spEthanol, self.spArgon) = self.data
		self.close()

mydb = MKDatabase()
#mydb.setMessage("test")
#mydb.startRecording("test")
#print mydb.isRecording()
#mydb.stopRecording()
#print mydb.isRecording()
mydb.setData(921,2,3,4)
#mydb.SetSetpoint(10,20,30,40)
mydb.getAll()
print mydb.temperature

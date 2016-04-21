#!/usr/bin/env python

import MySQLdb
from MySQLdb.constants import CLIENT
import os
import socket
import decimal
import struct
from MKFlowMessage import FBconvertLong # converter for long numbers to float and percent
#cvd-client->rbBmSDP7fSKp87b5

class MKDatabase(object):
    ip = "132.187.77.71"
    sql = ""
    data = ""
    ready = False
    messageID = -1
    hostname = ""
    recording = False
    recordingID = -1
    fileName = ""
    storage_description = 50
    storage_values = 30

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
            client_flag = CLIENT.FOUND_ROWS
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
        try:
            self.open()
            self.cursor = self.db.cursor()
            self.cursor.execute(self.sql)
            if not self.cursor.rowcount:
                self.data = ""
            else:
                self.data = self.cursor.fetchone()
            self.close
        except:
            raise

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
        if (self.hostname == "lab117"):
            self.ip = 'localhost'
        else:
            self.ip == "132.187.77.71"
        while not self.checkIP():
            print "ip not found"
            time.sleep(0.1)
        return self.ip

    def checkIP(self):
        if os.system("ping -c 1 -W 1 " + self.ip + " > /dev/null") == 0:
            return True
        else:
            return False

    def createArduino(self):
        self.sql = """CREATE TABLE IF NOT EXISTS `runtime_arduino` (
                `temperature` decimal(6,2) NOT NULL DEFAULT '0',
                `pressure` decimal(6,2) NOT NULL DEFAULT '0',
                `argon` decimal(6,2) NOT NULL DEFAULT '0',
                `ethanol` decimal(6,2) NOT NULL DEFAULT '0',
                `spTemperature` int(11) NOT NULL DEFAULT '0',
                `spPressure` int(11) NOT NULL DEFAULT '1000',
                `spEthanol` int(11) NOT NULL DEFAULT '0',
                `spArgon` int(11) NOT NULL DEFAULT '0'
                ) ENGINE=MEMORY DEFAULT Charset=utf8;"""
        self.write()

    def resetArduino(self):
        self.sql = """INSERT INTO `runtime_arduino`
                        (`temperature`, `pressure`, `argon`, `ethanol`, `spTemperature`, `spPressure`, `spEthanol`, `spArgon`)
                    VALUES
                        (0, 0, 0, 0, 0, 0, 0, 0);"""
        self.write()

    def writeArduino(self):
        try:
            self.write()
            if self.cursor.rowcount == 0:
                raise
        except:
            try:
                temp = self.sql
                try:
                    self.createArduino()
                    self.resetArduino()
                except:
                    pass
                self.sql = temp
                self.write()
            except:
                print self.sql
                raise
            else:
                pass

    def createFlowbus(self):
        self.sql = """
        CREATE TABLE IF NOT EXISTS `runtime_flowbus`
        (
            `instrument`    smallint(2) NOT NULL DEFAULT '0',
            `process`       smallint(2) NOT NULL,
            `flowBus`       smallint(2) NOT NULL,
            `dataType`      tinyint(1) NOT NULL DEFAULT '0',
            `parameter`     binary(%i) NOT NULL DEFAULT '0',
            `data`          binary(%i) NOT NULL DEFAULT '0',
            `time`          decimal(7,2) NOT NULL DEFAULT '0',
            UNIQUE KEY `instrument` (`instrument`,`process`,`flowBus`)
        )
        ENGINE=MEMORY
        DEFAULT CHARSET=utf8;""" % (self.storage_description, self.storage_values)
        self.write()

    def writeFlowbus(self):
        try:
            self.write()
        except:
            try:
                temp = self.sql
                self.createFlowbus()
                self.sql = temp
                self.write()
            except:
                print self.sql
                raise
            else:
                pass

    def createRecording(self):
        self.sql = """CREATE TABLE IF NOT EXISTS `runtime_recording` (
                `id` int(11) NOT NULL AUTO_INCREMENT,
                `recording` tinyint(4) NOT NULL DEFAULT '0',
                `id_recording` int(11) DEFAULT '0',

                PRIMARY KEY (`id`)
                ) ENGINE=MEMORY DEFAULT Charset=utf8 AUTO_INCREMENT=40;"""
        self.write()

        self.sql = """CREATE TABLE IF NOT EXISTS `recording` (
                `id` int(11) NOT NULL AUTO_INCREMENT,
                `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
                `recording` tinyint(4) NOT NULL DEFAULT '0',
                `filename` text NOT NULL,
                PRIMARY KEY (`id`)
                ) ENGINE=InnoDB DEFAULT Charset=utf8 AUTO_INCREMENT=40;"""
        self.write()

    def resetRecording(self):
        self.sql = """INSERT INTO `runtime_recording`
                        (`recording`)
                    VALUES
                        (0)"""
        self.write()

    def writeRecording(self):
        try:
            self.write()
            if self.cursor.rowcount == 0:
                raise
        except:
            try:
                temp = self.sql
                self.createRecording()
                self.resetRecording()
                self.sql = temp
                self.write()
            except:
                raise
            else:
                pass

    def createMessage(self):
        self.sql = """CREATE TABLE IF NOT EXISTS `cvd`.`runtime_message` (
                `id` int(11) NOT NULL AUTO_INCREMENT,
                `ready` tinyint(4) NOT NULL DEFAULT '0',
                `id_message` int(11) DEFAULT '0',

                PRIMARY KEY (`id`)
                ) ENGINE=MEMORY DEFAULT Charset=utf8 AUTO_INCREMENT=40;"""
        self.write()

        self.sql = """CREATE TABLE IF NOT EXISTS  `cvd`.`message` (
                `id` int(11) NOT NULL AUTO_INCREMENT,
                `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
                `processed` tinyint(4) NOT NULL DEFAULT '0',
                `text` text NOT NULL,
                PRIMARY KEY (`id`)
                ) ENGINE=InnoDB DEFAULT Charset=utf8 AUTO_INCREMENT=40;"""
        self.write()

    def resetMessage(self):
        self.sql = """INSERT INTO `cvd`.`runtime_message`
                        (`ready`)
                    VALUES
                        (0)"""
        self.write()
        self.sql = """DELETE FROM `cvd`.`message`
                    WHERE `processed` = 1"""
        self.write()

    def writeMessage(self):
        try:
            self.write()
            if self.cursor.rowcount == 0:
                raise
        except:
            try:
                temp = self.sql
                self.createMessage()
                self.resetMessage()
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
        try:
            self.temperature = decimal.Decimal(temperature)
            self.pressure = decimal.Decimal(pressure)
            self.argon = decimal.Decimal(argon)
            self.ethanol = decimal.Decimal(ethanol)
        except:
            self.temperature = 0.00
            self.pressure = 0.00
            self.argon = 0.00
            self.ethanol = 0.00
        self.sql = """UPDATE `cvd`.`runtime_arduino`
                SET	`temperature`	= %s,
                        `pressure`	= %s,
                        `ethanol`	= %s,
                        `argon`		= %s
                LIMIT 1;"""  % (self.temperature, self.pressure, self.ethanol, self.argon)
        self.writeArduino()

    def setLogFile(self, fileName):
        self.sql = """UPDATE `cvd`.`recording`
                    SET	`filename` = '%s'
                    WHERE `recording` = 1
                    LIMIT 1;""" % (fileName)
        self.write()
        self.fileName = fileName

    def isRecording(self):
        self.sql = """SELECT `recording`
                    FROM `cvd`.`runtime_recording`
                    LIMIT 1;"""
        try:
            self.read()
        except:
            return False
        if not len(self.data) == 1:
            return False
        else:
            if self.data[0]:
                return True
            else:
                return False

    def stopRecording(self):
        self.sql = """UPDATE `cvd`.`runtime_recording`
                SET	`recording` = 0;"""
        self.writeRecording()
        self.sql = """UPDATE `cvd`.`recording`
                SET	`recording` = 0
                WHERE `recording` = 1;"""
        self.writeRecording()
        self.recordingID = -1

    def startRecording(self, filename = ''):
        self.stopRecording

        self.sql = """INSERT INTO `cvd`.`recording` (
                `id` ,`time` , `recording` , `filename` )
                VALUES (
                NULL , CURRENT_TIMESTAMP , 1, '%s')""" % filename
        self.writeRecording()
        self.sql = """SELECT `id`
        FROM `cvd`.`recording`
                WHERE `recording` = 1
                LIMIT 1;"""
        self.read()
        self.sql = """UPDATE `cvd`.`runtime_recording`
                SET `id_recording` = %i,
                    `recording` = 1
                LIMIT 1;""" % self.data
        self.writeRecording()

    def getRecordingID(self):
        self.sql = """SELECT `id_recording`
                    FROM `cvd`.`runtime_recording`
                    LIMIT 1;"""
        self.read()
        if (len(self.data) == 1):
            return int(self.data[0])
        else:
            return -1

    def getLogFile(self):
        if not self.isRecording():
            return ""
        # get id from memory table
        recordingID = self.getRecordingID()
        # update filename from disc table if not already saved in class
        if not (recordingID == self.recordingID) or len(self.fileName) == 0:
            self.sql = """SELECT `filename`
                    FROM `cvd`.`recording`
                    WHERE `id` = %i;""" % recordingID
            self.read()
            if len(self.data) == 1:
                self.fileName = self.data[0]
            else:
                self.fileName = ''
            self.recordingID = recordingID
        return self.fileName

    def setMessage(self, message):
        self.sql = """INSERT INTO `cvd`.`message`
                (`text`) VALUES ('%s');"""  % (message)
        self.writeMessage()
        self.updateMessage()

    def updateMessage(self):
        self.sql = """SELECT `id` FROM `cvd`.`message`
                WHERE `processed` = 0
                LIMIT 1;"""
        self.read()
        if (len(self.data) == 1):
            id_message = self.data[0]
            ready = 1
        else:
            ready = 0
            id_message = -1

        self.sql = """UPDATE `cvd`.`runtime_message`
                SET `ready` = %i,
                    `id_message` = %i
                LIMIT 1;""" % (ready, id_message)
        self.writeMessage()

    def isReady(self):
        if self.ready:
            return True
        self.sql = """SELECT `ready`, `id_message`
                FROM `cvd`.`runtime_message`;"""
        try:
            self.read()
        except:
            return False
        if not len(self.data) == 2:
                self.data = (0,-1)
        (self.ready, self.messageID) = self.data
        if self.ready:
            return True
        else:
            return False

    def getMessage(self):
        self.message = ""
        if self.isReady():
            # get message
            self.sql = """SELECT `text`
                FROM `cvd`.`message`
                WHERE `id` = %i
                LIMIT 1;""" % self.messageID
            self.read()
            if (len(self.data) == 1):
                self.message = self.data[0]
            # mark as processed
            self.sql = """UPDATE `cvd`.`message`
                SET `processed` = 1
                WHERE `id` = %i;""" % self.messageID
            self.writeMessage()
            # search for pending messages
            self.updateMessage()
        # reset readout
        self.ready = False
        return self.message

    def setFlowbus(self, instrument, process, flowBus, dataTypeString, dataInput, timeInput, parameterName):
        time = decimal.Decimal(timeInput)
        parameterName = parameterName.encode("hex")
        if (dataTypeString == "character"):
            dataType = 0
            data = format(int(dataInput), 'x')
        elif(dataTypeString == "integer"):
            dataType = 1
            data = format(int(dataInput), 'x')
        elif(dataTypeString == "long"):
            dataType = 2
            data = format(int(dataInput), 'x')
        elif(dataTypeString == "string"):
            dataType = 3
            data = dataInput.encode("hex")
        else:
            raise ValueError("can not identify dataType at setFlowBus")

        self.sql = """
        INSERT INTO `cvd`.`runtime_flowbus`
        (`instrument`,`process`,`flowBus`,`dataType`,`data`,`time`, `parameter`)
        VALUES
        (%i, %i, %i, %i, UNHEX(LPAD('%s',%i,'0')), %.2f, UNHEX(LPAD('%s',%i,'0')))""" % (instrument, process, flowBus, dataType, data, self.storage_values * 2, time, parameterName, self.storage_description * 2)
        self.sql += """
        ON DUPLICATE KEY UPDATE
        `data` = UNHEX(LPAD('%s',%i,'0')),
        `time` = %.2f;""" % (data, self.storage_values * 2, time)
        self.writeFlowbus()

    def getFlowbus(self, instrument, process, flowBus):
        self.sql = """
        SELECT `dataType`,TRIM(LEADING '0' FROM HEX(`data`)),`time`,TRIM(LEADING '0' FROM HEX(`parameter`))
        FROM `cvd`.`runtime_flowbus`
        WHERE
        (   `instrument`    = %i
        AND `process`       = %i
        AND `flowBus`       = %i);
        """ % (instrument, process, flowBus)
        self.read()
        if (len(self.data) == 4):
            (dataType, dataOut, timeOut, parameter) = self.data
        else:
            raise

        parameter = parameter.decode("hex")
        time = decimal.Decimal(timeOut)
        if (dataType == 0):
            data = int(dataOut, 16)
        elif(dataType == 1):
            data = int(dataOut, 16)
        elif(dataType == 2):
            data = FBconvertLong(process, flowBus, int(dataOut,16))
        elif(dataType == 3):
            data = dataOut.decode("hex")
        else:
            data = 0
            raise

        return (parameter, data, time)

    def getAll(self):
        self.open()
        sql = """SELECT temperature, pressure, ethanol, argon,
                             spTemperature, spPressure, spEthanol, spArgon
                      FROM `cvd`.`runtime_arduino`
                      LIMIT 1"""
        try:
            self.sql = sql
            self.read()
        except:
            try:
                self.createArduino()
                self.resetArduino()
                self.sql = sql
                self.read()
            except:
                raise
        (self.temperature, self.pressure, self.ethanol, self.argon, self.spTemperature, self.spPressure, self.spEthanol, self.spArgon) = self.data
        self.close()


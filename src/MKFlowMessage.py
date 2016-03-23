#!/usr/bin/env python
from datetime import datetime       # datetime supports milliseconds. time doesn't
import sys                          # used to get line number of error print sys.exc_traceback.tb_lineno
import struct                       # used to convert bin-->float

class MKFlowMessage():
    def __init__(self, message1, message2):
        self.message1 = message1
        self.message2 = message2
        self.clear()
        self.resetSubType()
        self.analyse()

    def reprocess(self, message1, message2):
        self.message1 = message1
        self.message2 = message2
        self.resetSubType()
        self.analyse()

    def resetSubType(self):
        # message type identifier
        self.commandByte= -3
        self.isInvalid  = False # -2
        self.isError    = False # -1
        self.isStatus   = False #  0
        self.isSent     = False #  2
        self.isSentStatus = False # 1
        self.isRequest  = False #  4
        # clear message objects
        self.Invalid    = MKFlowInvalid()
        self.Error      = MKFlowError()
        self.Status     = MKFlowStatus()
        self.Sent       = MKFlowSent()
        #self.SentStatus = MKFlowSentStatus()
        self.Request    = MKFlowRequest()

    def getSubType(self):
        if self.isInvalid:
            return self.Invalid
        if self.isError:
            return self.Error
        if self.isStatus:
            return self.Status
        if self.isSent or self.isSentStatus:
            return self.Sent
        if self.isRequest:
            return self.Request

    def clear(self):
        self.data = []
        self.node       = -1
        self.sequence   = -1
        self.length     = -1
        self.manualLength = False
        self.dataLength = -1
        self.commandByte= -1
        self.commandByteHuman = ''
        self.commandByteHumanShort = ''
        self.direction      = ''
        self.time           = datetime
        self.time_human     = "%Y/%m/%d;%H:%M:%S.%f"
        self.time_second    = 0.00

    def getNode(self):
        return self.node

    def getSequence(self):
        return self.sequence

    def getLength(self):
        return self.length

    def setLength(self, length):
        self.length = length
        self.manualLength = True

    def getDirection(self):
        return self.direction

    def getTime(self):
        return self.time_human

    def getSeconds(self):
        return self.time_second

    def getCommandByte(self):
        return self.commandByte

    def getCommandByteShort(self):
        return self.commandByteHumanShort

    def trim(self):
        self.message1 = self.message1.replace('\n','')
        self.message2 = self.message2.replace('\n','')
        while self.message2[0:1] == " ":
            self.message2 = self.message2[1:]

    def split(self):
        # split message
        self.message1 = self.message1.split(" ")
        self.message2 = self.message2.split(" ")

    def analyseDirection(self):
        if self.message1[0] == '>':
            self.direction = 'right'
        elif self.message1[0] == '<':
            self.direction = 'left'
        else:
            self.direction = 'none'
            self.Invalid.add('MKFlowMessage:analyseDirection socat error direction not recognized')
            raise

    def analyseTime(self):
        self.time = datetime.strptime(self.message1[1] + ';' + self.message1[2], "%Y/%m/%d;%H:%M:%S.%f")
        self.time_human = self.time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self.time_second = self.time.hour*60*60 + self.time.minute * 60 + self.time.second + self.time.microsecond/1e6

    def analyseLength(self):
        if not self.manualLength:
            self.length = int(self.message1[4].split("=")[1])

    def parseMessage(self):
        try:
            self.trim()
            self.split()
        except:
            self.Invalid.add('MKFlowMessage:parseMessage:\tError while parsing')
            raise

    def parseData(self):
        #replace two DLE (escaped) sequences (10 10) by one databyte (10)
        try:
            start = 0
            foundOne = False
            while len(self.data) > start:
                found = self.data[start:].index(16)
                if self.data[(found+start+1)] == 16:
                    self.data.pop(found+start)
                    start = start + found
                    foundOne = True
                else:
                    start +=1
        except ValueError:
            # 10 not found. Ignore
            pass
        except:
            # other errors --> report
            raise

    def checkMessage2(self):
        # all this has to be checked before the error is raised.
        if not (len(self.message2)==self.length):
            self.Invalid.add('MKFlowMessage:parseMessage2:\tError in socat output: length of message-data array does not macht socat length')
        # dataLength is length-Byte
        if not (self.dataLength==len(self.data)-3) and not (self.dataLength == 0):
            self.Invalid.add('MKFlowMessage:parseMessage2:\tError in socat output: length-Byte in message does not match socat length')
        if (len(self.message2)<6):
            self.Invalid.add('MKFlowMessage:parseMessage2:\tMessage shorter than 6 bytes: DLE STX SEQUENCE NODE ... DLE ETX')
            # DLE STX SEQUENCE NODE LEN DATA DLE ETX
        if not ((self.message2[0] == "10") and (self.message2[1] == "02")):
            self.Invalid.add('MKFlowMessage:parseMessage2:\tno valid message beginning:\tDLE (0x10) STX (0x02) missing')
        if not ((self.message2[(self.length-2)] == "10") and (self.message2[(self.length-1)] == "03")):
            self.Invalid.add('MKFlowMessage:parseMessage2:\tno valid message ending:\tDLE (0x10) ETX (0x03) missing')
        if self.Invalid.isActive():
            raise ValueError('MKFlowMessage:parseMessage2:\tError while processing Message2')

    def analyse(self):
        try:
            self.parseMessage()
            self.analyseMessage()
            self.analyseMessageType()
            self.analyseCommandByte()
            if self.Invalid.isActive():
                raise ValueError('MKFlowMessage:analyse:\tMessage invalid')

        except Exception as e:
            self.Invalid.add('MKFlowMessage:analyse:\t'+str(e))
            self.Invalid.add('MKFlowMessage:analyse:\tLine number:\t' + str(sys.exc_traceback.tb_lineno))
            self.Invalid.add('MKFlowMessage:analyse:\tcommandByte:\t' + str(self.commandByte))
            self.commandByte = -2
            self.isInvalid = True
            #raise

    def analyseMessage(self):
        # DLE STX SEQUENCE NODE LEN DATA DLE ETX
        try:
            self.analyseMessage1()
            self.analyseMessage2()
        except:
            self.Invalid.add('MKFlowMessage:analyseMessage:\tError while extracting data.')
            raise

    def analyseMessage1(self):
        try:
            self.analyseDirection()
            self.analyseTime()
            self.analyseLength()
        except:
            self.Invalid.add('MKFlowMessage:analyseMessage1:\tError while processing message1')
            raise

    def analyseMessage2(self):
        # DLE STX SEQUENCE NODE LEN DATA DLE ETX
        try:
            self.data = [int(i,16) for i in self.message2[2:-2]]
            self.parseData()
            self.sequence   = self.data[0]
            self.node       = self.data[1]
            self.dataLength = self.data[2]
            self.checkMessage2()
        except:
            self.Invalid.add('MKFlowMessage:analyseMessage2:\tError while extracting data.')
            if len(self.data)<3:
                self.Invalid.add('MKFlowMessage:analyseMessage2:\tlen(data)='+str(len(self.data)))
            raise

    def analyseMessageType(self):
        # check if the message contains information
        try:
            # length 0 means.Error.Status in message. next byte after 00 contains.Error code.
            if self.data[2] == 0:
                self.commandByte = -1
            else:
                self.commandByte = self.data[3]
        except:
            self.Invalid.add('MKFlowMessage:analyseMessageType Error while retrieving Message')
            raise

    def analyseCommandByte(self):
        try:
            self.translateCommandByte()
            if self.commandByte == -2:
                self.isInvalid = True
            elif self.commandByte == -1:
                self.isError = True
                self.Error.set(self.data[3:])
                self.Error.setSequence(self.sequence)
                self.Error.setNode(self.node)
                self.Error.analyse()
            elif self.commandByte == 0:
                self.Status.set(self.data[4:])
                self.Status.analyse()
                self.isStatus = True
            elif self.commandByte == 4:
                self.Request.set(self.data[4:])
                self.isRequest = True
            elif (self.commandByte == 2):
                self.Sent.set(self.data[4:])
                self.isSent = True
            elif (self.commandByte == 1):
                self.Sent.set(self.data[4:])
                self.isSentStatus = True
            else:
                myError = 'MKFlowMessage:analyseCommandByte commandByte ' + str(self.commandbyte) + ' not handled'
                self.Invalid.add(myError)
                self.Invalid.add(self.commandByteHuman)
                raise ValueError(myError)
        except:
            raise

    def translateCommandByte(self):
        try:
            if self.commandByte == -2:
                self.commandByteHuman = "Invalid Message: Error in Program"
            elif self.commandByte == -1:
                self.commandByteHuman = "Valid Message: Error Message from Device"
            elif self.commandByte == 0:
                self.commandByteHuman = "Status message"
            elif self.commandByte == 1:
                self.commandByteHuman = "Send Parameter with destination address, will be answered with type 00 command"
            elif self.commandByte == 2:
                self.commandByteHuman = "Send Parameter with destination address, no.Status.Requested"
            elif self.commandByte == 3:
                self.commandByteHuman = "Send Parameter with source address, no.Status.Requested"
            elif self.commandByte == 4:
                self.commandByteHuman = "Request Parameter, will be answered with type 02 or 00 command"
            elif self.commandByte == 6:
                self.commandByteHuman = "Stop Process"
            elif self.commandByte == 7:
                self.commandByteHuman = "Start Process"
            elif self.commandByte == 8:
                self.commandByteHuman = "Claim Process"
            elif self.commandByte == 9:
                self.commandByteHuman = "Unclaim Process"
            else:
                self.commandByteHuman = "unhandled commandByte: " + str(self.commandByte)
                raise ValueError(self.commandByteHuman)
            if self.commandByte == 4:
                self.commandByteHumanShort = 'REQ'
            elif (self.commandByte >= 1) and (self.commandByte <= 3):
                self.commandByteHumanShort = 'ST' + str(self.commandByte)
            if self.commandByte == -2:
                self.commandByteHumanShort = 'INV'
            if self.commandByte == -1:
                self.commandByteHumanShort = 'ERR'
            if self.commandByte == 0:
                self.commandByteHumanShort = 'INF'
        except:
            raise

    def stdout(self):
        print '-- message Class Output begin --'
        print self.message1
        print self.message2
        print 'direction: \t' , self.getDirection()
        print 'length: \t'    , self.getLength()
        print 'time: \t'      , self.getTime()
        print 'seconds: \t'   , self.getSeconds()
        print 'sequence: \t'  , self.getSequence()
        print 'node: \t'      , self.getNode()
        print 'command: \t'   , self.getCommandByte()
        print '-- message end --'

    def stdoutShort(self, indent=''):
        return '\t'.join(str(i) for i in [indent, self.getNode(), self.getSequence(), self.getCommandByteShort()])

# Message Type Classes
class MKFlowInvalid():
    def __init__(self):
        self.value = ''
        self.active = False

    def add(self, newValue):
        self.active = True
        self.value += str(newValue) + '\n'

    def get(self):
        if self.active:
            return self.value
        else:
            return

    def isActive(self):
        return self.active

    def stdout(self, leading = '\t'):
        print leading, "-- MKFlowRequest Class Output Begin --"
        print leading, "Value:\t", self.value
        print leading, "-- MKFlowRequest Class Output End --"

    def stdoutShort(self, indent=''):
        return '\t'.join(str(i) for i in [indent, self.isActive()])

class MKFlowError():
    def __init__(self):
        self.value = 0
        self.node = -1
        self.sequence = -1
        self.text = ''
        self.active = False

    def set(self, data):
        self.active = True
        self.data = data
        self.value = data[0]

    def setNode(self, node):
        self.node = node

    def setSequence(self,sequence):
        self.sequence = sequence

    def analyse(self):
        if not len(self.data) == 1:
            raise ValueError('Error Class has received too many input bytes')
        self.translate()

    def getText(self):
        return self.text

    def getHuman(self):
        return self.getText()

    def getValue(self):
        return self.value

    def getData(self):
        return self.data

    def translate(self):
        if self.active:
            self.text = 'device returned error code ' + str(self.value) + ': '
            if (self.value==3):
                self.text += 'propar protocol error'
            elif (self.value==4):
                self.text += 'propar protocol error (or CRC error)'
            elif (self.value==5):
                if self.node >= 0:
                    self.text += 'destination node address ' + str(self.node) + ' rejected'
                else:
                    self.text += 'destination node address rejected'
                if self.sequence >= 0:
                    self.text += ' for sequence ' + str(self.sequence)
            elif (self.value==9):
                self.text += 'response message timeout'

    def stdout(self, indent = '\t'):
        print indent, '-- Error Class Output Begin--'
        print indent, 'Error Data:\t', self.getData()
        print indent, 'Error Number:\t', self.getValue()
        print indent, 'Error Message:\t', self.getText()
        print indent, '-- Error Class Output Begin--'

    def stdoutShort(self, indent=''):
        return '\t'.join(str(i) for i in [indent, self.getValue(),None,None,self.getHuman()])

class MKFlowStatus():
    def __init__(self):
        self.data = []
        self.status         = -1
        self.status_human   = ''
        self.index          = -1
        self.active = False

    def set(self, data):
        self.data   = data
        self.active = True

    def analyse(self):
        if len(self.data)>0:
            self.status = self.data[0]
            self.status_hex = hex(self.data[0])[2:]
        if len(self.data)>1:
            self.index  = self.data[1]
        self.humanize()

    def isActive(self):
        return self.active

    def getStatus(self):
        return self.status

    def getStatusByte(self):
        return self.status

    def getIndex(self):
        return self.index

    def getHuman(self):
        if self.status_human == '':
            self.humanize()
        return self.status_human

    def humanize(self):
        # dict([('no Status', -1), ('no Error', 0), ...])
        if self.status == -1:
            self.status_human = 'no Status'
        elif self.status_hex == '0':
            self.status_human = 'no Error'
        elif self.status_hex == '1':
            self.status_human = 'Process claimed'
        elif self.status_hex == '2':
            self.status_human = 'Command Error'
        elif self.status_hex == '3':
            self.status_human = 'Process Error'
        elif self.status_hex == '4':
            self.status_human = 'Parameter Error'
        elif self.status_hex == '5':
            self.status_human = 'Parameter type Error'
        elif self.status_hex == '6':
            self.status_human = 'Parameter value Error'
        elif self.status_hex == '7':
            self.status_human = 'Network not active'
        elif self.status_hex == '8':
            self.status_human = 'Time-out start character'
        elif self.status_hex == '9':
            self.status_human = 'Time-out serial line'
        elif self.status_hex == 'a':
            self.status_human = 'Hardware memory Error'
        elif self.status_hex == 'b':
            self.status_human = 'Node number Error'
        elif self.status_hex == 'c':
            self.status_human = 'General communication Error'
        elif self.status_hex == 'd':
            self.status_human = 'Read only Parameter.'
        elif self.status_hex == 'e':
            self.status_human = 'Error PC-communication'
        elif self.status_hex == 'f':
            self.status_human = 'No RS232 connection'
        elif self.status_hex == '10':
            self.status_human = 'PC out of memory'
        elif self.status_hex == '11':
            self.status_human = 'Write only Parameter'
        elif self.status_hex == '12':
            self.status_human = 'System configuration unknown'
        elif self.status_hex == '13':
            self.status_human = 'No free node address'
        elif self.status_hex == '14':
            self.status_human = 'Wrong interface type'
        elif self.status_hex == '15':
            self.status_human = 'Error serial port connection'
        elif self.status_hex == '16':
            self.status_human = 'Error opening communication'
        elif self.status_hex == '17':
            self.status_human = 'Communication Error'
        elif self.status_hex == '18':
            self.status_human = 'Error interface bus master'
        elif self.status_hex == '19':
            self.status_human = 'Timeout answer'
        elif self.status_hex == '1a':
            self.status_human = 'No start character'
        elif self.status_hex == '1b':
            self.status_human = 'Error first digit'
        elif self.status_hex == '1c':
            self.status_human = 'Buffer overflow in host'
        elif self.status_hex == '1d':
            self.status_human = 'Buffer overflow'
        elif self.status_hex == '1e':
            self.status_human = 'No answer found'
        elif self.status_hex == '1f':
            self.status_human = 'Error closing communication'
        elif self.status_hex == '20':
            self.status_human = 'Synchronisation Error'
        elif self.status_hex == '21':
            self.status_human = 'Send Error'
        elif self.status_hex == '22':
            self.status_human = 'Protocol Error'
        elif self.status_hex == '23':
            self.status_human = 'Buffer overflow in module'

    def stdout(self, indent = '\t'):
        print indent, "MKFlowStatus Class Output Begin"
        print indent, "Data Array:\t", self.data
        print indent, "Status :   \t", self.getStatus()
        print indent, "Status :   \t", self.getHuman()
        print indent, "Index Byte:\t", self.getIndex()
        print indent, "MKFlowStatus Class Output End"

    def stdoutShort(self,indent=''):
        print indent, 'INFO\t', self.getStatus(), '\t\t', self.getHuman()

# subclass for MKFlowProcess
class MKFlowParameter():
    def __init__(self):
        self.dataType   = 'undefined'

        self.index      = -1
        self.process    = -1
        self.number     = -1

        self.dataLength = 0
        self.dataStart = 0

        self.data       = []
        self.human      = ''

    def set(self, data):
        self.data = data

    def setLength(self,length=0):
        self.length = length

    def setProcess(self, process):
        self.process = process

    def analyse(self):
        pass

    def analyseData(self):
        self.index = self.data[0]
        self.number= self.data[0]

    def analyseDataType(self, number = -3):
        if number == -3:
            number = self.number
        identifier = format(number, '08b')[1:3]
        if identifier == '00':
            self.dataType = 'character'
        elif identifier == '01':
            self.dataType = 'integer'
        elif identifier == '10':
            self.dataType = 'long'
        elif identifier == '11':
            self.dataType = 'string'

    def substractDataType(self, number = -3):
        if number == -3:
            number = self.number
        if self.dataType == 'string':
            number -= int('60',16)
        elif self.dataType == 'long':
            number -= int('40',16)
        elif self.dataType == 'integer':
            number -= int('20',16)
        elif self.dataType == 'character':
            pass
        return number

    def isChained(self):
        if self.index >= 128:
            return True
        else:
            return False

    def getData(self):
        return self.data[0:self.length]

    def getIndex(self):
        index = self.index
        if self.isChained():
            index -= 128
        if index >= 32:
            index = self.substractDataType(index)
        return index

    def getProcess(self):
        return self.process

    def getNumber(self):
        return self.number

    def getDataType(self):
        return self.dataType

    def getLength(self):
        return self.length

    def getHuman(self):
        if self.human == '':
            self.humanize()
        return self.human

    def humanize(self):
        getIdent = dict([('0:0', 0), ('0:1', 1), ('0:2', 2), ('0:3', 3), ('0:4', 4), ('0:5', 5), ('0:10', 6), ('1:0', 7), ('1:1', 8), ('1:2', 9), ('1:3', 10), ('1:4', 11), ('1:5', 12), ('1:6', 13), ('1:7', 14), ('1:8', 15), ('1:9', 16), ('1:10', 17), ('1:11', 18), ('1:12', 19), ('1:13', 20), ('1:14', 21), ('1:15', 22), ('1:16', 23), ('1:17', 24), ('1:18', 25), ('1:19', 26), ('1:20', 27), ('0:12', 28), ('0:13', 29), ('0:14', 30), ('9:1', 31), ('10:0', 32), ('10:1', 33), ('10:2', 34), ('114:12', 51), ('115:3', 52), ('116:6', 53), ('114:1', 54), ('117:1', 55), ('117:2', 56), ('115:1', 57), ('116:7', 58), ('115:2', 59), ('114:2', 60), ('114:3', 61), ('116:1', 62), ('116:2', 63), ('116:3', 64), ('116:4', 65), ('114:4', 66), ('116:5', 67), ('115:4', 68), ('115:5', 69), ('115:6', 70), ('114:5', 71), ('117:3', 72), ('117:4', 73), ('115:7', 78), ('114:6', 79), ('0:19', 80), ('114:7', 81), ('114:8', 82), ('114:9', 83), ('114:10', 84), ('114:11', 85), ('114:13', 86), ('114:14', 87), ('114:15', 88), ('113:1', 89), ('113:2', 90), ('113:3', 91), ('113:4', 92), ('118:1', 93), ('118:2', 94), ('118:3', 95), ('118:4', 96), ('118:5', 97), ('118:6', 98), ('118:7', 99), ('118:8', 100), ('118:9', 101), ('118:10', 102), ('114:16', 103), ('113:5', 104), ('115:9', 105), ('116:8', 106), ('115:8', 113), ('113:6', 114), ('97:1', 115), ('97:2', 116), ('97:3', 117), ('97:4', 118), ('97:5', 119), ('97:6', 120), ('104:1', 121), ('104:2', 122), ('104:3', 123), ('104:4', 124), ('104:5', 125), ('104:6', 126), ('104:7', 127), ('1:31', 128), ('104:8', 129), ('113:7', 130), ('33:1', 138), ('33:2', 139), ('114:17', 140), ('33:7', 141), ('33:8', 142), ('33:9', 143), ('33:10', 144), ('115:10', 146), ('33:9', 148), ('33:10', 149), ('33:5', 150), ('33:6', 151), ('33:11', 152), ('33:13', 153), ('97:9', 155), ('104:9', 156), ('33:14', 157), ('33:15', 158), ('33:16', 159), ('33:17', 160), ('33:18', 161), ('33:20', 162), ('115:11', 163), ('114:18', 164), ('114:20', 165), ('114:21', 166), ('114:22', 167), ('114:23', 168), ('33:21', 169), ('113:8', 170), ('113:9', 171), ('113:10', 172), ('113:11', 173), ('113:12', 174), ('118:11', 175), ('115:12', 176), ('113:13', 177), ('113:14', 178), ('113:15', 179), ('113:16', 180), ('97:7', 181), ('33:22', 182), ('0:18', 183), ('0:20', 184), ('123:1', 185), ('123:3', 186), ('123:4', 187), ('123:10', 188), ('114:24', 189), ('115:13', 190), ('115:14', 191), ('116:9', 192), ('115:15', 193), ('115:16', 194), ('115:17', 195), ('115:18', 196), ('33:4', 197), ('125:10', 198), ('125:3', 199), ('125:9', 200), ('125:20', 201), ('115:22', 202), ('125:21', 203), ('33:0', 204), ('33:3', 205), ('33:23', 206), ('119:1', 207), ('119:2', 208), ('119:3', 209), ('119:4', 210), ('119:5', 211), ('119:6', 212), ('116:21', 213), ('116:22', 214), ('116:23', 215), ('116:24', 216), ('116:25', 217), ('116:26', 218), ('116:27', 219), ('116:28', 220), ('117:5', 221), ('33:24', 222), ('117:6', 223), ('33:25', 224), ('33:26', 225), ('33:27', 226), ('33:28', 227), ('33:29', 228), ('33:30', 229), ('114:25', 230), ('114:26', 231), ('114:27', 232), ('114:28', 233), ('114:29', 234), ('0:21', 235), ('115:20', 236), ('33:31', 237), ('33:12', 238), ('33:13', 239), ('33:16', 240), ('33:17', 241), ('33:10', 244), ('33:11', 245), ('113:17', 248), ('113:18', 249), ('113:20', 250), ('113:21', 251), ('113:22', 252), ('114:30', 253), ('113:23', 254), ('113:24', 255), ('113:25', 256), ('113:26', 257), ('113:27', 258), ('113:28', 259), ('113:29', 260), ('113:30', 261), ('113:31', 262), ('116:10', 263), ('116:11', 264), ('116:12', 265), ('116:13', 266), ('116:14', 267), ('65:15', 268), ('116:15', 269), ('116:18', 270), ('116:8', 271), ('116:9', 272), ('104:10', 273), ('104:11', 274), ('65:1', 275), ('116:17', 276), ('116:29', 277), ('116:30', 278), ('116:30', 279), ('116:31', 280), ('121:0', 281), ('121:1', 282), ('121:2', 283), ('121:3', 284), ('121:4', 285), ('121:5', 286), ('114:31', 287), ('65:21', 288), ('65:22', 289), ('65:23', 290), ('65:24', 291), ('65:25', 292), ('116:20', 293), ('115:31', 294), ('104:12', 295), ('104:13', 296), ('104:14', 297), ('125:8', 298), ('125:11', 299), ('124:7', 300), ('124:8', 301), ('124:10', 302), ('124:9', 303), ('124:11', 304), ('124:20', 305), ('124:21', 306), ('120:0', 307), ('120:2', 308), ('120:6', 309), ('120:7', 310), ('120:3', 311), ('120:1', 312), ('120:4', 313), ('120:5', 314), ('120:8', 315), ('120:9', 316), ('120:10', 317), ('120:11', 318), ('0:6', 319), ('0:7', 320), ('124:31', 321), ('115:23', 322), ('118:12', 323), ('65:26', 324), ('116:16', 325), ('119:31', 326), ('115:24', 327), ('125:12', 328), ('124:12', 329), ('0:8', 330)])
        getWord = dict([(0, 'Identification string'), (1, 'Primary node address'), (2, 'Secondary node address'), (3, 'Next node address'), (4, 'Last node address'), (5, 'Arbitrage'), (6, 'Initreset'), (7, 'Measure'), (8, 'Setpoint'), (9, 'Setpoint slope'), (10, 'Analog input'), (11, 'Control mode'), (12, 'Polynomial constant A'), (13, 'Polynomial constant B'), (14, 'Polynomial constant C'), (15, 'Polynomial constant D'), (16, 'Polynomial constant E'), (17, 'Polynomial constant F'), (18, 'Polynomial constant G'), (19, 'Polynomial constant H'), (20, 'Capacity'), (21, 'Sensor type'), (22, 'Capacity unit index'), (23, 'Fluid number'), (24, 'Fluid name'), (25, 'Claim node'), (26, 'Modify'), (27, 'Alarm info'), (28, 'Channel amount'), (29, 'First channel'), (30, 'Last channel'), (31, '<hostcontrl>'), (32, 'Alarm message unit type'), (33, 'Alarm message number'), (34, 'Relay status'), (51, 'Cycle time'), (52, 'Analog mode'), (53, 'Reference voltage'), (54, 'Valve output'), (55, 'Dynamic display factor'), (56, 'Static display factor'), (57, 'Calibration mode'), (58, 'Valve offset'), (59, 'Monitor mode'), (60, 'Alarm register1'), (61, 'Alarm register2'), (62, '<CalRegZS1>'), (63, '<CalRegFS1>'), (64, '<CalRegZS2>'), (65, '<CalRegFS2>'), (66, 'ADC control register'), (67, 'Bridge potmeter'), (68, '<AlarmEnble>'), (69, 'Test mode'), (70, '<ADC channel select>'), (71, 'Normal step controller response'), (72, 'Setpoint exponential smoothing filter'), (73, 'Sensor exponential smoothing filter'), (78, 'Tuning mode'), (79, 'Valve default'), (80, 'Global modify'), (81, 'Valve span correction factor'), (82, 'Valve curve correction'), (83, '<MemShipNor>'), (84, '<MemShipOpn>'), (85, 'IO status'), (86, '<FuzzStNeNo>'), (87, '<FuzzStPoNo>'), (88, '<FuzzStOpen>'), (89, 'Device type'), (90, 'BHTModel number'), (91, 'Serial number'), (92, 'Customer model'), (93, 'BHT1'), (94, 'BHT2'), (95, 'BHT3'), (96, 'BHT4'), (97, 'BHT5'), (98, 'BHT6'), (99, 'BHT7'), (100, 'BHT8'), (101, 'BHT9'), (102, 'BHT10'), (103, 'Broadcast repeating time'), (104, 'Firmware version'), (105, 'Pressure sensor type'), (106, 'Barometer pressure'), (113, 'Reset'), (114, 'User tag'), (115, 'Alarm limit maximum'), (116, 'Alarm limit minimum'), (117, 'Alarm mode'), (118, 'Alarm output mode'), (119, 'Alarm setpoint mode'), (120, 'Alarm new setpoint'), (121, 'Counter value'), (122, 'Counter unit index'), (123, 'Counter limit'), (124, 'Counter output mode'), (125, 'Counter setpoint mode'), (126, 'Counter new setpoint'), (127, 'Counter unit'), (128, 'Capacity unit'), (129, 'Counter mode'), (130, 'Minimum hardware revision'), (138, 'Slave factor'), (139, 'Reference voltage input'), (140, 'Stable situation controller response'), (141, 'Temperature'), (142, 'Pressure'), (143, 'Time'), (144, 'Calibrated volume'), (146, 'Range select'), (148, 'Frequency'), (149, 'Impulses/m3'), (150, 'Normal volume flow'), (151, 'Volume flow'), (152, 'Delta-p'), (153, '<scalefact>'), (155, 'Reset alarm enable'), (156, 'Reset counter enable'), (157, 'Master node'), (158, 'Master process'), (159, 'Remote instrument node'), (160, 'Remote instrument process'), (161, 'Minimum custom range'), (162, 'Maximum custom range'), (163, 'Relay/TTL output'), (164, 'Open from zero controller response'), (165, 'Controller features'), (166, 'PID-Kp'), (167, 'PID-Ti'), (168, 'PID-Td'), (169, 'Density'), (170, 'Calibration certificate'), (171, 'Calibration date'), (172, 'Service number'), (173, 'Service date'), (174, 'Identification number'), (175, 'BHT11'), (176, 'Power mode'), (177, 'Pressure inlet'), (178, 'Pressure outlet'), (179, 'Orifice'), (180, 'Fluid temperature'), (181, 'Alarm delay'), (182, 'Capacity 0%'), (183, 'Number of channels'), (184, 'Device function'), (185, 'Scan channel'), (186, 'Scan parameter'), (187, 'Scan time'), (188, 'Scan data'), (189, 'Valve open'), (190, 'Number of runs'), (191, 'Minimum process time'), (192, 'Leak rate'), (193, 'Mode info request'), (194, 'Mode info option list'), (195, 'Mode info option description'), (196, 'Calibrations options'), (197, 'Mass flow'), (198, 'Bus address'), (199, 'Interface configuration'), (200, 'Baudrate'), (201, 'Bus diagnostic string'), (202, 'Number of vanes'), (203, 'Fieldbus'), (204, 'fMeasure'), (205, 'fSetpoint'), (206, 'Mass'), (207, 'Manufacturer status register'), (208, 'Manufacturer warning register'), (209, 'Manufacturer error register'), (210, 'Diagnostic history string'), (211, 'Diagnostic mode'), (212, 'Manufacturer status enable'), (213, 'Analog output zero adjust'), (214, 'Analog output span adjust'), (215, 'Analog input zero adjust'), (216, 'Analog input span adjust'), (217, 'Sensor input zero adjust'), (218, 'Sensor input span adjust'), (219, 'Temperature input zero adjust'), (220, 'Temperature input span adjust'), (221, 'Adaptive smoothing factor'), (222, 'Slope setpoint step'), (223, 'Filter length'), (224, 'Absolute accuracy'), (225, 'Lookup table index'), (226, 'Lookup table X'), (227, 'Lookup table Y'), (228, 'Lookup table temperature index'), (229, 'Lookup table temperature'), (230, 'Valve maximum'), (231, 'Valve mode'), (232, 'Valve open correction'), (233, 'Valve zero hold'), (234, 'Valve slope'), (235, 'IFI data'), (236, 'Range used'), (237, 'Fluidset properties'), (238, 'Lookup table unit type index'), (239, 'Lookup table unit type'), (240, 'Lookup table unit index'), (241, 'Lookup table unit'), (244, 'Capacity unit type temperature'), (245, 'Capacity unit pressure'), (248, 'Formula type'), (249, 'Heat capacity'), (250, 'Thermal conductivity'), (251, 'Viscosity'), (252, 'Standard flow'), (253, 'Controller speed'), (254, 'Sensor code'), (255, 'Sensor configuration code'), (256, 'Restriction code'), (257, 'Restriction configurator code'), (258, 'Restriction NxP'), (259, 'Seals information'), (260, 'Valve code'), (261, 'Valve configuration code'), (262, 'Instrument properties'), (263, 'Lookup table frequency index'), (264, 'Lookup table frequency frequency'), (265, 'Lookup table frequency temperature'), (266, 'Lookup table frequency density'), (267, 'Lookup table frequency span adjust'), (268, 'Capacity unit index (ext)'), (269, 'Density actual'), (270, 'Measured restriction'), (271, 'Temperature potmeter'), (272, 'Temperature potmeter gain'), (273, 'Counter controller overrun correction'), (274, 'Counter controller gain'), (275, 'Sub fluid number'), (276, 'Temperature compensation factor'), (277, 'DSP register address'), (278, 'DSP register long'), (279, 'DSP register floating point'), (280, 'DSP register integer'), (281, 'Standard deviation'), (282, 'Measurement status'), (283, 'Measurement stop criteria'), (284, 'Measurement time out'), (285, 'Maximum number of runs'), (286, 'Minimum standard deviation'), (287, 'IO switch status'), (288, 'Sensor bridge settings'), (289, 'Sensor bridge current'), (290, 'Sensor resistance'), (291, 'Sensor bridge voltage'), (292, 'Sensor group name'), (293, 'Sensor calibration temperature'), (294, 'Valve safe state'), (295, 'Counter unit type index'), (296, 'Counter unit type'), (297, 'Counter unit index (ext)'), (298, 'Bus1 selection'), (299, 'Bus1 medium'), (300, 'Bus2 mode'), (301, 'Bus2 selection'), (302, 'Bus2 address'), (303, 'Bus2 baudrate'), (304, 'Bus2 medium'), (305, 'Bus2 diagnostics'), (306, 'Bus2 name'), (307, 'PIO channel selection'), (308, 'PIO parameter'), (309, 'PIO input/output filter'), (310, 'PIO parameter capacity 0%'), (311, 'PIO parameter capacity 100%'), (312, 'PIO configuration selection'), (313, 'PIO analog zero adjust'), (314, 'PIO analog span adjust'), (315, 'PIO hardware capacity max'), (316, 'PIO capacity set selection'), (317, 'PIO hardware capacity 0%'), (318, 'PIO hardware capacity 100%'), (319, 'Hardware platform id'), (320, 'Hardware platform sub id'), (321, 'Temporary baudrate'), (322, 'Setpoint monitor mode'), (323, 'BHT12'), (324, 'Nominal sensor voltage'), (325, 'Sensor voltage compensation factor'), (326, 'PCB serial number'), (327, 'Minimum measure time'), (328, 'Bus1 parity'), (329, 'Bus2 parity'), (330, 'Firmware id')])
        myIdent = str(self.getProcess()) + ":" + str(self.getNumber())
       
        if myIdent in getIdent.keys():
            if getIdent[myIdent] in getWord.keys():
                self.human = getWord[getIdent[myIdent]]
                
# subclass for MKFlowData
class MKFlowProcess():
    class MKFlowParameter(MKFlowParameter):
        pass
        
    def __init__(self):
        self.number = -1
        self.length = 0
        self.data = []
        self.Parameter = []
        
    def set(self, data):
        self.data   = data
        self.number = data[0]
        
    def analyse(self):
        index = 0
        position = 1
        chained = True
        while chained:
            index = len(self.Parameter)
            self.Parameter.append(self.MKFlowParameter())
            self.Parameter[index].set(self.data[position:])
            self.Parameter[index].setProcess(self.getProcess())
            self.Parameter[index].analyse()
            position += self.Parameter[index].getLength()
            chained = self.Parameter[index].isChained()
        self.length = position

    def isChained(self):
        if self.number >= 128:
            return True
        else:
            return False

    def getNumber(self):
        return self.number

    def getProcess(self):
        if self.isChained():
            return (self.number - 128)
        else:
            return self.number

    def getLength(self):
        return self.length
        
    def stdout(self, leading = '\t\t'):
        print leading, "-- MKFlowProcess Class Output Begin --"
        print leading, 'Data:\t', self.data
        print leading, 'Data:\t', self.data[0:self.getLength()]
        print leading, '1st byte:\t', format(self.data[0], '08b')[0:4] + ' ' + format(self.data[0], '08b')[4:8]
        print leading, 'chained:\t', self.isChained()
        print leading, 'Process:\t', self.getProcess()
        print leading, 'Total Parameters: ', len(self.Parameter)
        for parameter in self.Parameter:
            parameter.stdout(leading + '\t')
        print leading, "-- MKFlowProcess Class Output End --"

class MKFlowData():
    class MKFlowProcess(MKFlowProcess):
        pass

    def __init__(self):
        self.data = []
        self.active = False
        self.process = []
        self.length = 0

    def set(self,data):
        self.active = True
        self.data = data
        self.analyse()

    def analyse(self):
        self.analyseProcess()
        if not self.check():
            raise ValueError('Data was not fully processed. Some information might be missing. Declare whole as invalid')
            pass

    def check(self):
        return (len(self.data) == self.length)

    def analyseProcess(self):
        index = 0
        position = 0
        chained = True
        while chained:
            index = len(self.process)
            self.process.append(self.MKFlowProcess())
            self.process[index].set(self.data[position:])
            self.process[index].analyse()
            position += self.process[index].getLength()
            chained = self.process[index].isChained()
        self.length = position

    def stdout(self, leading = '\t'):
        print leading, "-- MKFlowData Class Output Begin --"
        print leading, "Data Array: \t", self.data
        print leading, "Data Array: \t", self.data[0:self.length]
        print leading, 'Total Processes:\t', len(self.process)
        print leading, 'Data' + (" not " if not self.check() else " ") +'fully processed'
        for process in self.process:
            process.stdout('\t\t')
        print leading, "-- MKFlowData Class Output End --"

class MKFlowRequest(MKFlowData):
    def stdoutShort(self, indent=''):
        for process in self.process:
            for parameter in process.Parameter:
                return '\t'.join(str(i) for i in [indent , parameter.getProcess(), parameter.getIndex(), parameter.getNumber(), parameter.getHuman()])

    class MKFlowProcess(MKFlowProcess):
        class MKFlowParameter(MKFlowParameter):
            def analyse(self):
                self.analyseData()
                self.analyseDataType(self.number)
                self.setLength(3)

            def analyseData(self):
                try:
                    if len(self.data)<3:
                        raise ValueError('MKFlowRequest:analyseData data array too short')
                    self.index   = self.data[0]
                    self.process = self.data[1] # process should be filled by parent
                    self.number  = self.data[2]
                except:
                    raise

            def setLength(self,length=0):
                self.length = length
                if self.dataType == 'string':
                    self.length += 1
                    self.DataLength = self.data[3]

            def getNumber(self):
                # FB Number ( no chaining parameter present)
                return self.substractDataType(self.number)

            def stdout(self, leading = '\t\t\t'):
                print leading, "-- MKFlowRequest Class Output Begin --"
                print leading, 'Data:    \t', self.getData()
                print leading, '1st byte:\t', format(self.data[0], '08b')[0:4] + ' ' + format(self.data[0], '08b')[4:8]
                print leading, 'Chained: \t', self.isChained()
                print leading, 'Index:   \t', self.getIndex()
                print leading, '2nd byte:\t', format(self.data[1], '08b')[0:4] + ' ' + format(self.data[1], '08b')[4:8]
                print leading, 'Process: \t', self.getProcess()
                print leading, '3rd byte:\t', format(self.data[2], '08b')[0:4] + ' ' + format(self.data[2], '08b')[4:8]
                print leading, 'DataType:\t', self.getDataType()
                print leading, 'FbNr:    \t', self.getNumber()
                print leading, 'Length:  \t', self.getLength()
                print leading, 'Human Ind:\t', self.getHuman()
                print leading, "-- MKFlowRequest Class Output End --"

class MKFlowSent(MKFlowData):
    def stdoutShort(self, indent=''):
        for process in self.process:
            for parameter in process.Parameter:
                return '\t'.join(str(i) for i in [indent, process.getProcess(), parameter.getIndex(), None, parameter.getValue()])

    class MKFlowProcess(MKFlowProcess):
        class MKFlowParameter(MKFlowParameter):
            def analyse(self):
                self.analyseData()
                self.analyseDataType()
                self.analyseValue()

            def analyseValue(self):
                self.dataStart = 1
                self.dataValueFloat = float(0)
                if self.dataType == 'string':
                    self.dataLength = self.data[self.dataStart]
                    self.dataStart += 1
                    self.setLength()
                    self.dataValue  = ''.join(chr(i) for i in self.data[self.dataStart:self.length])
                elif self.dataType == 'long':
                    # can also be IEE floating point notation
                    self.dataLength = 4
                    self.setLength()
                    (self.dataValueFloat,) = struct.unpack('<f',''.join(chr(i) for i in self.data[self.dataStart:self.length]))
                    self.dataValue  = int(''.join(hex(i)[2:] for i in self.data[self.dataStart:self.length]),16)
                elif self.dataType == 'integer':
                    self.dataLength = 2
                    self.setLength()
                    self.dataValue  = int(''.join(hex(i)[2:] for i in self.data[self.dataStart:self.length]),16)
                elif self.dataType == 'character':
                    self.dataLength = 1
                    self.setLength()
                    self.dataValue = self.data[self.dataStart]
                else:
                    self.dataLength = 0
                    self.setLength()
                    self.dataValue = None
                    raise ValueError('MKFlowSent:analyseValue datatype not found: ' + str(self.dataType))
                if (len(self.data)) < self.length:
                    pass
                    #raise ValueError('length of data does not match message size.')
                elif (len(self.data)) > self.length:
                    pass
                    #raise ValueError('length of data too long. Check for chaining!')

            def setLength(self):
                if self.dataLength == 0:
                    # undefined length. use whole
                    self.length = len(self.data)
                else:
                    self.length = self.dataLength + self.dataStart

            def getValue(self):
                return self.dataValue

            def getValueFloat(self):
                return self.dataValueFloat

            def stdout(self, leading = '\t\t\t'):
                print leading, "-- MKFlowSent:MKFlowProcess:MKFlowParameter Class Output Begin --"
                print leading, 'Data:    \t', self.getData()
                print leading, '1st byte:\t', format(self.data[0], '08b')[0:4] + ' ' + format(self.data[0], '08b')[4:8]
                print leading, 'Chained: \t', self.isChained()
                print leading, 'DataType:\t', self.getDataType()
                print leading, 'Index:    \t', self.getIndex()
                print leading, '2nd byte:\t', format(self.data[1], '08b')[0:4] + ' ' + format(self.data[1], '08b')[4:8]
                print leading, 'Length:  \t', self.getLength()
                print leading, 'Value:   \t', self.getValue()
                if self.dataType == 'long':
                    print leading, 'Float:   \t', self.getValueFloat()
                print leading, "-- MKFlowSent:MKFlowProcess:MKFlowParameter Class Output End --"

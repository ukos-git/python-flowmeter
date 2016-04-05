#!/usr/bin/env python

import MKDatabase
# Main Class
class MKFlowCommunication():
    def __init__(self):
        self.nullNode = MKFlowNode(-1)
        self.node_numbers = []
        self.nodes = []

    def addNode(self, number):
        if not self.isNode(number):
            self.node_numbers += [number]
            node = MKFlowNode(number)
            self.nodes += [node]

    def isNode(self, number):
        return (number in self.node_numbers)

    def getNode(self, number):
        if self.isNode(number):
            id = self.node_numbers.index(number)
            node = self.nodes[id]
            return node
        else:
            return self.nullNode

    def Node(self, number):
        if not self.isNode(number):
            self.addNode(number)
        return self.getNode(number)

class MKFlowNode():
    def __init__(self, node):
        self.node = node
        self.nullSequence = MKFlowSequence(-1)
        self.sequence_numbers = []
        self.sequences = []

    def getNumber(self):
        return self.node

    def addSequence(self, number):
        if not self.isSequence(number):
            self.sequence_numbers += [number]
            sequence = MKFlowSequence(number)
            self.sequences += [sequence]

    def isSequence(self, number):
        return (number in self.sequence_numbers)

    def getSequence(self, number):
        if self.isSequence(number):
            id = self.sequence_numbers.index(number)
            sequence = self.sequences[id]
            return sequence
        else:
            return self.nullSequence

    def Sequence(self, number):
        if not self.isSequence(number):
            self.addSequence(number)
        return self.getSequence(number)

class MKFlowSequence():
    def __init__(self, sequence):
        self.sequence = sequence
        self.nullChild = MKFlowModbus(-1, -1)
        self.reset()

    def reset(self):
        self.parameter_ids = []
        self.parameters = []

        self.hasAnswer = False
        self.hasRequest = False
        self.RequestHasValue = False
        self.isAnalysed = False
        self.isStatus = False
        self.isError = False
        self.isValid = False

    def setReadRequest(self, Message):
        self.Request = Message.getSubType()
        self.hasRequest = True
        self.hasAnswer = False
        self.RequestHasValue = False

    def setWriteRequest(self, Message):
        self.setReadRequest(Message)
        self.RequestHasValue = True

    def setStatus(self, Message):
        self.setAnswer(Message)
        self.isStatus = True

    def setError(self, Message):
        self.setAnswer(Message)
        self.isError = True

    def setAnswer(self, Message):
        self.Answer = Message.getSubType()
        self.time = Message.getSeconds()
        self.hasAnswer = True
        self.isStatus = False
        self.isError = False

    def check(self):
        if self.hasAnswer and self.hasRequest:
            return True
        else:
            return False

    def addParameter(self, process, index):
        if not self.isParameter(process, index):
            self.parameter_ids += [self.createID(process, index)]
            Parameter = MKFlowModbus(process, index)
            self.parameters += [Parameter]

    def isParameter(self, process, index):
        return (self.createID(process, index) in self.parameter_ids)

    def createID(self, process, index):
        return ":".join(str(i) for i in [process, index])

    def getParameter(self, process, index):
        if self.isParameter(process, index):
            id = self.parameter_ids.index(self.createID(process, index))
            Parameter = self.parameters[id]
            return Parameter
        else:
            return self.nullChild

    def Parameter(self, process, index):
        if not self.isParameter(process, index):
            self.addParameter(process, index)
        return self.getParameter(process, index)

    def analyse(self):
        if self.check():
            # Process Request
            for process in self.Request.process:
                for parameter in process.Parameter:
                    self.Parameter(process.getProcess(), parameter.getIndex()).setNumber(parameter.getNumber())
                    self.Parameter(process.getProcess(), parameter.getIndex()).setName(parameter.getHuman())
                    self.Parameter(process.getProcess(), parameter.getIndex()).setLength(parameter.getLength())
                    if self.RequestHasValue:
                        self.Parameter(process.getProcess(), parameter.getIndex()).setValue(parameter.getValue())
                        self.Parameter(process.getProcess(), parameter.getIndex()).setDataType(parameter.getDataType())

            # Process Answer
            if not self.RequestHasValue and not self.isStatus and not self.isError:
                for process in self.Answer.process:
                    for parameter in process.Parameter:
                        self.Parameter(process.getProcess(), parameter.getIndex()).setValue(parameter.getValue())
                        self.Parameter(process.getProcess(), parameter.getIndex()).setDataType(parameter.getDataType())

            # Answer with Status or Error and set valid
            self.valid = True
            self.analyseStatus()
            self.analyseError()
            self.isAnalysed = True

    def analyseStatus(self):
        if self.isStatus:
            if self.Answer.getStatus() == 0:
                # no error
                self.valid = True
            elif self.Answer.getStatus() > 3 and self.Answer.getStatus() < 8:
                # Parameter Error
                where = self.Answer.getIndex()
                count = 4
                for parameter_id in self.parameter_ids:
                    [process, index] = [int(i) for i in parameter_id.split(":")]
                    Parameter = self.getParameter(process, index)
                    if not self.RequestHasValue:
                        Parameter.setInvalid()
                    if where == count:
                        self.error = "Status: %s\t Parameter: %s" % (self.Answer.getHuman(), Parameter.getName())
                        Parameter.setError(self.Answer.getHuman())
                    count += int(Parameter.getLength())
            else:
                self.error = self.Answer.getHuman()
                self.valid = False

    def analyseError(self):
        if self.isError:
            self.error = self.Answer.getText()
            self.valid = False
        if not self.valid:
            for parameter_id in self.parameter_ids:
                [process, index] = [int(i) for i in parameter_id.split(":")]
                Parameter = self.getParameter(process, index)
                Parameter.setError(self.error)

    def output(self):
        if self.check():
            if not self.isAnalysed:
                self.analyse()
            for parameter_id in self.parameter_ids:
                [process, index] = [int(i) for i in parameter_id.split(":")]
                Parameter = self.getParameter(process, index)
                try:
                    Parameter.stdout()
                except:
                    self.stdout()
                    raise ValueError("error in MKFlowModbusClass output")

    def readOut(self):
        if self.check():
            if not self.isAnalysed:
                self.analyse()
            for parameter_id in self.parameter_ids:
                [process, index] = [int(i) for i in parameter_id.split(":")]
                Parameter = self.getParameter(process, index)
                try:
                    if not Parameter.isInvalid():
                        valid = True
                        proc = process
                        fbnr = Parameter.getNumber()
                        name = Parameter.getName()
                        value = Parameter.getValue()
                        dataType = Parameter.getDataType()
                        time = self.time
                        self.reset()
                        return (valid, proc, fbnr, value, dataType, time)
                except:
                    self.stdout()
                    raise ValueError("error storing parameter")
            self.reset()
        raise ValueError("Nothing to do")

    def stdout(self):
        print "--- sequence: %i ---" % self.sequence
        print "---- parameters: %s ----" % self.parameter_ids
        if self.hasRequest:
            print "---- request ----"
            self.Request.stdout()
        if self.hasAnswer:
            print "---- answer ----"
            self.Answer.stdout()


class MKFlowModbus():
    def __init__(self, process, index):
        self.process = process
        self.index = index
        self.invalid = False
        self.error = ''
        self.value = None
        self.human = ''
        self.dataType = '' # readybility. store as string
        self.length = 0

    def setNumber(self, number):
        self.number = number

    def getNumber(self):
        return self.number

    def setValue(self, value):
        self.value = value

    def getValue(self):
        return self.value

    def setDataType(self, dataType):
        self.dataType = dataType

    def getDataType(self):
        return self.dataType

    def setName(self, string):
        self.human = string

    def getName(self):
        return self.human

    def setInvalid(self):
        self.invalid = True

    def setLength(self, length):
        self.length = length

    def getLength(self):
        return self.length

    def setError(self, error):
        self.error = error
        self.setInvalid()

    def isInvalid(self):
        if self.invalid:
            return True
        else:
            return False

    def stdout(self):
        returnarray = [self.invalid, self.process, self.number, self.human]
        if not self.invalid:
            returnarray += [self.value]
        else:
            returnarray += [self.error]
        print '\t'.join(str(i) for i in returnarray)


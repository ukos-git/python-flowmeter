# python-flowmeter
Store data from Bronkhorst FlowMeters in a MySQL database. With this connection it is also possible to access the FlowBus data over the network by other devices.
Stand-alone version for [python-swnt-reactor](https://github.com/ukos-git/python-swnt-reactor)

# how it works
The communication between FlowMeter and Bright Display Adapter is bridged through socat which directly echoes from the incoming to the outcoming port. The socat output is recorded by this program. All messages are then sorted and sored in memory. If amatching  question/answer pair from the FlowBus protocol is found, the Data is analyzed and then stored in a local MySQL database. The tables of the MySQL DataBase are temporary tables that are stored in RAM due to the high write-throughput.

# setup
currently our Bronkhorst FlowMeters are connected in a special way:
* Voltage for the FlowMeters are constantly connectexd.
* An output for the Analog signal (set/read) is directed to an arduino
* the digital signal output is directed to the PC and then back again to a Bronkhorst Bright Display Adapter.
* data on the PC is bridged using a USB to 4xRS232 converter: All Data incoming from the FlowMeter is analysed by the PC

The analog read-out was the start of the project.
The Bronkhorst Bright Adapters will be unnecessary as soon as this program can talk independently to the FlowBus. Right Now it only listens passively and does nothing if there is no communication.

# ToDo
* Some functionality like Database access, Hostname, path, tty Ports, Flow-Gas names etc are hard-coded to the source code.
* There is no client application yet for displaying the readout in a nice way. You can reaed the database using any appropriate application like phpmyadmin.
* Start active communication without Bright Display Adapter.
* The bridge stops working at some point. Reason is not clear.

# Get Started
Without the proper FlowMeters installed, you can input one of the log file from ./input/log[1,2]. To do this look at the commented line in `MKFlowMain.py-->MKFlow()-->init():`
```python
self.Input.setBridge(port1, port2)
#self.Input.setLogFile('/home/matthias/Documents/programs/python/swnt-reactor/data/log/bridge/testing/log1.log')
```
uncomment the setLogFile and comment the setBridge to input the contents of the log file.

# sample flowbus analysis

The following communication is taken from the communication of the Bronkhorst FlowMeter. It consists of a request and a send operation, captured by passing the communication through the tty(s) of a pc running this python app. The [complete analysis](https://github.com/ukos-git/python-flowmeter/blob/master/documents/Bronkhorst_FlowBus_translated.txt) is saved located in a document.

The basic message captured by socat is this:

```
['>', '2015/06/08', '13:38:21.012908', '', 'length=24', 'from=0', 'to=23']
['10', '02', '01', '80', '11', '04', '01', '80', '00', '01', '81', '00', '02', '82', '00', '03', '83', '00', '04', '04', '00', '05', '10', '03']

['<', '2015/06/08', '13:38:21.028538', '', 'length=19', 'from=0', 'to=18']
['10', '02', '01', '80', '0c', '02', '01', '80', '03', '81', '7f', '82', '04', '83', '20', '04', '43', '10', '03']
```

It gets translated by the program to the following:

```
1	 --- request ---
-- message Class Output begin --
['>', '2015/06/08', '13:38:21.012908', '', 'length=24', 'from=0', 'to=23']
['10', '02', '01', '80', '11', '04', '01', '80', '00', '01', '81', '00', '02', '82', '00', '03', '83', '00', '04', '04', '00', '05', '10', '03']
direction:  right
length:  24
time:  2015-06-08 13:38:21.012
seconds:  49101.012908
sequence:  1
node:  128
command:  4
-- message end --
	-- MKFlowData Class Output Begin --
	Data Array: 	[1, 128, 0, 1, 129, 0, 2, 130, 0, 3, 131, 0, 4, 4, 0, 5]
	Data Array: 	[1, 128, 0, 1, 129, 0, 2, 130, 0, 3, 131, 0, 4, 4, 0, 5]
	Total Processes:	1
	Data fully processed
		-- MKFlowProcess Class Output Begin --
		Data:	[1, 128, 0, 1, 129, 0, 2, 130, 0, 3, 131, 0, 4, 4, 0, 5]
		Data:	[1, 128, 0, 1, 129, 0, 2, 130, 0, 3, 131, 0, 4, 4, 0, 5]
		1st byte:	0000 0001
		chained:	False
		Process:	1
		Total Parameters:  5
			-- MKFlowRequest Class Output Begin --
			Data:    	[128, 0, 1]
			1st byte:	1000 0000
			Chained: 	True
			Index:   	0
			2nd byte:	0000 0000
			Process: 	0
			3rd byte:	0000 0001
			DataType:	character
			FbNr:    	1
			Length:  	3
			Human Ind:	Primary node address
			-- MKFlowRequest Class Output End --
			-- MKFlowRequest Class Output Begin --
			Data:    	[129, 0, 2]
			1st byte:	1000 0001
			Chained: 	True
			Index:   	1
			2nd byte:	0000 0000
			Process: 	0
			3rd byte:	0000 0010
			DataType:	character
			FbNr:    	2
			Length:  	3
			Human Ind:	Secondary node address
			-- MKFlowRequest Class Output End --
			-- MKFlowRequest Class Output Begin --
			Data:    	[130, 0, 3]
			1st byte:	1000 0010
			Chained: 	True
			Index:   	2
			2nd byte:	0000 0000
			Process: 	0
			3rd byte:	0000 0011
			DataType:	character
			FbNr:    	3
			Length:  	3
			Human Ind:	Next node address
			-- MKFlowRequest Class Output End --
			-- MKFlowRequest Class Output Begin --
			Data:    	[131, 0, 4]
			1st byte:	1000 0011
			Chained: 	True
			Index:   	3
			2nd byte:	0000 0000
			Process: 	0
			3rd byte:	0000 0100
			DataType:	character
			FbNr:    	4
			Length:  	3
			Human Ind:	Last node address
			-- MKFlowRequest Class Output End --
			-- MKFlowRequest Class Output Begin --
			Data:    	[4, 0, 5]
			1st byte:	0000 0100
			Chained: 	False
			Index:   	4
			2nd byte:	0000 0000
			Process: 	0
			3rd byte:	0000 0101
			DataType:	character
			FbNr:    	5
			Length:  	3
			Human Ind:	Arbitrage
			-- MKFlowRequest Class Output End --
		-- MKFlowProcess Class Output End --
	-- MKFlowData Class Output End --
1	128	1	REQ	0	0	1	Primary node address
2	 --- send ---
-- message Class Output begin --
['<', '2015/06/08', '13:38:21.028538', '', 'length=19', 'from=0', 'to=18']
['10', '02', '01', '80', '0c', '02', '01', '80', '03', '81', '7f', '82', '04', '83', '20', '04', '43', '10', '03']
direction:  left
length:  19
time:  2015-06-08 13:38:21.028
seconds:  49101.028538
sequence:  1
node:  128
command:  2
-- message end --
	-- MKFlowData Class Output Begin --
	Data Array: 	[1, 128, 3, 129, 127, 130, 4, 131, 32, 4, 67]
	Data Array: 	[1, 128, 3, 129, 127, 130, 4, 131, 32, 4, 67]
	Total Processes:	1
	Data fully processed
		-- MKFlowProcess Class Output Begin --
		Data:	[1, 128, 3, 129, 127, 130, 4, 131, 32, 4, 67]
		Data:	[1, 128, 3, 129, 127, 130, 4, 131, 32, 4, 67]
		1st byte:	0000 0001
		chained:	False
		Process:	1
		Total Parameters:  5
			-- MKFlowSent:MKFlowProcess:MKFlowParameter Class Output Begin --
			Data:    	[128, 3]
			1st byte:	1000 0000
			Chained: 	True
			DataType:	character
			Index:    	0
			2nd byte:	0000 0011
			Length:  	2
			Value:   	3
			Human Ind:	
			-- MKFlowSent:MKFlowProcess:MKFlowParameter Class Output End --
			-- MKFlowSent:MKFlowProcess:MKFlowParameter Class Output Begin --
			Data:    	[129, 127]
			1st byte:	1000 0001
			Chained: 	True
			DataType:	character
			Index:    	1
			2nd byte:	0111 1111
			Length:  	2
			Value:   	127
			Human Ind:	
			-- MKFlowSent:MKFlowProcess:MKFlowParameter Class Output End --
			-- MKFlowSent:MKFlowProcess:MKFlowParameter Class Output Begin --
			Data:    	[130, 4]
			1st byte:	1000 0010
			Chained: 	True
			DataType:	character
			Index:    	2
			2nd byte:	0000 0100
			Length:  	2
			Value:   	4
			Human Ind:	
			-- MKFlowSent:MKFlowProcess:MKFlowParameter Class Output End --
			-- MKFlowSent:MKFlowProcess:MKFlowParameter Class Output Begin --
			Data:    	[131, 32]
			1st byte:	1000 0011
			Chained: 	True
			DataType:	character
			Index:    	3
			2nd byte:	0010 0000
			Length:  	2
			Value:   	32
			Human Ind:	
			-- MKFlowSent:MKFlowProcess:MKFlowParameter Class Output End --
			-- MKFlowSent:MKFlowProcess:MKFlowParameter Class Output Begin --
			Data:    	[4, 67]
			1st byte:	0000 0100
			Chained: 	False
			DataType:	character
			Index:    	4
			2nd byte:	0100 0011
			Length:  	2
			Value:   	67
			Human Ind:	Control mode
			-- MKFlowSent:MKFlowProcess:MKFlowParameter Class Output End --
		-- MKFlowProcess Class Output End --
-- MKFlowData Class Output End --
```

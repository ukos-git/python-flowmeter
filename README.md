# python-flowmeter
WIP:application not ready for public release. History rewrites possible on every branch.

# description
Store data from Bronkhorst FlowMeters in a MySQL database. With this connection it is possible to access the FlowBus data over the network by other devices.
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

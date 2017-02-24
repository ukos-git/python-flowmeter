#!/bin/bash
if [ "$(hostname)" == "raspberrypi" ]
then
    python /home/pi/programs/python-flowmeter/src/serverFlowmeter.py
fi
if [ "$(hostname)" == "lab117" ]
then
    python /home/lab/programs/python-flowmeter/src/serverFlowmeter.py
fi
if [ "$(hostname)" == "uk-work" ]
then
    python /home/matthias/Documents/programs/python/python-flowmeter/src/serverFlowmeter.py
fi
python ./src/serverFlowmeter.py

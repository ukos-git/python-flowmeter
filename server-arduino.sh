#!/bin/bash
if [ "$(hostname)" == "raspberrypi" ]
then
    python /home/pi/programs/swnt-reactor/src/serverArduino.py
fi
if [ "$(hostname)" == "lab117" ]
then
    python /home/lab/programs/swnt-reactor/src/serverArduino.py
fi
if [ "$(hostname)" == "uk-work" ]
then
    python /home/matthias/Documents/programs/python/swnt-reactor/src/serverArduino.py
fi


#!/bin/bash
if [ "$(hostname)" == "raspberrypi" ]
then
    pypy /home/pi/programs/swnt-reactor/src/serverArduino.py
fi
if [ "$(hostname)" == "lab117" ]
then
    pypy /home/lab/programs/swnt-reactor/src/serverArduino.py
fi
if [ "$(hostname)" == "uk-work" ]
then
    pypy /home/matthias/Documents/programs/python/swnt-reactor/src/serverArduino.py
fi


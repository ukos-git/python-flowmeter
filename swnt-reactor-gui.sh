#!/bin/bash
if [ "$(hostname)" == "raspberrypi" ]
then
    python /home/pi/programs/swnt-reactor/src/MKTkinker.py
else
    python /home/matthias/Documents/programs/python/swnt-reactor/src/MKTkinker.py
fi

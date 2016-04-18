#!/bin/bash
if [ "$(hostname)" == "raspberrypi" ]
then
    python /home/pi/programs/swnt-reactor/src/MKMain.py
else
    python /home/matthias/Documents/programs/python/swnt-reactor/src/MKtkinker.py
fi

#!/bin/bash
NOW=$(date +"%Y-%m-%d")
# socat -x /dev/ttyUSB1,raw,echo=0,b38400 /dev/ttyUSB0,raw,echo=0,b38400 2>>"log_bridgeAr_$NOW"& tail -f "log_bridgeAr_$NOW"
socat /dev/ttyUSB1,raw,echo=0,b38400 /dev/ttyUSB0,raw,echo=0,b38400

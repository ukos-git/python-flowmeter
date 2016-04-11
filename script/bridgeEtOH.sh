#!/bin/bash
NOW=$(date +"%Y-%m-%d")
socat -x /dev/ttyUSB2,raw,echo=0,b38400 /dev/ttyUSB3,raw,echo=0,b38400 2>>"log_bridgeEtOH_$NOW"& tail -f "log_bridgeEtOH_$NOW"

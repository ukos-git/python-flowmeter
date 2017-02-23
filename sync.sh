#!/bin/bash

rsync -AaXv ./src/*.py pi@132.187.77.177:/home/pi/programs/swnt-reactor/src
rsync -AaXv ./src/*.py pi@132.187.77.184:/home/pi/programs/swnt-reactor/src
rsync -AaXv ./src/*.py pi@132.187.77.181:/home/pi/programs/swnt-reactor/src

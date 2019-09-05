#!/bin/bash

# Ensure that we have enough command line arguments
if [ "$#" -lt 1 ]
then
	echo "Not enough arguments"
	exit 1
fi

# Get the current directory. The status file should be in the same
# directory by convention
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
statusFile="${DIR}/status"

# Start/stop the file and update the status accordingly
if [ $1 == "start" ]
then
	sudo service tinyproxy start
	echo 1 > $statusFile
elif [ $1 == "stop" ]
then
	sudo service tinyproxy stop
	echo 0 > $statusFile
else
	echo "Not a valid parameter"
fi

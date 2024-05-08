#!/usr/bin/env bash

BASEDIR=$(dirname "$0")

source $BASEDIR/tmbotenv/bin/activate
echo "Starting bot in '$BASEDIR'"
python3 $BASEDIR/client.py


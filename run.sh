#!/usr/bin/env bash

BASEDIR=$(dirname "$0")

echo "Starting bot in '$BASEDIR'"

source $BASEDIR/tmbotenv/bin/activate

python $BASEDIR/client.py


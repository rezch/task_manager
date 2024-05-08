#!/usr/bin/env bash

# to add bot token to env:
# add 'export TOKEN="<token>"' to ~/.bashrc


BASEDIR=$(dirname "$0")

source $BASEDIR/tmbotenv/bin/activate
echo "Starting bot in '$BASEDIR'"
python3 $BASEDIR/client.py


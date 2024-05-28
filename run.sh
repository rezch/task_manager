#!/usr/bin/env bash

# to add bot token to env:
# add 'export TOKEN="<token>"' to ~/.bashrc


BASEDIR=$(dirname "$0")

source tmbotenv/bin/activate
echo "Starting bot"
python3 client.py


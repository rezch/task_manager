#!/usr/bin/env bash

BASEDIR=$(dirname "$0")

echo "Starting installing env in '$BASEDIR'"

python3 -m venv $BASEDIR/tmbotenv
source $BASEDIR/tmbotenv/bin/activate

pip3 install telebot
pip3 install g4f

#!/usr/bin/env bash

BASEDIR=$(dirname "$0")

echo "Starting installing env in '$BASEDIR'"
python3 -m venv $BASEDIR/tmbotenv
source $BASEDIR/tmbotenv/bin/activate

echo "Updating pip3 in env"
sudo -H pip3 install --upgrade pip

echo "pip3 install libs in env"
pip3 install telebot
pip3 install g4f
pip3 install SpeechRecognition

echo "apt update in system"
sudo apt-get update

echo "ffmpeg install in system"
sudo apt-get remove --purge ffmpeg
sudo apt-add-repository ppa:mc3man/trusty-media
sudo apt-add-repository ppa:jonathonf/ffmpeg-3
sudo apt-get install ffmpeg

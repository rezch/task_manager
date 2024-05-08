#!/usr/bin/env bash

BASEDIR=$(dirname "$0")

# install python3 if it needed
if ! type -P python3; then
    echo "installing python3"
    sudo apt install python3
fi

# install python3-venv if it needed
if ! type -P python3-venv; then
    echo "installing python3-venv"
    sudo apt install python3-venv
fi

echo "starting installing env in '$BASEDIR'"
python3 -m venv $BASEDIR/tmbotenv
source $BASEDIR/tmbotenv/bin/activate

echo "updating pip3"
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

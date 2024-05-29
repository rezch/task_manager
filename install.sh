#!/usr/bin/env bash

# install python3 if it needed
if ! type python3.10; then
    echo "installing python3.10"
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt update
    sudo apt install -y python3.10
fi

# install python3-venv if it needed
if ! type python3-venv; then
    echo "installing python3-venv"
    sudo apt install -y python3-venv
fi

echo "starting installing env"
sudo python3 -m venv tmbotenv
sudo chmod -R 0777 tmbotenv
source tmbotenv/bin/activate
echo "source env"
pip3 list

if ! type pip3; then
  echo "pip3 install in system"
  sudo apt install -y python3-pip
fi

echo "pip3 install libs in env"
if ! pip3 list | grep telebot; then
  pip3 install telebot
fi
if ! pip3 list | grep g4f; then
  pip3 install g4f
fi
if ! pip3 list | grep SpeechRecognition; then
  pip3 install SpeechRecognition
fi
if ! pip3 list | grep translatepy; then
  pip3 install translatepy
fi

# install ffmpeg if it needed
# if type ffmpeg; then
#   sudo apt-get -y remove --purge ffmpeg
# fi
if ! type ffmpeg; then
  echo "ffmpeg install in system"
  sudo apt-add-repository -y ppa:mc3man/trusty-media
  sudo apt-add-repository -y ppa:jonathonf/ffmpeg-3
  sudo apt-get -y install ffmpeg
fi


#!/usr/bin/env bash

BASEDIR=$(dirname "$0")

# install python3 if it needed
if ! type -P python3; then
    echo "installing python3"
    sudo apt install -y python3
fi

# install python3-venv if it needed
if ! type -P python3-venv; then
    echo "installing python3-venv"
    sudo apt install -y python3-venv
fi

echo "starting installing env in '$BASEDIR'"
sudo python3 -m venv "$BASEDIR"/tmbotenv
sudo source "$BASEDIR"/tmbotenv/bin/activate

if ! type -P pip3; then
  echo "pip3 install in system"
  sudo apt-get -y install ffmpeg
fi

echo "pip3 install libs in env"
if ! pip3 list | grep telebot; then
  sudo pip3 install telebot
fi
if ! pip3 list | grep g4f; then
  sudo pip3 install g4f
fi
if ! pip3 list | grep SpeechRecognition; then
  sudo pip3 install SpeechRecognition
fi
if ! pip3 list | grep translatepy; then
  sudo pip3 install translatepy
fi

# install ffmpeg if it needed
# if type -P ffmpeg; then
#   sudo apt-get -y remove --purge ffmpeg
# fi
if ! type -P ffmpeg; then
  echo "ffmpeg install in system"
  sudo apt-add-repository -y ppa:mc3man/trusty-media
  sudo apt-add-repository -y ppa:jonathonf/ffmpeg-3
  sudo apt-get -y install ffmpeg
fi


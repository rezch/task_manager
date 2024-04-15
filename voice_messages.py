import speech_recognition as sr
import os
import requests
import subprocess


def convert_voice_to_text(message, path):
    try:
        r = sr.Recognizer()
        with sr.AudioFile(path) as source:
            audio = r.record(source)
            text = r.recognize_google(audio, language="ru-RU")
        return text
    except:
        return 0 # прописать ошибку для пользователя


def get_text_voice(message):
    file_info = bot.get_file(message.voice.file_id)
    file = requests.get(
        'https://api.telegram.org/file/bot{0}/{1}'.format
        (token,
         file_info.file_path)
    )
    src = file_info.file_path[:6] + 'ogg' + file_info.file_path[5:]
    dst = file_info.file_path[:6] + 'wav' + file_info.file_path[5:-3] + 'wav'
    downloaded_file = bot.download_file(file_info.file_path)
    with open('file.ogg', 'wb') as f:
        f.write(downloaded_file)
    src_filename = 'file.ogg'
    dest_filename = f'file.wav'
    process = subprocess.run(['ffmpeg', '-i', src_filename, dest_filename])

    text = convert_voice_to_text(message, dest_filename)
    os.remove(src_filename)
    os.remove(dest_filename)
    return text

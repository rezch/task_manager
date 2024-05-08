import speech_recognition as sr


def recognise(filename):
    r = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio_text = r.listen(source)
        try:
            text = r.recognize_google(audio_text, language="ru_RU")
            print('Converting audio transcripts into text ...')
            print(text)
            return text
        except:
            return "Sorry, the text is not recognized."


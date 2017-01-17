                                               # NOTE: this requires PyAudio because it uses the Microphone class
import speech_recognition as sr

def voice_in():
    r = sr.Recognizer()
    # r = sr.Recognizer(language = "zh-CN")
    with sr.Microphone() as source:                # use the default microphone as the audio source
        audio = r.listen(source)                   # listen for the first phrase and extract it into audio data


    try:
        res = r.recognize(audio)                   # no attribute recognize
        print("You said :"+ r.recognize(audio))    # recognize speech using Google Speech Recognition
        return res
    except LookupError:                            # speech is unintelligible
        print("Could not understand audio")
        return " "

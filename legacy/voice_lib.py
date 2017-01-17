#!/usr/bin/python
#coding=utf-8 
import pyttsx
import time 
# import speech_recognition as sr
import PyBaiduYuyin as pby
# tts = pby.TTS(app_key=YOUR_APP_KEY, secret_key=YOUR_SECRET_KEY)
# tts.say("你好")

engine = pyttsx.init()
rate = engine.getProperty('rate')
voices = engine.getProperty('voices')
print voices[0].languages 
print rate
engine.setProperty('rate', rate-80)
# engine.setProperty('voice', 'Mandarin')
# engine.setProperty('voice', 'female')
engine.say_baidu('Greetings!')
engine.say_baidu('How are you today?')
engine.say_baidu('What can I do for you?')

voices = engine.getProperty('voices')

# for voice in voices:
#     engine.setProperty('voice', 'Mandarin')
#     print voice.id
#     engine.say('The quick brown fox jumped over the lazy dog.')
engine.runAndWait()
time.sleep(2)
engine.stop()
# engine.say('What can I do for you?')
# engine.say('Greetings!')
# engine.runAndWait()
# while  engine.isBusy():
#     time.sleep(2)
time.sleep(1)
# r = sr.Recognizer()

#edit by lhh
API_KEY = 'KWDnbPePMm5GfAV1Z2Et1ai1'
API_SECRET = 'd8f23d71249de2cb19a4c62f0018dba1'
r = pby.Recognizer(app_key = API_KEY, secret_key = API_SECRET)
#end

engine = pyttsx.init()
# with sr.Microphone() as source:                # use the default microphone as the audio source
#     audio = r.listen(source)                   # listen for the first phrase and extract it into audio data
#
# edit by lhh
with pby.Microphone() as source:                # use the default microphone as the audio source
    audio = r.listen(source)
#end
res =''
# engine = pyttsx.init()
try:
    res = r.recognize(audio)
    # res = r.recognize_google(audio)
    print("You said " + res)    # recognize speech using Google Speech Recognition
except LookupError:                            # speech is unintelligible
    print("Could not understand audio")

if res.find("test") >= 0:
    engine.say_baidu('Greetings!')
    engine.say_baidu('Thanks, please come again')
else:
    engine.say_baidu('I am sorry.')
    engine.say_baidu('I do not understand you.')
time.sleep(1)
engine.runAndWait()    
time.sleep(1)
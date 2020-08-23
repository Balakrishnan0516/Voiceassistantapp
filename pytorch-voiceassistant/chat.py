from __future__ import print_function
from flask import Flask
from googletest import Create_Service
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import time
import pyttsx3
import speech_recognition as sr
import pytz
import subprocess
import random
import json
import torch
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize
import webbrowser
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64



device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
MONTHS = ["january", "february", "march", "april", "may", "june","july", "august", "september","october","november", "december"]
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAY_EXTENTIONS = ["rd", "th", "st", "nd"]

chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'

def mailsend(subhere):  
    CLIENT_SECRET_FILE = 'client_secret.json'
    API_NAME = 'gmail'
    API_VERSION = 'v1'
    SCOPES = ['https://mail.google.com/']
    
    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    
    emailMsg = subhere
    mimeMessage = MIMEMultipart()
    mimeMessage['to'] = 'abc@gmail.com'
    mimeMessage['subject'] = 'You won'
    mimeMessage.attach(MIMEText(emailMsg, 'plain'))
    raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()
    message = service.users().messages().send(userId='me', body={'raw': raw_string}).execute()
    print(message)



def speak(text):
    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate', 155)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.say(text)
    engine.runAndWait()

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
            print(said)
        except Exception as e:
            print("Exception: " + str(e))

    return said.lower()

def note(text):
    date = datetime.datetime.now()
    file_name = str(date).replace(":", "-") + "-note.txt"
    with open(file_name, "w") as f:
        f.write(text)

    subprocess.Popen(["notepad.exe", file_name])



WAKE = "hey kitty"
print("Start")

while True:
    print("Listening")
    text = get_audio()

    if text.count(WAKE) > 0:
        speak("I am ready") 
        while True:
            sentence = get_audio()    
            if 'open facebook' in sentence:
                speak("opening facebook")
                webbrowser.open("http://facebook.com")
                continue;

            if 'send mail' in sentence:
                speak("opening gmail")
                webbrowser.open("mail url here")
                speak("tell me the body of the mail")
                subhere = get_audio()
                mailsend(subhere)
                speak("send succesfully")
                continue;    

            sentence = tokenize(sentence)
            X = bag_of_words(sentence, all_words)
            X = X.reshape(1, X.shape[0])
            X = torch.from_numpy(X).to(device)
            output = model(X)
            _, predicted = torch.max(output, dim=1)
            tag = tags[predicted.item()]
            probs = torch.softmax(output, dim=1)
            prob = probs[0][predicted.item()]
            if prob.item() > 0.75:
                for intent in intents['intents']:
                    if tag == intent["tag"]:
                        speak({random.choice(intent['responses'])})
                        lastext = {random.choice(intent['responses'])}
                
            else:
                speak(" I do not understand what you are saying ")

           

            NOTE_STRS = ["thanks", "thanks for visiting", "thankyou","Happy to help!", "Any time!", "My pleasure"]
            for phrase in NOTE_STRS:
                if phrase in lastext:
                    speak("Please give your valuable feedback")
                    note_text = get_audio()
                    note(note_text)
                    speak("I've made a note of that Thanks for visiting")    
            
            SONG_STRS = ["sorry i'm not good in singing ill play a song for u.","sorry i'm not feeling well,i'll play a song for u"]
            for phrase in SONG_STRS:
                if phrase in lastext:
                    speak("Here we go!")
                    webbrowser.open("https://gaana.com/song/believer-173")

            SONGNXT_STRS = ["Hey i'm not good in tamil so i gonna play you a tamil song","sorry pa unnakku orru tamil song play panrey ketu enjoy pannu"]
            for phrase in SONGNXT_STRS:
                if phrase in lastext:
                    speak("Here we go!")
                    webbrowser.open("https://gaana.com/song/chellamma-from-doctor")        
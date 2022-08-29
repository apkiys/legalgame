#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().system('cat ./requirements.txt')


# In[2]:


get_ipython().system('pip install -r requirements.txt')


# In[3]:


import sqlite3
import sqlalchemy
import pandas as pd
import numpy as np
import random
import time
import speech_recognition as sr
import pyttsx3
import sys


# In[4]:


df = pd.read_csv(r'./data/legal.csv')
df


# In[5]:


TERMS = df['lexicon']
MEANS = df['explanation']


# In[6]:


engine = pyttsx3.init()


# In[7]:


def recognize_speech_from_mic(recognizer, microphone):

    # check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    # try recognizing the speech in the recording
    # if a RequestError or UnknownValueError exception is caught,
    #     update the response object accordingly
    try:
        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response


# In[8]:


term = random.choice(TERMS)
df['lexicon'] == term
term


# In[9]:


mean = df['explanation'][df['lexicon'] == term].values[0]
mean


# In[ ]:


if __name__ == "__main__":

    TERMS = df['lexicon']
    NUM_GUESSES = 3
    PROMPT_LIMIT = 5

    # create recognizer and mic instances
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    from colorama import init
    init(strip=not sys.stdout.isatty()) # strip colors if stdout is redirected
    from termcolor import cprint 
    from pyfiglet import figlet_format

    print()
    cprint(figlet_format('Legal Game!', font='starwars'), 'yellow', 'on_red', attrs=['bold'])
    
    
    # format the instructions string
    instructions = (
        "\n"
        "I'm thinking of one legal term:\n"
        "\n"
        "{mean}\n"
        "\n"
        "You have {n} tries to guess which one.\n"
    ).format(mean=''.join(mean), n=NUM_GUESSES)

    # show instructions and wait 3 seconds before starting the game
    print(instructions)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    engine.say("Welcome to legal game!")
    engine.say("I'm thinking of one legal term,")
    engine.say(mean)
    engine.say("You have three tries to guess which one")
    engine.runAndWait()
    time.sleep(3)

    for i in range(NUM_GUESSES):
        # get the guess from the user
        # if a transcription is returned, break out of the loop and
        #     continue
        # if no transcription returned and API request failed, break
        #     loop and continue
        # if API request succeeded but no transcription was returned,
        #     re-prompt the user to say their guess again. Do this up
        #     to PROMPT_LIMIT times
        for j in range(PROMPT_LIMIT):
            print('Guess {}. Speak!'.format(i+1))
            guess = recognize_speech_from_mic(recognizer, microphone)
            if guess["transcription"]:
                break
            if not guess["success"]:
                break
            print("I didn't catch that. What did you say?\n")

        # if there was an error, stop the game
        if guess["error"]:
            print("ERROR: {}".format(guess["error"]))
            break

        # show the user the transcription
        print("You said: {}".format(guess["transcription"]))

        # determine if guess is correct and if any attempts remain
        guess_is_correct = guess["transcription"].lower() == term.lower()
        user_has_more_attempts = i < NUM_GUESSES - 1

        # determine if the user has won the game
        # if not, repeat the loop if user has more attempts
        # if no attempts left, the user loses the game
        if guess_is_correct:
            print("Congrats! You win!\n".format(term))
            engine.say("Congrats, you win!")
            engine.runAndWait()
            break
        elif user_has_more_attempts:
            print("Incorrect. Try again.\n")
        else:
            print("Sorry, you lose!\n\nThe term is '{}'.\n".format(term))
            engine.say("Sorry, you lose!")
            engine.say("The term is")
            engine.say(term)          
            engine.runAndWait()
            continue


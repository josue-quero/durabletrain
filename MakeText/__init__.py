# This function is not intended to be invoked directly. Instead it will be
# triggered by an orchestrator function.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import logging

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import json
import string
import time
import threading
import wave
try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    print("""
    Importing the Speech SDK for Python failed.
    Refer to
    https://docs.microsoft.com/azure/cognitive-services/speech-service/quickstart-python for
    installation instructions.
    """)
    import sys
    sys.exit(1)
nltk.download('stopwords')
nltk.download('punkt')
global stopWords
stopWords = set(stopwords.words("spanish"))


def summarize_line(text):
  words = word_tokenize(text)
  freqTable = dict()
  for word in words:
      word = word.lower()
      if word in stopWords:
          continue
      if word in freqTable:
          freqTable[word] += 1
      else:
          freqTable[word] = 1
  sentences = sent_tokenize(text)
  sentenceValue = dict()
  for sentence in sentences:
      for word, freq in freqTable.items():
          if word in sentence.lower():
              if sentence in sentenceValue:
                  sentenceValue[sentence] += freq
              else:
                  sentenceValue[sentence] = freq
  sumValues = 0
  for sentence in sentenceValue:
      sumValues += sentenceValue[sentence]
  average = int(sumValues / len(sentenceValue))
  summary = ''
  for sentence in sentences:
      if (sentence in sentenceValue) and (sentenceValue[sentence] > (1.1 * average)):
          summary += " " + sentence
  return summary


def make_text(wavfile):
  speech_key, service_region = "72fc3a794ec24a16804697462f59e6bf", "eastus"
  wavfile = wavfile
  speech_config = speechsdk.SpeechConfig(
      subscription=speech_key, region=service_region)
  audio_config = speechsdk.audio.AudioConfig(filename=wavfile)
  speech_recognizer = speechsdk.SpeechRecognizer(
      speech_config=speech_config, language="es-Es", audio_config=audio_config)
  done = False

  def stop_cb(evt):
    """callback that stops continuous recognition upon receiving an event `evt`"""
    print('CLOSING on {}'.format(evt))
    speech_recognizer.stop_continuous_recognition()
    nonlocal done
    done = True
    
  lines = []
  # Connect callbacks to the events fired by the speech recognizer
  speech_recognizer.recognized.connect(
      lambda evt: lines.append(evt.result.text))
  # stop continuous recognition on either session stopped or canceled events
  speech_recognizer.session_stopped.connect(stop_cb)
  speech_recognizer.canceled.connect(stop_cb)
  # Start continuous speech recognition
  speech_recognizer.start_continuous_recognition()
  while not done:
      time.sleep(.5)
  return lines




def main(file: str) -> str:
    lines = make_text(file)
    text = ""
    for line in lines:
        text += (line + " ")
    summarized = summarize_line(text)
    return summarized

import pygame
import spacy
import speech_recognition as sr
from PyQt5.QtCore import QThread, pyqtSignal
from gtts import gTTS
from spacy.matcher import Matcher

from src.models.mainModel import *


class Player(QThread):
    play_finish = pyqtSignal()

    def __init__(self, article):
        self.article = article
        self.__filename = "../res/temp/tts.mp3"
        super().__init__()

    def run(self):
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        tts = gTTS(self.article.content, lang='ro')
        tts.save(self.__filename)
        pygame.mixer.music.load(self.__filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
        pygame.mixer.music.unload()
        open(self.__filename, "w").close()
        self.play_finish.emit()

    def quit(self):
        pygame.mixer.music.stop()
        pygame.mixer.music.stop()
        super().quit()


class Recorder(QThread):
    stopped = False
    rec_stop = pyqtSignal()
    rec_finish = pyqtSignal(object)

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone(device_index=1)
        self.recording = None
        super().__init__()

    def getRecording(self):
        return self.recording

    def run(self):
        recording = None
        with self.mic as source:
            try:
                recording = self.recognizer.listen(source, timeout=30)
            except sr.WaitTimeoutError as e:
                recording = None

        if recording is not None:
            self.recording = recording
            try:
                self.recording = self.recognizer.recognize_google(self.recording, language="ro-RO")
                self.rec_finish.emit(self.recording)
            except:
                self.rec_finish.emit(None)
        else:
            self.rec_stop.emit()


class MainWindowController():

    def __init__(self, config):
        try:
            connstring = config['mongodb']['host']
            connect(connstring)
        except Exception as e:
            print(e)

        pygame.mixer.init()
        spacy.prefer_gpu()
        self.__nlp = spacy.load("ro_core_news_lg")
        self.__matcher = Matcher(self.__nlp.vocab)
        verbs = ["căuta", "cauta", "găsi", "afișa", "arăta"]
        nouns = ["lege", "articol", "speța"]
        pattern = [{"LEMMA": {"IN": verbs}},
                   {"LEMMA": {"IN": nouns}}, ]
        self.__sources = {"Codul Civil": "1", "Codul Penal": "2",
                          "Codul de Procedură Civilă": "3", "Codul de Procedură Penală": "4"}
        #TODO implement other sources
        self.__matcher.add("LawSearch", [pattern])
        self.__recognizer = sr.Recognizer()

    def processRecording(self, recording):
        doc = self.__nlp(recording)
        article = None
        matches = self.__matcher(doc)
        for match_id, start, end in matches:
            artNr = 0
            source = ""
            for ent in doc.ents:
                if ent.label_ == "NUMERIC_VALUE":
                    artNr = ent.text
                if ent.label_ == "WORK_OF_ART":
                    source = ent.text
            if artNr != 0 and source != "":
                artId = self.__sources[source] + artNr
                try:
                    article = self.getArticle(artId)
                except DoesNotExist as e:
                    print(e)
        return article

    def getArticle(self, artId):
        art = Article.objects.get(artId=artId)
        return art

    def transcribe(self, audio):
        return self.__recognizer.recognize_google(audio)


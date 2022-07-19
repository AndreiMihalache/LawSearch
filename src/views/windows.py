from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from src.controllers.controllers import MainWindowController, Recorder, Player


class DisplayWindow(QScrollArea):

    def __init__(self, article):
        super().__init__()

        self.__layout = QVBoxLayout()
        self.__layout.setAlignment(Qt.AlignTop )
        self.__widget = QWidget()
        self.setWindowTitle(article.name)

        self.__speechButton = QPushButton()
        self.__speechButton.setIcon(QtGui.QIcon("../res/icons/speaker.png"))
        self.__speechButton.setFixedSize(40,40)
        self.__speechButton.setIconSize(QtCore.QSize(32, 32))
        self.__speechButton.clicked.connect(self.playContent)
        self.__layout.addWidget(self.__speechButton)

        self.__titleLabel = QLabel(article.name)
        self.__layout.addWidget(self.__titleLabel)
        self.__contentLabel = QLabel(article.content)
        self.__layout.addWidget(self.__contentLabel)


        if(article.case !=""):
            self.__caseLabel = QLabel(article.case)
            self.__layout.addWidget(self.__caseLabel)

        self.__widget.setLayout(self.__layout)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setWidgetResizable(True)
        self.setWidget(self.__widget)

        self.__playingState = False
        self.__player = Player(article)
        self.__player.play_finish.connect(self.resetButton)

    def playContent(self):
        if self.__playingState ==False:
            self.__playingState = True
            self.__speechButton.setIcon(QtGui.QIcon("../res/icons/stop.png"))
            self.__speechButton.setIconSize(QtCore.QSize(32, 32))
            self.__player.start()
        else:
            self.__playingState=False
            self.__speechButton.setIcon(QtGui.QIcon("../res/icons/speaker.png"))
            self.__speechButton.setIconSize(QtCore.QSize(32, 32))
            self.__player.quit()

    def resetButton(self):
        self.__playingState = False
        self.__speechButton.setIcon(QtGui.QIcon("../res/icons/speaker.png"))
        self.__speechButton.setIconSize(QtCore.QSize(32, 32))

    def closeEvent(self, event):
        self.__player.quit()
        event.accept()


class MainWindow(QMainWindow):

    def __init__(self, config):
        super().__init__(parent=None)
        self.__windows = []
        self.setWindowTitle("Voice Assistant")
        self.setFixedSize(230, 200)

        self.__centralWidget = QWidget()
        self.setCentralWidget(self.__centralWidget)

        self.__generalLayout = QVBoxLayout()
        self.__centralWidget.setLayout(self.__generalLayout)

        self.__controller = MainWindowController(config)
        self.__recordingState = False
        self.__recorder = Recorder()
        self.__recorder.rec_finish.connect(self.finishRecorder)
        self.__recorder.rec_stop.connect(self.stopRecorder)

        self.__createButtons()

        self.show()

    def __createButtons(self):
        self.__label = QTextEdit()
        self.__label.setText("Asistent Vocal")
        self.__label.setReadOnly(True)
        self.__generalLayout.addWidget(self.__label)

        self.__speechButton = QPushButton()
        self.__speechButton.setIcon(QtGui.QIcon("../res/icons/mic.png"))
        self.__speechButton.setIconSize(QtCore.QSize(32, 32))
        self.__speechButton.clicked.connect(self.switchRecorder)
        self.__generalLayout.addWidget(self.__speechButton)


    def turnMicOff(self):
        self.__recordingState = False
        self.__speechButton.setIcon(QtGui.QIcon("../res/icons/mic.png"))

    def switchRecorder(self):
        if self.__recordingState == False:
            self.__recordingState = True
            self.__speechButton.setIcon(QtGui.QIcon("../res/icons/recording.png"))
            self.__label.setText("Înregistrare...")
            self.__recorder.start()
        else:
            self.turnMicOff()
            self.__label.setText("Asistent vocal")
            self.__recorder.quit()


    def finishRecorder(self, recording):
        if recording is not None:
            article = self.__controller.processRecording(recording)
            recording = recording.capitalize()
            self.__label.setText(recording)
            if article is not None:
                window = DisplayWindow(article)
                self.__windows.append(window)
                window.show()
            else:
                self.__label.setText("Repetați comanda")
        self.turnMicOff()


    def stopRecorder(self):
        print("recorder has stopped")
        self.turnMicOff()
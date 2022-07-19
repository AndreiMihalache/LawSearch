import configparser
import sys

from PyQt5.QtWidgets import QApplication

from views.windows import MainWindow


class App():
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('../res/config.ini')
        self.__app = QApplication(sys.argv)
        self.__view = MainWindow(config)
    def exec(self):
        sys.exit(self.__app.exec())

app = App()
app.exec()

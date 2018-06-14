#!/Users/toshi/miniconda3/bin/python

# https://www.cifraclub.com.br/joao-alexandre/pra-cima-brasil/

import sys
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtCore import QUrl, QObject
from PyQt5.QtQml import QQmlComponent, QQmlApplicationEngine

from web2chordpro import load


if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    engine.load("main.qml")

    root = engine.rootObjects()[0]
    url_field = root.findChild(QObject, "url")
    load_url_button = root.findChild(QObject, "loadUrlButton")
    title_field = root.findChild(QObject, "songTitle")
    key_field = root.findChild(QObject, "songKey")
    error_msg = root.findChild(QObject, "errorMsg")

    def clear_fields():
        title_field.setProperty("text", "")
        key_field.setProperty("text", "")
        error_msg.setProperty("text", "")

    def load_url():
        clear_fields()
        song_data = load(url_field.property("text"))
        if song_data:
            title_field.setProperty("text", song_data.title)
            key_field.setProperty("text", song_data.key)
        else:
            error_msg.setProperty("text", "Could not load song data :(")

    # Connect signals
    url_field.editingFinished.connect(load_url)
    load_url_button.clicked.connect(load_url)

    engine.quit.connect(app.quit)
    sys.exit(app.exec_())

#!/usr/bin/python3
import sys
import re
from pathlib import Path
from flask import Flask, render_template, request

from chopro import ChoPro
from config import *


app = Flask(__name__)

def get_html(filename):
    with open(filename) as cpfile:
        cpstr = cpfile.read()
    chopro = ChoPro(cpstr)
    return chopro.get_html()


@app.route('/')
def index():
    path = Path(CHOPRO_DIR)
    regex = re.compile(r".(chopro|chordpro)$", re.IGNORECASE)
    songs = {regex.sub('', f.name): f.name for f in path.iterdir()}
    return render_template('index.html', songs=sorted(songs.keys()), song_files=songs)

@app.route('/song')
def chords():
    filename = (Path(CHOPRO_DIR) / request.args['filename']).absolute()
    return render_template('chords.html', chords=get_html(filename))


if __name__=='__main__':
    app.run(debug=True)
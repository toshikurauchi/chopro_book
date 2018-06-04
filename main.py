#!/usr/bin/python3
import sys
import re
from pathlib import Path
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

from chopro import ChoPro
from config import *


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/chopro_book.db'
db = SQLAlchemy(app)


class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    songs = db.Column(db.PickleType)

    def __repr__(self):
        return '<Playlist %r>' % self.name


def get_html(filename, transpose):
    with open(filename) as cpfile:
        cpstr = cpfile.read()
    chopro = ChoPro(cpstr, transpose)
    return chopro.get_html()


def list_songs():
    path = Path(CHOPRO_DIR)
    regex = re.compile(r".(chopro|chordpro)$", re.IGNORECASE)
    return {regex.sub('', f.name): f.name for f in path.iterdir()}


@app.route('/')
def index():
    songs = list_songs()
    return render_template('index.html', songs=sorted(songs.keys()), song_files=songs)

@app.route('/playlists')
def playlists():
    all = ['as', 'sdf']
    return render_template('playlists.html', playlists=all)

@app.route('/song')
def chords():
    transpose = int(request.args['transpose']) if 'transpose' in request.args else 0
    filename = request.args['filename']
    full_filename = (Path(CHOPRO_DIR) / filename).absolute()
    return render_template('chords.html', chords=get_html(full_filename, transpose), song_file=filename, next_transpose=str(transpose + 1), prev_transpose=str(transpose - 1))

@app.route('/playlist')
def playlist_form():
    songs = list_songs()
    return render_template('playlist_form.html', song_files=songs)


if __name__=='__main__':
    app.run(debug=True)
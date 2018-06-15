#!/usr/bin/python3
import sys
import re
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for
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

    def __init__(self, id=None, name='', songs=[]):
        self.id = id
        self.name = name
        self.songs = songs

    def __repr__(self):
        return '<Playlist %r>' % self.name


def get_html(filename, transpose):
    with open(filename) as cpfile:
        cpstr = cpfile.read()
    chopro = ChoPro(cpstr, transpose)
    return chopro.get_html()


def clean_name(name):
    regex = re.compile(r".(chopro|chordpro)$", re.IGNORECASE)
    return regex.sub('', name)

def list_songs():
    path = Path(CHOPRO_DIR)
    
    return {clean_name(f.name): f.name for f in path.iterdir()}


@app.route('/')
def index():
    songs = list_songs()
    return render_template('index.html', songs=sorted(songs.keys()), song_files=songs)

@app.route('/playlists')
def playlists():
    all_playlists = Playlist.query.all()
    return render_template('playlists.html', playlists=all_playlists)

@app.route('/song')
def chords():
    transpose = int(request.args['transpose']) if 'transpose' in request.args else 0
    filename = request.args['filename']
    full_filename = (Path(CHOPRO_DIR) / filename).absolute()
    return render_template('chords.html', chords=get_html(full_filename, transpose), song_file=filename, next_transpose=str(transpose + 1), prev_transpose=str(transpose - 1))

@app.route('/playlist', methods=['GET', 'POST'])
def playlist_form():
    if (request.method == 'POST'):
        name = request.form.get('name')
        songs = request.form.get('songs').split(';;')
        playlist = Playlist(name=name, songs=songs)
        db.session.add(playlist)
        db.session.commit()
        return redirect(url_for('playlist_view', pid=playlist.id))
        
    songs = list_songs()
    return render_template('playlist_form.html', song_files=songs)

@app.route('/playlist/<pid>', methods=['GET'])
def playlist_view(pid):
    playlist = Playlist.query.get(pid)
    songs = [clean_name(s) for s in playlist.songs]
    song_files = {s: f for s, f in zip(songs, playlist.songs)}
    return render_template('playlist_view.html', playlist=playlist, songs=songs, song_files=song_files)


if __name__=='__main__':
    app.run(debug=True)
#!/usr/bin/python3
import sys
import re
from collections import OrderedDict
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

    @property
    def songs_dict(self):
        return OrderedDict((clean_name(s), s) for s in self.songs)


def get_html(filename, transpose):
    with open(filename) as cpfile:
        cpstr = cpfile.read()
    chopro = ChoPro(cpstr, transpose)
    return chopro.get_html()


def clean_name(name):
    regex = re.compile(r".(chopro|chordpro)$", re.IGNORECASE)
    return regex.sub('', name)


def list_songs(ignore=[]):
    path = Path(CHOPRO_DIR)
    songfiles = sorted([f for f in path.iterdir() if f.name not in ignore])
    return OrderedDict((clean_name(f.name), f.name) for f in songfiles)


@app.route('/')
def index():
    songs = list_songs()
    return render_template('index.html', song_files=songs)


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
@app.route('/playlist/<pid>/edit', methods=['GET', 'POST'], endpoint='playlist_edit')
def playlist_form(pid=None):
    if (request.method == 'POST'):
        name = request.form.get('name')
        songs = request.form.get('songs').split(';;')
        if pid is not None:
            playlist = Playlist.query.get(pid)
            playlist.name = name
            playlist.songs = songs
        else:
            playlist = Playlist(name=name, songs=songs)
        db.session.add(playlist)
        db.session.commit()
        return redirect(url_for('playlist_view', pid=playlist.id))
    
    # GET
    playlist = Playlist()
    form_action = url_for('playlist_form')
    if pid is not None:
        playlist = Playlist.query.get(pid)
        form_action = url_for('playlist_edit', pid=pid)
    selected_songs = playlist.songs_dict
    songs = list_songs(ignore=selected_songs.values())
    return render_template('playlist_form.html', playlist=playlist, selected_songs=selected_songs, song_files=songs, form_action=form_action)


@app.route('/playlist/<pid>', methods=['GET'])
def playlist_view(pid):
    playlist = Playlist.query.get(pid)
    return render_template('playlist_view.html', playlist=playlist, song_files=playlist.songs_dict)


if __name__=='__main__':
    app.run(debug=True)
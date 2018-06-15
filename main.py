#!/usr/bin/python3
import sys
import re
from unicodedata import normalize
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
    def song_list(self):
        return [Song(s) for s in self.songs]


class Song:
    def __init__(self, filename, transpose=0):
        self.filename = filename
        self.transpose = transpose

        self.name = clean_name(self.filename)
    
    def __eq__(self, other):
        return self.filename == other.filename

    @property
    def html(self):
        full_filename = (Path(CHOPRO_DIR) / self.filename).absolute()
        with open(full_filename) as cpfile:
            cpstr = cpfile.read()
        chopro = ChoPro(cpstr, self.transpose)
        return chopro.get_html()
    
    @property
    def next_transpose(self):
        return str(self.transpose + 1)
    
    @property
    def prev_transpose(self):
        return str(self.transpose - 1)

    @property
    def slug(self):
        # Based on: http://flask.pocoo.org/snippets/5/
        _punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
        result = []
        for word in _punct_re.split(self.filename.lower()):
            word = normalize('NFKD', word).encode('ascii', 'ignore')
            if word:
                result.append(''.join(map(chr, word)))
        return '-'.join(result)
        

def clean_name(name):
    regex = re.compile(r".(chopro|chordpro)$", re.IGNORECASE)
    return regex.sub('', name)


def list_songs(ignore=[]):
    path = Path(CHOPRO_DIR)
    songfiles = sorted([Song(f.name) for f in path.iterdir()], key=lambda s: s.filename)
    return [s for s in songfiles if s not in ignore]


@app.route('/')
def index():
    return render_template('index.html', songs=list_songs())


@app.route('/playlists')
def playlists():
    all_playlists = Playlist.query.all()
    return render_template('playlists.html', playlists=all_playlists)


@app.route('/song')
def chords():
    transpose = int(request.args['transpose']) if 'transpose' in request.args else 0
    song = Song(request.args['filename'], transpose)
    return render_template('chords.html', song=song)


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
    selected_songs = playlist.song_list
    available_songs = list_songs(ignore=selected_songs)
    return render_template('playlist_form.html', playlist=playlist, selected_songs=selected_songs, available_songs=available_songs, form_action=form_action)


@app.route('/playlist/<pid>', methods=['GET'])
def playlist_view(pid):
    playlist = Playlist.query.get(pid)
    return render_template('playlist_view.html', playlist=playlist, songs=playlist.song_list)


if __name__=='__main__':
    app.run(debug=True)
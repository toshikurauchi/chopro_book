#!/usr/bin/python3
import sys
import re
from unicodedata import normalize
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

from chopro import ChoPro
from config import *


SHORT_LIMIT = 100


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chopro_book.db'
db = SQLAlchemy(app)


class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    songs = db.relationship('PlaylistSong', backref='playlist', cascade="all,delete")

    def __init__(self, id=None, name='', song_files=[]):
        self.id = id
        self.name = name
        self.song_files = song_files
        self.new_songs = []
        self.deleted_songs = []

    def __repr__(self):
        return '<Playlist %r>' % self.name
    
    @property
    def sorted_songs(self):
        return sorted(self.songs, key=lambda s: s.index)

    @property
    def song_files(self):
        return [s.filename for s in self.sorted_songs]

    @song_files.setter
    def song_files(self, new_songs):
        current_songs = {s.filename: s for s in self.songs}
        self.new_songs = []
        self.songs = []
        for index, f in enumerate(new_songs):
            if f in current_songs:
                song = current_songs.pop(f)
                song.index = index
            else:
                song = PlaylistSong(self, f, index)
                self.new_songs.append(song)
            self.songs.append(song)
        self.deleted_songs = list(current_songs.values())

    @property
    def song_list(self):
        print([(s.filename, s.index) for s in self.sorted_songs])
        return [s.song for s in self.sorted_songs]


class PlaylistSong(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), nullable=False)
    transpose = db.Column(db.Integer)
    index = db.Column(db.Integer)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), nullable=False)

    def __init__(self, playlist, filename, index, transpose=0):
        self.playlist = playlist
        self.filename = filename
        self.index = index
        self.transpose = transpose
    
    @property
    def song(self):
        return Song(self.filename, self.transpose, self.id)


class Song:
    def __init__(self, filename, transpose=0, playlist_song_id=None):
        self.filename = filename
        self.transpose = transpose
        self.playlist_song_id = playlist_song_id
        self._lyrics = None

        self.name = clean_name(self.filename)
    
    def __eq__(self, other):
        return self.filename == other.filename

    def chopro(self):
        full_filename = (Path(CHOPRO_DIR) / self.filename).absolute()
        with open(full_filename) as cpfile:
            cpstr = cpfile.read()
        return ChoPro(cpstr, self.transpose)

    @property
    def html(self):
        return self.chopro().get_html()
    
    @property
    def lyrics(self):
        if self._lyrics is None:
            try:
                self._lyrics = self.chopro().get_lyrics()
            except:
                raise Exception(self.name)
        return self._lyrics
    
    @property
    def short_lyrics(self):
        lyrics = self.lyrics
        short = ''
        song_started = False
        for line in lyrics.split('\n'):
            clean = line.strip()
            if not song_started and clean:
                song_started = True
                if 'intro' in clean.lower():
                    continue
            if clean:
                short += clean + '<br>'
            if len(short) > SHORT_LIMIT:
                break
        return short

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
    transpose = int(request.args.get('transpose', 0))
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
            playlist.song_files = songs
        else:
            playlist = Playlist(name=name, song_files=songs)
        for s in playlist.new_songs:
            db.session.add(s)
        for s in playlist.deleted_songs:
            db.session.delete(s)
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


@app.route('/playlist-song/<pid>', methods=['GET'])
def playlist_song(pid):
    playlist_song = PlaylistSong.query.get(pid)
    transpose = int(request.args.get('transpose', 0))
    playlist_song.transpose = transpose
    
    # Save
    db.session.add(playlist_song)
    db.session.commit()

    song = playlist_song.song
    return render_template('playlist_song.html', song=song)


if __name__=='__main__':
    app.run(debug=True)
#!/Users/toshi/miniconda3/bin/python

import re
import requests
import click
from bs4 import BeautifulSoup


class Chord:
    def __init__(self, match, str):
        self.start = match.start(0)
        self.end = match.end(0)
        self.chord = str[self.start:self.end]

    def __str__(self):
        return self.chord

    def __repr__(self):
        return f'({self.start}, {self.end}): {self.chord}'

    @property
    def chopro(self):
        return f'[{self.chord}]'

class SongData:
    def __init__(self, title='', author='', key='', chords=''):
        self.title = title
        self.author = author
        self.key = key
        self.chords = chords
        self.chopro = None

    @property
    def chopro_chords(self):
        if self.chopro is None:
            self.chopro = ''
            last_chords = []
            for line in self.chords.split('\n'):
                is_chord_line = False
                if '<b>' in line:
                    is_chord_line = True
                    chords = line.replace('<b>', '').replace('</b>', '')
                    last_chords = [Chord(m, chords) for m in re.finditer('\S+', chords)]
                else:
                    chopro_line = ''
                    prev_i = 0
                    for chord in last_chords:
                        chopro_line += line[prev_i:chord.start] + chord.chopro
                        prev_i = chord.start
                    chopro_line += line[prev_i:]
                    last_chords = []
                    self.chopro += chopro_line + '\n'
        return self.chopro

    def write(self, filename=None):
        if filename is None:
            filename = self.title + '.chopro'
        with open(filename, 'w') as f:
            f.write('{t: ' + self.title + '}\n')
            if self.author:
                f.write('{st: ' + self.author + '}\n')
            if self.key:
                f.write('\n{key: ' + self.key + '}\n')
            f.write('\n')
            f.write(self.chopro_chords)


def load(chord_url):
    try:
        page = requests.get(chord_url)
        soup = BeautifulSoup(page.content, 'html.parser')
        div_cifra = soup.find('div', class_='cifra')
        title = str(div_cifra.find('h1').string)
        author = str(div_cifra.find('h2').find('a').string)
        key = str(div_cifra.find('span', id='cifra_tom').find('a').string)

        chords = str(div_cifra.find('pre'))
        chords = chords.replace('<pre>', '').replace('</pre>', '')

        return SongData(title, author, key, chords)
    except:
        return None


@click.command()
@click.argument('chord_url', type=str)
def convert(chord_url):
    song_data = load(chord_url)
    if song_data:
        song_data.write()


if __name__ == '__main__':
    convert()

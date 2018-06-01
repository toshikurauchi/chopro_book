"""chopro2html.py

Convert ChoPro/Chordpro to HTML
"""

import getopt
import sys


VERSION = '0.0.1'


def chopro2html(chopro_text):
    from chopro.core import ChoPro
    chopro = ChoPro(chopro_text)
    html = chopro.get_html()
    return html

def chopro2lyrics(chopro_text):
    from chopro.core import ChoPro
    chopro = ChoPro(chopro_text)
    lyrics = chopro.get_lyrics()
    return lyrics

if __name__ == '__main__':
    main()

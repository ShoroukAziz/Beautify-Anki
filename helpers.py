import  os, re
from aqt.mediasrv import RequestHandler
from anki.hooks import wrap
# -*- coding: utf-8 -*-
"""
Beautify Anki
an Addon for Anki
Github (https://github.com/my-Anki/Beautify-Anki)
Copyright (c) 2020 Shorouk Abdelaziz (https://shorouk.dev)
"""
#################################################################################
# Beautify Anki n is released under GNU AGPL, version 3 or later                #
# This Addon uses the following CSS and Javascript libraries                    #
#                                                                               #
# Acknowledgments                                                               #
# This Addon uses the following CSS and Javascript libraries                    #
#   - Materialize                                                               #
#   - Animate.css                                                               #
#   - plotly                                                                    #
# The Statistics part in the Deck Browser is based on Carlos Duarte             #
#  addon "More Decks Stats and Time Left" which is based on                     #
#  Dmitry Mikheev code, in add-on "More decks overview stats"                   #
#  and calumks code, in add-on "Deck Stats"                                     #
#                                                                               #
# The Statistics part in The Deck Overview pages is based on                    #
#  Kazuwuqt addon "More Overview Stats 2.1 " which is based on                  #
#  the More Overview Stats 2 add-on by Martin Zuther which is in turn based on  #
#  "More Overview Stats" by Calumks                                             #
#                                                                               #
#################################################################################
materialize_path = "assets/materialize.css"
fonts_path = "assets/flUhRq6tzZclQEJ-Vdg-IuiaDsNc.woff2"


FILES = re.compile(r'\.(?:jpe?g|gif|css|woff2|png|tiff|bmp)$', re.I) #Perl FTW! <3

RES_DIR = 'assets'
FILES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), RES_DIR))

def _redirectWebExports(self, path, _old):
    targetPath = os.path.join(os.getcwd(), RES_DIR, '')
    if path.startswith(targetPath):
        return os.path.join(FILES_DIR, path[len(targetPath):])
    return _old(self,path)

RequestHandler._redirectWebExports = wrap(RequestHandler._redirectWebExports, _redirectWebExports, 'around')

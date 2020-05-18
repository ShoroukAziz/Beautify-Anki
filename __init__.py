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

from .deck_browser import updateRenderingMethods
from .deck_overview import updateRenderingDeckOverview 
from .reviewer import renderReviewer
import aqt
from aqt import  gui_hooks
from typing import Optional, Any
from .config import *


updateRenderingMethods()
updateRenderingDeckOverview()
renderReviewer()

# if CONFIG['DARK_MODE']:
#     deckbrowser_dark = "deckbrowser_dark.css"
# else :
#     deckbrowserCSS = ""

# add my css and js to the deck overview page
def on_webview_will_set_content (web_content: aqt.webview.WebContent,  context: Optional[Any]):
    # showInfo(str(context))
    if  isinstance(context, (
        aqt.deckbrowser.DeckBrowser ,aqt.overview.Overview,aqt.toolbar.TopToolbar ,
         aqt.deckbrowser.DeckBrowserBottomBar , aqt.overview.OverviewBottomBar, aqt.reviewer.ReviewerBottomBar)):        
        # web_content.js.append ("../assets/js/canvasjs.min.js")
        web_content.js.append ("../assets/js/script.js")
        web_content.css.append ("../assets/css/font.css")
        web_content.css.append ("../assets/css/animate.css")
        web_content.css.append ("../assets/css/materialize.css")

    if  isinstance(context, aqt.overview.Overview):        
        web_content.css.append ("../assets/css/overview.css")
        web_content.js.append ("../assets/js/plotly-latest.min.js")

        

    if  isinstance(context, aqt.deckbrowser.DeckBrowser):        
        web_content.css.append ("../assets/css/deckbrowser.css")
        # web_content.css.append ("../assets/css/{}".format(deckbrowser_dark))
    if isinstance (context , ( aqt.deckbrowser.DeckBrowserBottomBar,aqt.overview.OverviewBottomBar)):         
        web_content.css.append ("../assets/css/bottombar.css")

    if isinstance (context ,  aqt.toolbar.TopToolbar):
        web_content.css.append ("../assets/css/toolbar.css")
    if isinstance (context , aqt.reviewer.ReviewerBottomBar):
      web_content.css.append ("../assets/css/reviewer_bottom.css")

gui_hooks.webview_will_set_content.append(on_webview_will_set_content)
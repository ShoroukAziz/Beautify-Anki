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
#   - Bootstrap                                                                 #
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

from aqt import mw


updateRenderingMethods()
updateRenderingDeckOverview()
if CONFIG["change answer buttons"]:
    renderReviewer()


addon = mw.addonManager.addonFromModule(__name__)
base="/_addons/"+addon

# add the assests folder to the media server
mw.addonManager.setWebExports(__name__, r"user_files/assets/.+(\.svg|\.png|\.css|\.woff|\woff2|\.jpeg|\.gif|\.tiff|\.bmp|\.jpg|\.js|\.TTF|\.ttf|\.otf)")


# add my css and js 
def on_webview_will_set_content (web_content: aqt.webview.WebContent,  context: Optional[Any]):
    
    # add css and js to all contexts
    if  isinstance(context, (
        aqt.deckbrowser.DeckBrowser ,aqt.overview.Overview,aqt.toolbar.TopToolbar ,
         aqt.deckbrowser.DeckBrowserBottomBar , aqt.overview.OverviewBottomBar)) :        
      
        if CONFIG["animation"]:
            web_content.css.append (base+"/user_files/assets/css/animate.css")

        web_content.css.append (base+"/user_files/assets/css/bootstrap.min.css")
        web_content.css.append (base+"/user_files/assets/css/universal.css")
        

        
        
    # add css and js to deck overview
    if  isinstance(context, aqt.overview.Overview):        
        web_content.css.append (base+"/user_files/assets/css/overview.css")
        web_content.css.remove("overview.css")
        web_content.css.remove("css/webview.css")
        web_content.js.append (base+"/user_files/assets/js/plotly-latest.min.js")  

    # add css and js to deck browser
    if  isinstance(context, aqt.deckbrowser.DeckBrowser):        
        web_content.css.append (base+"/user_files/assets/css/deckbrowser.css")
        web_content.css.remove("css/deckbrowser.css")
    
    # add css and js to deck browser bottom bar
    if isinstance (context , ( aqt.deckbrowser.DeckBrowserBottomBar,aqt.overview.OverviewBottomBar)):        
        web_content.css.append (base+"/user_files/assets/css/bottombar.css")
        web_content.css.remove("css/webview.css")

        if NIHGT_MODE:         
            web_content.css.append (base+"/user_files/assets/css/bottombar_dark.css")

    # add css and js to top bar
    if isinstance (context ,  aqt.toolbar.TopToolbar):
        web_content.css.append (base+"/user_files/assets/css/toolbar.css")
    
    # add css and js to reviewer bottom bar
    if isinstance (context , aqt.reviewer.ReviewerBottomBar) and CONFIG["change answer buttons"]:
      web_content.css.append (base+"/user_files/assets/css/reviewer_bottom.css")
      web_content.css.append (base+"/user_files/assets/css/bootstrap.min.css")

gui_hooks.webview_will_set_content.append(on_webview_will_set_content)
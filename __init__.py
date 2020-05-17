# based on Carlos Duarte in add-on (More Decks Stats and Time Left) https://ankiweb.net/shared/info/1556734708 
#License        | GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


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
        web_content.js.append ("../assets/js/canvasjs.min.js")
        web_content.js.append ("../assets/js/script.js")
        web_content.css.append ("../assets/css/font.css")
        web_content.css.append ("../assets/css/animate.css")
        web_content.css.append ("../assets/css/materialize.css")

    if  isinstance(context, aqt.overview.Overview):        
        web_content.css.append ("../assets/css/overview.css")
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
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

from anki.errors import DeckRenameError
from anki.hooks import wrap
import anki.sched, anki.schedv2
from anki.lang import _, ngettext
from aqt import mw
from aqt.deckbrowser import DeckBrowser , DeckBrowserBottomBar , RenderDeckNodeContext
from aqt.toolbar import Toolbar , BottomBar
from aqt.reviewer import Reviewer
from aqt.utils import *


from aqt import AnkiQt, gui_hooks
from aqt.utils import shortcut 
from copy import deepcopy
from .config import *

from anki.rsbackend import TR, DeckTreeNode


bg_animation = CONFIG["animation"]




def init(self, mw: AnkiQt) -> None:
    self.mw = mw
    self.web = mw.web
    self.scrollPos = QPoint(0, 0)

CountTimesNew = 2
def renderStats(self, _old):
    # Get due and new cards
    new = 0
    lrn = 0
    due = 0

    for tree in self.mw.col.sched.deckDueTree():
        new += tree[4]
        lrn += tree[3]
        due += tree[2]

    total = (CountTimesNew*new) + lrn + due
    totalDisplay = new + lrn + due

    # Get studdied cards
    cards, thetime = self.mw.col.db.first(
            """select count(), sum(time)/1000 from revlog where id > ?""",
            (self.mw.col.sched.dayCutoff - 86400) * 1000)

    cards   = cards or 0
    thetime = thetime or 0

    speed   = cards * 60 / max(1, thetime)
    minutes = int(total / max(1, speed))             

    
    buf="""
    


    
    <div class='row align-items-center full   stats' style="background-color: {BROWSER[overview-wedgit-bg]} ">
            <div class="col col-sm-2 ">
                    <i class=" material-icons  medium  left">{BROWSER[overview-wedgit-icon]}</i> 
            </div>
            <div class="col col-sm-10"> {old_stats} </div>
    </div>
    
    <!------------------END ROW 1------------------------------->

    <div class="row align-items-center full">

        <div class='col col-sm-6  stats half left ' style="background-color: {BROWSER[average-wedgit-bg]}">
            <div class="row align-items-center">
                    <div class="col col-sm-3">
                    <i class=" material-icons  medium  ">{BROWSER[average-wedgit-icon]}</i> 
                    </div>

                    <div class="col col-sm-9">{LOCALS[Average]}: {speed:.2f} <br> {LOCALS[cards/minute]} </div>
            </div>   
        </div>

        <div class='col col-sm-6  stats half right ' style="background-color:  {BROWSER[remaining-wedgit-bg]}">
            <div class="row align-items-center">
                <div class="col col-sm-3">
                <i class=" material-icons  medium  ">{BROWSER[remaining-wedgit-icon]}</i>
                </div>
                <div class="col col-sm-9">
                {} {LOCALS[more]}
                </div>
             </div>
        </div>

    </div>
<!--------------------END ROW 2----------------------------->

    <div class="row align-items-center full">

        <div class='col col-sm-6  stats  half left' style="background-color:{BROWSER[new-wedgit-bg]}">

        <div class="row align-items-center">
        <div class="col col-sm-3">
             <i class=' material-icons  medium  '>{BROWSER[new-wedgit-icon]}</i>
             </div>
              <div class="col col-sm-9">
            {new_count} <br>   {LOCALS[New]}
            </div>
        </div>
        </div>



        <div class='col col-sm-6  stats  half right'style="background-color: {BROWSER[due-wedgit-bg]}">
            <div class="row align-items-center">
                <div class="col col-sm-3">
                <i class=' material-icons  medium '>{BROWSER[due-wedgit-icon]}</i>
                </div>

                <div class="col col-sm-9">
                {due_count}  &nbsp;  {LOCALS[Due]}    <br>
                {learn_count} &nbsp;  {LOCALS[Learn]} <br> 
                {review_count}  &nbsp;   {LOCALS[Review]}  
                </div>


            </div>


        </div>



    </div>


<!--------------------END ROW 3----------------------------->




    <div class='row align-items-center full stats'  style="background-color:{BROWSER[total-wedgit-bg]} ">
              <div class="col col-sm-2">
                    <i class=' material-icons  medium  left'>{BROWSER[total-wedgit-icon]} </i>
                    </div>
                    <div class="col col-sm-10">
                    {total_cards} <br>  {LOCALS[Total]}
                    </div>
           

    </div>


    </div></div>
    """.format( str(ngettext("%s <br>  {LOCALS[minute]} ".format( LOCALS=LOCALS), "%s <br>  {LOCALS[minutes]}".format( LOCALS=LOCALS), minutes) % (minutes)),
        old_stats=_old(self), speed=speed,
        new_count=new,due_count=lrn+due,learn_count=lrn,review_count=due,
        total_cards=totalDisplay,BROWSER=BROWSER , LOCALS=LOCALS)
    
  
    return buf



def renderDeckTree(self, top: DeckTreeNode,_old) -> str:
        buf = ""

        ctx = RenderDeckNodeContext(current_deck_id=self.mw.col.conf["curDeck"])

        for child in top.children:
            buf += self._render_deck_node(child, ctx)

        return buf


def render_deck_node(self, node: DeckTreeNode, ctx: RenderDeckNodeContext,_old) -> str:
    if node.collapsed:
        prefix = "+"
    else:
        prefix = "-"

    due = node.review_count + node.learn_count

    def indent():
        return "&nbsp;" * 6 * (node.level - 1)

    if node.deck_id == ctx.current_deck_id:
        klass = "deck current"
    else:
        klass = "deck"

    buf = "<div class='deck-row row align-items-center %s' id='%d'>" % (klass, node.deck_id)
    # deck link
    if node.children:
        collapse = (
            "<a class=collapseable href=# onclick='return pycmd(\"collapse:%d\")'>%s</a>"
            % (node.deck_id, prefix)
        )
    else:
        collapse = "<span class=collapseable></span>"
    if node.filtered:
        extraclass = "filtered"
    else:
        extraclass = ""
    buf += """<div class="col col-sm-1">
          <img src="%s/assets/deck_icons/%s.png" onerror="this.src='%s/assets/deck_icons/default.png'" alt="" class="circle"></div>

    <div  class='col col-sm-8 decktd ' >%s%s<a class="align-middle deck padding %s"
    href=# onclick="return pycmd('open:%d')">%s</a></div>""" % (
        base,
        node.name,
        base,
        indent(),
        collapse,
        extraclass,
        node.deck_id,
        node.name,
    )
    # due counts
    def nonzeroColour(cnt, klass):
        if not cnt:
            klass = "zero-count"
        return f'<div class="{klass}">{cnt}</div>'

    buf += " <div class='col col-sm-1 ' >%s</div><div class='col col-sm-1 ' >%s</div> " % (
        nonzeroColour(due, "review-count"),
        nonzeroColour(node.new_count, "new-count"),
    )
    # options
    buf += (
        "<div  class='opts col col-sm-1'><a onclick='return pycmd(\"opts:%d\");'>"
        "<i style=\"color:{THEME[gear-icon-color]}  \" class=\'gears material-icons\'>settings</i></a></div></div>".format(THEME=THEME) % node.deck_id
    )
    # children
    if not node.collapsed:
        for child in node.children:
            buf += self._render_deck_node(child, ctx)
    return buf



DeckBrowser.drawLinks = [
        ["", "shared", _("<i class='material-icons left'>cloud_download</i> Get Shared")],
        ["", "create", _("<i class='material-icons left'>create_new_folder</i>Create Deck")],
        ["Ctrl+I", "import", _("<i class='material-icons left'>file_upload</i>Import File")], 
    ]

def drawButtons(self,_old):
    buf = """<style> 
    
    #outer{{
  background-color: {THEME[bottombar-color]};
    }}
     </style>""".format(THEME=THEME)
    drawLinks = deepcopy(self.drawLinks)
    for b in drawLinks:
        if b[0]:
            b[0] = _("Shortcut key: %s") % shortcut(b[0])
        buf += """
<a class='waves-effect waves-light btn-small' style="background:{THEME[buttons-color]} " title='%s' onclick='pycmd(\"%s\");'> %s </a>""".format(THEME=THEME) %  tuple(
            b
        )
    self.bottom.draw(
        
        buf=buf,
        link_handler=self._linkHandler,
        web_context=DeckBrowserBottomBar(self),
    )





Toolbar. _body = """
<nav style="text-align:{THEME[topbar-position]};background-color:{THEME[topbar-color]}"  width=100%%>
<tr>
<td class=tdcenter'>%s</td>
</tr></nav>
""".format(THEME=THEME)

animation = ""
if bg_animation :
    animation = """
    <div class="crossfade">
        <figure></figure>
        <figure></figure>
        <figure></figure>
        <figure></figure>
        <figure></figure>
    </div>

    """
else:
    animation ="""
    <style>
    body{
        background-image: url('%s/assets/background.jpg') !important ; 

    }
    </style>
    """%(base)

main_bg = """

.deck-row{{
    border-bottom: 1px solid {THEME[decks-border-color]} 

}}

.decks-container{{
background-color:{THEME[large-areas-color]} ;
}}

a.deck , .collapseable{{
    color: {THEME[decks-font-color]};
}}

.filtered{{
    color: {THEME[filtered-deck-color]} !important;;
}}

@font-face {{
    font-family: '{THEME[decks-font-family]}';
    src: url('{base}/assets/fonts/{THEME[decks-font-src]}');   
}}

@font-face {{
    font-family: '{BROWSER[wedgits-font-family]}';
    src: url('{base}/assets/fonts/{BROWSER[wedgits-font-src]}');   
}}

.decktd{{
    font-size:{THEME[decks-font-size]};
    font-family:{THEME[decks-font-family]};
}}

.stats{{
    font-size:{BROWSER[wedgits-font-size]};
    font-family:{BROWSER[wedgits-font-family]};
}}

.review-count{{
    background-color:{BROWSER[review-count-background-color]} ;
    color: {BROWSER[review-count-color]};
}}


.new-count{{
    background-color:{BROWSER[new-count-background-color]} ;
    color: {BROWSER[new-count-color]};
}}

""".format(THEME=THEME,BROWSER=BROWSER, base=base)


DeckBrowser._body = """
<style>
{main_bg}

</style>

<div class="overlay" style="background : linear-gradient(20deg,{THEME[overlay-color1]}, {THEME[overlay-color2]}) ;" >
{animation}
<center class="container">
<div class=row>
<div class="col col-sm-12 col-md-7 col-lg-8">
<div class="container decks-container">
%(tree)s
</div>
</div>
<div class="col col-sm-12 col-md-5 col-lg-4" style="color:{BROWSER[wedgits-font-color]}">
%(stats)s
</div>
</center>
</div>
""".format(animation=animation,THEME=THEME,main_bg=main_bg,BROWSER=BROWSER)

def updateRenderingMethods():   

    DeckBrowser._renderDeckTree = wrap(DeckBrowser._renderDeckTree , renderDeckTree, "around")
    DeckBrowser._render_deck_node = wrap(DeckBrowser._render_deck_node, render_deck_node, 'around')
    DeckBrowser._drawButtons = wrap(DeckBrowser._drawButtons, drawButtons, 'around')
    DeckBrowser._renderStats = wrap(DeckBrowser._renderStats, renderStats, 'around')
    
    
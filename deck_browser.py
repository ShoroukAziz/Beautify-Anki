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



addon = mw.addonManager.addonFromModule(__name__)
base="/_addons/"+addon


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
    


    <div class="row" >
    <div class='col s12 valign-wrapper card-panel stats' style="background-color: {BROWSER[overview-wedgit-bg]} ">
            <i class=" material-icons  medium  left">{BROWSER[overview-wedgit-icon]}</i>
        {old_stats}
    </div>
    </div>
    <div class="row">
    <div class='col s6 m6 valign-wrapper  card-panel  stats  ' style="background-color: {BROWSER[average-wedgit-bg]}">
        <i class=" material-icons  medium  left">{BROWSER[average-wedgit-icon]}</i> Average:
        {speed:.2f} <br> cards/minute
    </div>
    <div class='col s6  valign-wrapper  card-panel  stats ' style="background-color:  {BROWSER[remaining-wedgit-bg]}">
        <i class=" material-icons  medium  left">{BROWSER[remaining-wedgit-icon]}</i> {} more
    </div>
    </div>
    <div class="row">
    <div class='col s6 valign-wrapper  card-panel  stats  ' style="background-color:{BROWSER[new-wedgit-bg]}">
    <i class=' material-icons  medium  left'>{BROWSER[new-wedgit-icon]}</i>  {new_count} <br>  New
    </div>
    <div class='col s6 valign-wrapper  card-panel  stats  'style="background-color: {BROWSER[due-wedgit-bg]}">
    <i class=' material-icons  medium left'>{BROWSER[due-wedgit-icon]}</i> {due_count}  &nbsp; Due    <br>
       {learn_count} &nbsp; Learn <br> 
    {review_count}  &nbsp;  Review 
    </div>
    </div>
    <div class='row'>
        <div class='col s12 m6 valign-wrapper  card-panel  stats ' style="background-color:{BROWSER[total-wedgit-bg]} ">
    <i class=' material-icons  medium  left'>{BROWSER[total-wedgit-icon]} </i>  {total_cards} <br> Total
    </div>

    </div>
    </div></div>
    """.format( str(ngettext("%s <br> minute", "%s <br> minutes", minutes) % (minutes)),
        old_stats=_old(self), speed=speed,
        new_count=new,due_count=lrn+due,learn_count=lrn,review_count=due,
        total_cards=totalDisplay,BROWSER=BROWSER)
    
  
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

    buf = "<li class='collection-item avatar row %s' id='%d'>" % (klass, node.deck_id)
    # deck link
    if node.children:
        collapse = (
            "<a class=collapse href=# onclick='return pycmd(\"collapse:%d\")'>%s</a>"
            % (node.deck_id, prefix)
        )
    else:
        collapse = "<span class=collapse></span>"
    if node.filtered:
        extraclass = "filtered"
    else:
        extraclass = ""
    buf += """
          <img src="%s/assets/deck_icons/%s.png" onerror="this.src='%s/assets/deck_icons/default.png'" alt="" class="circle">
    <span  class='col s7 decktd ' colspan=5>%s%s<a class="deck padding %s"
    href=# onclick="return pycmd('open:%d')">%s</a></span>""" % (
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
        return f'<span class="{klass}">{cnt}</span>'

    buf += " <span class='col s2 ' align=center>%s</span><span class='col s2 ' align=center>%s</span> " % (
        nonzeroColour(due, "review-count"),
        nonzeroColour(node.new_count, "new-count"),
    )
    # options
    buf += (
        "<span align=center class='opts col s1'><a onclick='return pycmd(\"opts:%d\");'>"
        "<i style=\"color:{THEME[gear-icon-color]}  \" class=\'gears material-icons\'>settings</i></a></span></li>".format(THEME=THEME) % node.deck_id
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
        background-image: url('./assets/background.jpg') !important ; 

    }
    </style>
    """

main_bg = """
.collection .collection-item {{
background-color: rgba(0,0,0,0) ;
border-bottom: 1px solid {THEME[decks-border-color]} 
}}

.card{{
background-color:{THEME[large-areas-color]} ;
}}

a.deck , .collapse{{
    color: {THEME[decks-font-color]};
}}

.filtered{{
    color: {THEME[filtered-deck-color]} !important;;
}}

""".format(THEME=THEME)


DeckBrowser._body = """
<style>
{main_bg}

</style>

<div class="overlay" style="background : linear-gradient(20deg,{THEME[overlay-color1]}, {THEME[overlay-color2]}) ;" >
{animation}
<center class="container">
<div class=row>
<div class="col s8">
<ul class=" card collection highlight" cellspacing=0 cellpading=3>
%(tree)s
</ul>
</div>
<div class="col s4" style="color:{BROWSER[wedgits-font-color]}">
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
    
    
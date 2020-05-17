
from anki.errors import DeckRenameError
from anki.hooks import wrap
import anki.sched, anki.schedv2
from anki.lang import _, ngettext
from aqt import mw
from aqt.deckbrowser import DeckBrowser , DeckBrowserBottomBar
from aqt.toolbar import Toolbar , BottomBar
from aqt.reviewer import Reviewer
from aqt.utils import *


from aqt import AnkiQt, gui_hooks
from aqt.utils import shortcut 
from copy import deepcopy
from .helpers import *
from .config import *


def init(self, mw: AnkiQt) -> None:
    self.mw = mw
    self.web = mw.web
    # self.bottom = BottomBar(mw, mw.bottomWeb)
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
    <div class="row">
    <div class='col s12 valign-wrapper card horizontal small stats  {STATS[label-bg1]}  {STATS[labels-color]}'>
            <i class=" material-icons  medium {STATS[labels-color]}   left">{STATS[icon1]}</i>
        {old_stats}
    </div>
    </div>
    <div class="row">
    <div class='col s6 valign-wrapper card horizontal small stats  {STATS[label-bg2]} {STATS[labels-color]}'>
        <i class=" material-icons  medium {STATS[labels-color]} left">{STATS[icon2]}</i> Average:
        {speed:.2f} <br> cards/minute
    </div>
    <div class='col s6 valign-wrapper card horizontal small stats   {STATS[label-bg3]} {STATS[labels-color]}'>
        <i class=" material-icons  medium {STATS[labels-color]} left">{STATS[icon3]}</i> {} more
    </div>
    </div>
    <div class="row">
    <div class='col s6 valign-wrapper card horizontal small stats  {STATS[label-bg4]} {STATS[labels-color]}'>
    <i class=' material-icons  medium {STATS[labels-color]}   left'>{STATS[icon4]}</i>   New Cards :  &nbsp; {new_count}
    </div>
    <div class='col s6 valign-wrapper card horizontal small stats  {STATS[label-bg5]} {STATS[labels-color]}'>
    <i class=' material-icons  medium {STATS[labels-color]}   left'>{STATS[icon5]}</i>   Due  :  &nbsp; {due_count}<br>
    Learn : &nbsp; {learn_count} <br> 
    Review : &nbsp; {review_count} 
    </div>
    </div>
    <div class='row'>
        <div class='col s12 valign-wrapper card horizontal small stats {STATS[label-bg6]} {STATS[labels-color]}'>
    <i class=' material-icons  medium {STATS[labels-color]} left'>{STATS[icon6]} </i> Total :  &nbsp;  {total_cards}
    </div>

    </div>
    </div></div>
    """.format( str(ngettext("%s minute", "%s minutes", minutes) % (minutes)),
        old_stats=_old(self), speed=speed,
        new_count=new,due_count=lrn+due,learn_count=lrn,review_count=due,
        total_cards=totalDisplay,STATS=STATS)
    
  
    return buf


def renderDeckTree(self, nodes,depth, _old,):
    if not nodes:
        return ""
    buf = ""
    nameMap = self.mw.col.decks.nameMap()
    for node in nodes:
        buf += self._deckRow(node, depth, len(nodes), nameMap)
    return buf

def deckRow(self, node, depth, cnt, nameMap , _old):
    name, did, due, lrn, new, children = node
    deck = self.mw.col.decks.get(did)
    if did == 1 and cnt > 1 and not children:
        # if the default deck is empty, hide it
        if not self.mw.col.db.scalar("select 1 from cards where did = 1"):
            return ""
    # parent toggled for collapsing
    for parent in self.mw.col.decks.parents(did, nameMap):
        if parent["collapsed"]:
            buff = ""
            return buff
    prefix = " - "
    if self.mw.col.decks.get(did)["collapsed"]:
        prefix = " + "
    due += lrn

    def indent():
        return "&nbsp;" * 6 * depth

    if did == self.mw.col.conf["curDeck"]:
        klass = "deck current"
    else:
        klass = "deck"
    buf = "<li class='collection-item avatar row %s' id='%d'>" % (klass, did)
    # deck link
    if children:
        collapse = (
            "<a class='collapse padding' href=# onclick='return pycmd(\"collapse:%d\")'>%s</a>"
            % (did, prefix)
        )
    else:
        collapse = "<span class=collapse></span>"
    if deck["dyn"]:
        extraclass = "filtered"
    else:
        extraclass = ""
    buf += """
          <img src="assets/deck_icons/%s.png"  onerror="this.src='assets/deck_icons/default.png'" alt="" class="circle">
    <span  class='col s7 decktd ' colspan=5>%s%s<a class="deck padding %s"
    href=# onclick="return pycmd('open:%d')">%s</a></span>""" % (
        name,
        indent(),
        collapse,
        extraclass,
        did,
        name,
    )
    # due counts
    def nonzeroColour(cnt, klass):
        if not cnt:
            klass = "zero-count"
        if cnt >= 1000:
            cnt = "1000+"
        return f'<span class="{klass}">{cnt}</span>'

    buf += " <span class='col s2 ' align=center>%s</span><span class='col s2 ' align=center>%s</span> " % (
        nonzeroColour(due, "review-count"),
        nonzeroColour(new, "new-count"),
    )
    # options
    buf += (
        "<span align=center class='opts col s1'><a onclick='return pycmd(\"opts:%d\");'>"
        "<img src='/assets/gears.svg' class=gears></a></span></li>" % did
    )
    # children
    buf += self._renderDeckTree(children, depth + 1)
    return buf




DeckBrowser.drawLinks = [
        ["", "shared", _("<i class='material-icons left'>cloud_download</i> Get Shared")],
        ["", "create", _("<i class='material-icons left'>create_new_folder</i>Create Deck")],
        ["Ctrl+I", "import", _("<i class='material-icons left'>file_upload</i>Import File")], 
    ]

def drawButtons(self,_old):
    buf = ""
    drawLinks = deepcopy(self.drawLinks)
    for b in drawLinks:
        if b[0]:
            b[0] = _("Shortcut key: %s") % shortcut(b[0])
        buf += """
<a class='{MAIN[bg-color]} waves-effect waves-light btn-small' title='%s' onclick='pycmd(\"%s\");'> %s </a>""".format(MAIN=MAIN) %  tuple(
            b
        )
    self.bottom.draw(
        
        buf=buf,
        link_handler=self._linkHandler,
        web_context=DeckBrowserBottomBar(self),
    )




Toolbar. _body = """
<nav class='{MAIN[bg-color]}'  width=100%%>
<tr>
<td class=tdcenter align=center>%s</td>
</tr></nav>
""".format(MAIN=MAIN)

DeckBrowser._body = """'
<center class="container">
<div class=row>
<div class="col s8">
<ul class=" card collection highlight" cellspacing=0 cellpading=3>
%(tree)s
</ul>
</div>
<div class="col s4">
%(stats)s
</div>
</center>
"""

def updateRenderingMethods():   

    DeckBrowser._renderDeckTree = wrap(DeckBrowser._renderDeckTree , renderDeckTree, "around")
    DeckBrowser._deckRow = wrap(DeckBrowser._deckRow, deckRow, 'around')
    DeckBrowser._drawButtons = wrap(DeckBrowser._drawButtons, drawButtons, 'around')
    DeckBrowser._renderStats = wrap(DeckBrowser._renderStats, renderStats, 'around')
    
    
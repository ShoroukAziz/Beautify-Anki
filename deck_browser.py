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
#   - Bootstrap                                                               #
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
            <div class="col col-2 ">
                <svg width="3em" height="3em" viewBox="0 0 16 16" class="bi bi-card-checklist" fill="{BROWSER[wedgits-font-color]}" xmlns="http://www.w3.org/2000/svg">
                    <path fill-rule="evenodd" d="M14.5 3h-13a.5.5 0 0 0-.5.5v9a.5.5 0 0 0 .5.5h13a.5.5 0 0 0 .5-.5v-9a.5.5 0 0 0-.5-.5zm-13-1A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h13a1.5 1.5 0 0 0 1.5-1.5v-9A1.5 1.5 0 0 0 14.5 2h-13z"/>
                    <path fill-rule="evenodd" d="M7 5.5a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1-.5-.5zm-1.496-.854a.5.5 0 0 1 0 .708l-1.5 1.5a.5.5 0 0 1-.708 0l-.5-.5a.5.5 0 1 1 .708-.708l.146.147 1.146-1.147a.5.5 0 0 1 .708 0zM7 9.5a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1-.5-.5zm-1.496-.854a.5.5 0 0 1 0 .708l-1.5 1.5a.5.5 0 0 1-.708 0l-.5-.5a.5.5 0 0 1 .708-.708l.146.147 1.146-1.147a.5.5 0 0 1 .708 0z"/>
                </svg>
            </div>
            <div class="col col-10"> {old_stats} </div>
    </div>
    
    <!------------------END ROW 1------------------------------->

    <div class="row align-items-center full">

        <div class='col col-6  stats half left ' style="background-color: {BROWSER[average-wedgit-bg]}">
            <div class="row align-items-center">
                    <div class="col col-4">
                        <svg width="3em" height="3em" viewBox="0 0 16 16" class="bi bi-watch" fill="{BROWSER[wedgits-font-color]}" xmlns="http://www.w3.org/2000/svg">
                        <path fill-rule="evenodd" d="M4 14.333v-1.86A5.985 5.985 0 0 1 2 8c0-1.777.772-3.374 2-4.472V1.667C4 .747 4.746 0 5.667 0h4.666C11.253 0 12 .746 12 1.667v1.86A5.985 5.985 0 0 1 14 8a5.985 5.985 0 0 1-2 4.472v1.861c0 .92-.746 1.667-1.667 1.667H5.667C4.747 16 4 15.254 4 14.333zM13 8A5 5 0 1 0 3 8a5 5 0 0 0 10 0z"/>
                        <path d="M13.918 8.993A.502.502 0 0 0 14.5 8.5v-1a.5.5 0 0 0-.582-.493 6.044 6.044 0 0 1 0 1.986z"/>
                        <path fill-rule="evenodd" d="M8 4.5a.5.5 0 0 1 .5.5v3a.5.5 0 0 1-.5.5H6a.5.5 0 0 1 0-1h1.5V5a.5.5 0 0 1 .5-.5z"/>
                        </svg>
                    </div>

                    <div class="col col-8">{LOCALS[Average]}: {speed:.2f} <br> {LOCALS[cards/minute]} </div>
            </div>   
        </div>

        <div class='col col-6  stats half right ' style="background-color:  {BROWSER[remaining-wedgit-bg]}">
            <div class="row align-items-center">
                <div class="col col-4">
                    <svg width="3em" height="3em" viewBox="0 0 16 16" class="bi bi-stopwatch-fill" fill="{BROWSER[wedgits-font-color]}" xmlns="http://www.w3.org/2000/svg">
                    <path fill-rule="evenodd" d="M5.5.5A.5.5 0 0 1 6 0h4a.5.5 0 0 1 0 1H9v1.07A7.002 7.002 0 0 1 8 16 7 7 0 0 1 7 2.07V1H6a.5.5 0 0 1-.5-.5zm3 4.5a.5.5 0 0 0-1 0v3.5h-3a.5.5 0 0 0 0 1H8a.5.5 0 0 0 .5-.5V5z"/>
                    </svg>
                </div>
                <div class="col col-8">
                {} {LOCALS[more]}
                </div>
             </div>
        </div>

    </div>
<!--------------------END ROW 2----------------------------->

    <div class="row align-items-center full">

        <div class='col col-6  stats  half left' style="background-color:{BROWSER[new-wedgit-bg]}">

        <div class="row align-items-center">
        <div class="col col-4">
            <svg width="3em" height="3em" viewBox="0 0 16 16" class="bi bi-layers-fill" fill="{BROWSER[wedgits-font-color]}" xmlns="http://www.w3.org/2000/svg">
            <path fill-rule="evenodd" d="M7.765 1.559a.5.5 0 0 1 .47 0l7.5 4a.5.5 0 0 1 0 .882l-7.5 4a.5.5 0 0 1-.47 0l-7.5-4a.5.5 0 0 1 0-.882l7.5-4z"/>
            <path fill-rule="evenodd" d="M2.125 8.567l-1.86.992a.5.5 0 0 0 0 .882l7.5 4a.5.5 0 0 0 .47 0l7.5-4a.5.5 0 0 0 0-.882l-1.86-.992-5.17 2.756a1.5 1.5 0 0 1-1.41 0l.418-.785-.419.785-5.169-2.756z"/>
            </svg>
             </div>
              <div class="col col-8">
            {new_count} <br>   {LOCALS[New]}
            </div>
        </div>
        </div>



        <div class='col col-6  stats  half right'style="background-color: {BROWSER[due-wedgit-bg]}">
            <div class="row align-items-center">
                <div class="col col-4">
                    <svg width="3em" height="3em" viewBox="0 0 16 16" class="bi bi-pencil-square" fill="{BROWSER[wedgits-font-color]}" xmlns="http://www.w3.org/2000/svg">
                    <path d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456l-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z"/>
                    <path fill-rule="evenodd" d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5v11z"/>
                    </svg>

                </div>

                <div class="col col-8">
                {due_count}  &nbsp;  {LOCALS[Due]}    <br>
                {learn_count} &nbsp;  {LOCALS[Learn]} <br> 
                {review_count}  &nbsp;   {LOCALS[Review]}  
                </div>


            </div>


        </div>


        



    </div>



<!--------------------END ROW 3----------------------------->




    <div class='row align-items-center full stats'  style="background-color:{BROWSER[total-wedgit-bg]} ">
              <div class="col col-2">
             
                        <svg width="3em" height="3em" viewBox="0 0 16 16" class="bi bi-pie-chart-fill" fill="{BROWSER[wedgits-font-color]}" xmlns="http://www.w3.org/2000/svg">
                        <path d="M15.985 8.5H8.207l-5.5 5.5a8 8 0 0 0 13.277-5.5zM2 13.292A8 8 0 0 1 7.5.015v7.778l-5.5 5.5zM8.5.015V7.5h7.485A8.001 8.001 0 0 0 8.5.015z"/>
                        </svg>
                    </div>
                    <div class="col col-10">
                    {total_cards} <br>  {LOCALS[Total]}
                    </div>
           

    </div>

    <div id="hm">
    </div>

    </div></div>
    """.format( str(ngettext("%s <br>  {LOCALS[minute]} ".format( LOCALS=LOCALS), "%s <br>  {LOCALS[minutes]}".format( LOCALS=LOCALS), minutes) % (minutes)),
        old_stats=_old(self), speed=speed,
        new_count=new,due_count=lrn+due,learn_count=lrn,review_count=due,
        total_cards=totalDisplay,BROWSER=BROWSER , LOCALS=LOCALS , base=base)
    
  
    return buf



def renderDeckTree(self, top: DeckTreeNode,_old) -> str:
        buf = ""
        buf += self._topLevelDragRow()

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

    buf = "<tr class='deck-row row align-items-center  %s' id='%d'>" % (klass, node.deck_id)
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
    buf += """<td class="col col-1" style="padding-left:15px;">
          <img src="%s/user_files/assets/deck_icons/%s.png" onerror="this.src='%s/user_files/assets/deck_icons/default.png'" alt="" class="circle"></td>

    <td  class='col col-8 decktd ' >%s%s<a class="align-middle deck padding %s"
    href=# onclick="return pycmd('open:%d')">%s</a></td>""" % (
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
            klass = "count zero-count"
        return f'<td class="col col-1 "><span class="{klass}">{cnt}</span></td>'

    buf += " %s %s" % (
        nonzeroColour(due, "count review-count"),
        nonzeroColour(node.new_count, "count new-count"),
    )
    # options
    buf += (
        "<td  class='opts col col-1'><a onclick='return pycmd(\"opts:%d\");'>".format(THEME=THEME) % node.deck_id
    )
    buf+= """
    <svg width="1em" height="1em" viewBox="0 0 16 16" class="bi bi-gear-fill" fill="{THEME[gear-icon-color]}" xmlns="http://www.w3.org/2000/svg">
    <path fill-rule="evenodd" d="M9.405 1.05c-.413-1.4-2.397-1.4-2.81 0l-.1.34a1.464 1.464 0 0 1-2.105.872l-.31-.17c-1.283-.698-2.686.705-1.987 1.987l.169.311c.446.82.023 1.841-.872 2.105l-.34.1c-1.4.413-1.4 2.397 0 2.81l.34.1a1.464 1.464 0 0 1 .872 2.105l-.17.31c-.698 1.283.705 2.686 1.987 1.987l.311-.169a1.464 1.464 0 0 1 2.105.872l.1.34c.413 1.4 2.397 1.4 2.81 0l.1-.34a1.464 1.464 0 0 1 2.105-.872l.31.17c1.283.698 2.686-.705 1.987-1.987l-.169-.311a1.464 1.464 0 0 1 .872-2.105l.34-.1c1.4-.413 1.4-2.397 0-2.81l-.34-.1a1.464 1.464 0 0 1-.872-2.105l.17-.31c.698-1.283-.705-2.686-1.987-1.987l-.311.169a1.464 1.464 0 0 1-2.105-.872l-.1-.34zM8 10.93a2.929 2.929 0 1 0 0-5.86 2.929 2.929 0 0 0 0 5.858z"/>
    </svg>
    </a></td></tr>
    """.format(THEME=THEME)
    # children
    if not node.collapsed:
        for child in node.children:
            buf += self._render_deck_node(child, ctx)
    return buf


sharedIcon = """
<img src="{base}/user_files/assets/icons/deck browser icons/get shared.svg" style="margin-top: -5px; margin-right:5px">
""".format(base=base)

creatDeckIcon ="""
<img src="{base}/user_files/assets/icons/deck browser icons/create deck.svg" style="margin-top: -5px; margin-right:5px">
""".format(base=base)

importFileIcon = """
<img src="{base}/user_files/assets/icons/deck browser icons/import file.svg" style="margin-top: -5px; margin-right:5px">
""".format(base=base)

DeckBrowser.drawLinks = [
        ["", "shared", _("{sharedIcon} Get Shared ".format(sharedIcon=sharedIcon))],
        ["", "create", _("{creatDeckIcon}Create Deck".format(creatDeckIcon=creatDeckIcon))],
        ["Ctrl+I", "import", _("{importFileIcon} Import File".format(importFileIcon=importFileIcon))], 
    ]

def drawButtons(self,_old):
    buf = """<style> 
    
    #outer{{
  background-color: {THEME[bottombar-color]} ;
  background-image:unset !important;
    }}
     </style>""".format(THEME=THEME)
    drawLinks = deepcopy(self.drawLinks)
    for b in drawLinks:
        if b[0]:
            b[0] = _("Shortcut key: %s") % shortcut(b[0])
        buf += """
<button type="button" class='btn btn-sm' style="background:{THEME[buttons-color]}; color:{THEME[buttons-label-color]} " title='%s' onclick='pycmd(\"%s\");'> %s </button>""".format(THEME=THEME) %  tuple(
            b
        )
    self.bottom.draw(
        
        buf=buf,
        link_handler=self._linkHandler,
        web_context=DeckBrowserBottomBar(self),
    )





Toolbar. _body = """
<nav style="font-size:12px ; text-align:{THEME[topbar-position]};background-color:{THEME[topbar-color]}"  width=100%%>
<tr>
<td class=tdcenter'>%s</td>
</tr></nav>
""".format(THEME=THEME)

animation = ""
if bg_animation :
    animation = """
    <script>
    
    </script>
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
        background-image: url('%s/user_files/assets/background.jpg') !important ; 
        background-size :cover !important;

    }
    </style>
    """%(base)


heatmapStyle=""
if THEME["heatmap-background"]:
    heatmapStyle="""
        .rh-container{{
            background-color: {THEME[large-areas-color]};
            width:96.5%%;
            min-width: max-content;
            text-align: center;
            box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);


        }}
        .streak{{
            background-color: {THEME[large-areas-color]};
            padding:10px;
        }}
     """.format(THEME=THEME)
     
if HEATMAP_POSITION == "right":
    heatmap_script = """
<script>
window.addEventListener('load', 
  function() {{
    child = document.querySelector(".rh-container")
    //.classList.add({HEATMAP_WIDTH});
    parent = document.querySelector("#hm")
    parent.appendChild(child);

  }}, false);

</script>
    """
else:
    heatmap_script =""


main_bg = """

.deck-row{{
    border-bottom: 1px solid {THEME[decks-border-color]} 

}}

.decks-container{{
background-color:{THEME[large-areas-color]} ;
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);

}}

a.deck , .collapseable{{
    color: {THEME[decks-font-color]};
}}

.collapseable{{
     color: {THEME[decks-font-color]} !important;
}}

.filtered{{
    color: {THEME[filtered-deck-color]} !important;;
}}

@font-face {{
    font-family: '{THEME[decks-font-family]}';
    src: url('{base}/user_files/assets/fonts/{THEME[decks-font-src]}');   
}}

@font-face {{
    font-family: '{BROWSER[wedgits-font-family]}';
    src: url('{base}/user_files/assets/fonts/{BROWSER[wedgits-font-src]}');   
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

{heatmapStyle}

""".format(THEME=THEME,BROWSER=BROWSER, base=base , heatmapStyle=heatmapStyle)


DeckBrowser._body = """
<style>
{main_bg}

</style>

<div class="overlay" style="background : linear-gradient(20deg,{THEME[overlay-color1]}, {THEME[overlay-color2]}) ;" >
{animation}
<center class="container">
<div class=row>
<div class="col col-12 col-md-7 {TABLE_WIDTH}">
<table class="container decks-container">
%(tree)s
</table>
</div>
<div class="col col-12 col-md-5 {STATS_WIDTH}" style="color:{BROWSER[wedgits-font-color]}">
%(stats)s


</div>
</center>
</div>

{heatmap_script}


""".format(animation=animation,THEME=THEME,main_bg=main_bg,BROWSER=BROWSER,TABLE_WIDTH=TABLE_WIDTH,STATS_WIDTH=STATS_WIDTH,HEATMAP_WIDTH=HEATMAP_WIDTH,heatmap_script=heatmap_script)

def updateRenderingMethods():   

    DeckBrowser._renderDeckTree = wrap(DeckBrowser._renderDeckTree , renderDeckTree, "around")
    DeckBrowser._render_deck_node = wrap(DeckBrowser._render_deck_node, render_deck_node, 'around')
    DeckBrowser._drawButtons = wrap(DeckBrowser._drawButtons, drawButtons, 'around')
    DeckBrowser._renderStats = wrap(DeckBrowser._renderStats, renderStats, 'around')
    
    
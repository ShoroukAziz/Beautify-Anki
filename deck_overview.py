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

from typing import Optional, Any

from anki.errors import DeckRenameError
from anki.hooks import wrap
import anki.sched
import anki.schedv2
from anki.schedv2 import Scheduler
from aqt import mw
from aqt.overview import Overview, OverviewContent, OverviewBottomBar
from aqt.toolbar import Toolbar, BottomBar
from aqt import AnkiQt, gui_hooks
from aqt.utils import shortcut
import aqt

import json
import os
import time
from datetime import date, timedelta
import math
from aqt.utils import showInfo


from copy import deepcopy
from .config import *


def desc(self, deck, _old):
    button = mw.button
    desc = ""

    if( deck.get("desc", "")!=""):
        desc += "<div class='deck-desc'  style='background-color:{THEME[large-areas-color]}'>".format(THEME=THEME)
        desc += deck.get("desc", "")
        desc += """
        </div>"""


    counts = list(self.mw.col.sched.counts())
    finished = not sum(counts)
    if finished:
        finish_msg = u'''
      <div > {:s}</div>
    '''.format(self.mw.col.sched.finishedMsg())
        btn = ""
        desc += finish_msg
    else:
        finish_msg = ""
        btn = u'''      
            {button:s} 
            '''.format(button=button('study', _('<img style=\"margin-top: -5px; margin-right:5px\" src=\"{base}/user_files/assets/icons/deck overview icons/study now.svg\" > Study Now'.format(base=base)), id='study', class_='btn btn-lg', extra='style=\'background:{THEME[buttons-color]};color:{THEME[buttons-label-color]};\''.format(THEME=THEME)))
    if deck["dyn"]:
        desc += """
<div class='card-panel animate__animated animate__fadeInUp animate__slow amber amber lighten-4'>This is a special deck for studying outside of the normal schedule.
Cards will be automatically returned to their original decks after you review 
them.Deleting this deck from the deck list will return all remaining cards 
to their original deck.</div>"""+btn

    else:
        desc+="""
        <br>
        <br>
        <div>
        {}
        </div>
        """.format(btn)
    if not desc:
        return "<p>"
    if deck["dyn"]:
        dyn = "dyn"
    else:
        dyn = ""
    return '<div class=" %s">%s</div>' % (dyn, desc)

#####################################################################################################################

def table(self):
    current_deck_name = self.mw.col.decks.current()['name']

    try:
        learn_per_day = self.mw.col.decks.confForDid(
            self.mw.col.decks.current()['id'])['new']['perDay']
    except:
        learn_per_day = 0

    correction_for_notes = 1
    count_label = LOCALS["Cards"]
    last_match_length = 0

    if 'note_correction_factors' in CONFIG:
        for fragment, factor in CONFIG['note_correction_factors'].items():
            if current_deck_name.startswith(fragment):
                if len(fragment) > last_match_length:
                    correction_for_notes = int(factor)
                    count_label = LOCALS["Notes"]
                    last_match_length = len(fragment)

        # prevent division by zero and negative results
        if correction_for_notes <= 0:
            correction_for_notes = 1

    if 'date_format' in CONFIG:
        if CONFIG['date_format'].strip().lower() == 'us':
            date_format = "%m/%d/%Y"
        elif CONFIG['date_format'].strip().lower() == 'asia':
            date_format = "%Y/%m/%d"
        elif CONFIG['date_format'].strip().lower() == 'eu':
            date_format = "%d.%m.%Y"
        else:
            date_format = CONFIG['date_format']
    else:
        date_format = "%d.%m.%Y"

    total, mature, young, unseen, suspended, due = self.mw.col.db.first(
        u'''
      select
      -- total
      count(id),
      -- mature
      sum(case when queue = 2 and ivl >= 21
           then 1 else 0 end),
      -- young / learning
      sum(case when queue in (1, 3) or (queue = 2 and ivl < 21)
           then 1 else 0 end),
      -- unseen
      sum(case when queue = 0
           then 1 else 0 end),
      -- suspended
      sum(case when queue < 0
           then 1 else 0 end),
      -- due
      sum(case when queue = 1 and due <= ?
           then 1 else 0 end)
      from cards where did in {:s}
    '''.format(self.mw.col.sched._deckLimit()),
        round(time.time()))

    if not total:
        return u'<p>No cards found.</p>'

    scheduled_counts = list(self.mw.col.sched.counts())
    cards = {}

    cards['mature'] = mature // int(correction_for_notes)
    cards['young'] = young // int(correction_for_notes)
    cards['unseen'] = unseen // int(correction_for_notes)
    cards['suspended'] = suspended // int(correction_for_notes)
    cards['total'] = total // int(correction_for_notes)
    cards['new'] = scheduled_counts[0]
    cards['learning'] = scheduled_counts[1]
    cards['review'] = scheduled_counts[2]
    cards['todo'] = cards['new'] + cards['learning'] + cards['review']
    cards['count_label'] = count_label

    try:
        daysUntilDone = math.ceil(cards['unseen'] / learn_per_day)
    except:
        daysUntilDone = 0

    try:
        cards['doneDate'] = (
            date.today()+timedelta(days=daysUntilDone)).strftime(date_format)
    except:
        showInfo("Unsupported date format. Defaulting to Day.Month.Year instead. Use one of the shorthands: \"us\", \"asia\" or \"eu\", or specify the date like \"\%d.\%m.\%Y\", \"\%m/\%d/\%Y\" etc.\n For more information check the table at: https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior", type="warning", title="More Overview Stats 2.1 Warning")
        cards['doneDate'] = (
            date.today()+timedelta(days=daysUntilDone)).strftime("%d.%m.%Y")

    cards['daysLeft'] = daysUntilDone

    if(daysUntilDone == 1):
        cards['daysLeft'] = '{} {LOCALS[day]}'.format(daysUntilDone,LOCALS=LOCALS)
    else:
        cards['daysLeft'] = '{} {LOCALS[days]}'.format(daysUntilDone,LOCALS=LOCALS)

 ####################### Writing Output HTML ########################## 

    output = u'''
    <!-----------END Break subtitles script--------------->

 
    <!------------------ plotly script------------------>
    <script type="text/javascript">

        window.onload = function () {{
            var data = [{{
        type: "pie",
        hole: .5,
        automargin: true,
        values: [{cards[mature]:d}, {cards[young]:d}, {cards[unseen]:d},  {cards[suspended]:d}],
        labels: ["{LOCALS[Mature]}", "{LOCALS[Young]}", "{LOCALS[Unseen]}", "{LOCALS[Suspended]}"],
        marker: {{
        colors:["#2e7d32","#85dd95","#707070","#941b1b"]

        }},
        textinfo: "label+percent",
        insidetextorientation: "radial",
        textfont :{{
            color:"{PIE[wedgits-font-color]}"
        }}
        }}]

        var layout = {{
        showlegend: true,
        height: 387,
        width: 350,
        paper_bgcolor:"{THEME[large-areas-color]}",
        margin: {{"t": 0, "b": 0, "l": 0, "r": 0}},
            legend: {{"orientation": "h" ,
            font: {{
                "color": "{PIE[wedgits-font-color]}"
            }}
            
            }}  
        }};
        
        Plotly.newPlot('myDiv', data, layout);
        }}

    </script>
    <!------------------END  plotly script------------------>

    <div class='row '>
        <!-----------------------------stats Widgets ------------------------------>
        <div class='col col-sm-12 col-lg-6 text-center'>

            <div class='row'">

                <div class= 'col col-sm-6 widget widget-top' style="background-color:{OVERVIEW[total-notes-wedgit-bg]} ">
                    <span class='number'> {cards[total]:d}<br> </span>  {LOCALS[Total]} {cards[count_label]}
                </div>

                <div class= 'col col-sm-6 widget widget-top' style="background-color: {OVERVIEW[remaining-wedgit-bg]} ">
                        <svg width="2.3em" height="2.3em" viewBox="0 0 16 16" class="bi bi-stopwatch-fill" fill="{OVERVIEW[wedgits-font-color]} " xmlns="http://www.w3.org/2000/svg">
                    <path fill-rule="evenodd" d="M5.5.5A.5.5 0 0 1 6 0h4a.5.5 0 0 1 0 1H9v1.07A7.002 7.002 0 0 1 8 16 7 7 0 0 1 7 2.07V1H6a.5.5 0 0 1-.5-.5zm3 4.5a.5.5 0 0 0-1 0v3.5h-3a.5.5 0 0 0 0 1H8a.5.5 0 0 0 .5-.5V5z"/>
                    </svg><br>
                        {LOCALS[Done in]}
                        {cards[daysLeft]:s} {cards[doneDate]:s} 
                </div>
            </div>

            <!-------------------------END ROW 1 --------------------------------->
            
            <div class='row'>
                <div class='widget  col col-sm-6 d-flex align-items-center justify-content-center'  style="background-color:{OVERVIEW[new-wedgit-bg]}  ">
                    <div>
                     <svg width="2.3em" height="2.3em" viewBox="0 0 16 16" class="bi bi-layers-fill" fill="{OVERVIEW[wedgits-font-color]} " xmlns="http://www.w3.org/2000/svg">
                    <path fill-rule="evenodd" d="M7.765 1.559a.5.5 0 0 1 .47 0l7.5 4a.5.5 0 0 1 0 .882l-7.5 4a.5.5 0 0 1-.47 0l-7.5-4a.5.5 0 0 1 0-.882l7.5-4z"/>
                    <path fill-rule="evenodd" d="M2.125 8.567l-1.86.992a.5.5 0 0 0 0 .882l7.5 4a.5.5 0 0 0 .47 0l7.5-4a.5.5 0 0 0 0-.882l-1.86-.992-5.17 2.756a1.5 1.5 0 0 1-1.41 0l.418-.785-.419.785-5.169-2.756z"/>
                    </svg>                      
                    <div class='number'>
                        {cards[new]:d}
                    </div>
                    {LOCALS[New]} 
                    </div>
                </div>

                <div class='widget  col col-sm-6 d-flex align-items-center justify-content-center'  style="background-color:{OVERVIEW[learning-wedgit-bg]}">
                    <div>
                    <svg width="2.3em" height="2.3em" viewBox="0 0 16 16" class="bi bi-book-half" fill="{OVERVIEW[wedgits-font-color]} " xmlns="http://www.w3.org/2000/svg">
                    <path fill-rule="evenodd" d="M12.786 1.072C11.188.752 9.084.71 7.646 2.146A.5.5 0 0 0 7.5 2.5v11a.5.5 0 0 0 .854.354c.843-.844 2.115-1.059 3.47-.92 1.344.14 2.66.617 3.452 1.013A.5.5 0 0 0 16 13.5v-11a.5.5 0 0 0-.276-.447L15.5 2.5l.224-.447-.002-.001-.004-.002-.013-.006-.047-.023a12.582 12.582 0 0 0-.799-.34 12.96 12.96 0 0 0-2.073-.609zM15 2.82v9.908c-.846-.343-1.944-.672-3.074-.788-1.143-.118-2.387-.023-3.426.56V2.718c1.063-.929 2.631-.956 4.09-.664A11.956 11.956 0 0 1 15 2.82z"/>
                    <path fill-rule="evenodd" d="M3.214 1.072C4.813.752 6.916.71 8.354 2.146A.5.5 0 0 1 8.5 2.5v11a.5.5 0 0 1-.854.354c-.843-.844-2.115-1.059-3.47-.92-1.344.14-2.66.617-3.452 1.013A.5.5 0 0 1 0 13.5v-11a.5.5 0 0 1 .276-.447L.5 2.5l-.224-.447.002-.001.004-.002.013-.006a5.017 5.017 0 0 1 .22-.103 12.958 12.958 0 0 1 2.7-.869z"/>
                    </svg>
                    
                    <div class='number'>
                        {cards[learning]:d}
                    </div>
                    {LOCALS[Learning]} 
                    </div>
                </div>
            </div>

            <!-------------------------END ROW 2 --------------------------------->

            <div class='row'>

                <div class='widget  col col-sm-6 d-flex align-items-center justify-content-center'  style="background-color: {OVERVIEW[review-wedgit-bg]} ">
                        <div>
                         <svg width="2.3em" height="2.3em" viewBox="0 0 16 16" class="bi bi-pencil-square" fill="{OVERVIEW[wedgits-font-color]} " xmlns="http://www.w3.org/2000/svg">
                        <path d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456l-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z"/>
                        <path fill-rule="evenodd" d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5v11z"/>
                        </svg>
                        <div class='number'>
                            {cards[review]:d}
                        </div>
                        {LOCALS[Review]} 
                        </div>
        
                </div>

                <div class='widget  col col-sm-6 d-flex align-items-center justify-content-center'  style="background-color: {OVERVIEW[total-wedgit-bg]}  ">
                    <div>
                         <svg width="2.3em" height="2.3em" viewBox="0 0 16 16" class="bi bi-pie-chart-fill" fill="{OVERVIEW[wedgits-font-color]} " xmlns="http://www.w3.org/2000/svg">
                        <path d="M15.985 8.5H8.207l-5.5 5.5a8 8 0 0 0 13.277-5.5zM2 13.292A8 8 0 0 1 7.5.015v7.778l-5.5 5.5zM8.5.015V7.5h7.485A8.001 8.001 0 0 0 8.5.015z"/>
                        </svg>                    <div class='number'>
                            {cards[todo]:d}
                    </div>
                    {LOCALS[Total]} 
                    </div>
                </div>
            </div>
            <!-------------------------END ROW 3 --------------------------------->

            
        </div>  

        <!------------------- End widgets ------------------------------>

        <!---------------- the pie chart ------------------------------->
        <div id='myDiv' class='col col-sm-12 col-lg-6'  style="padding:2% ">

        </div> 
        <!---------------- END pie chart ------------------------------->


    </div>

  '''.format(cards=cards, OVERVIEW=OVERVIEW , THEME=THEME , PIE=PIE , LOCALS=LOCALS)

    return output
#####################################################################################################################


def renderPage(self,_old):
    but = self.mw.button
    deck = self.mw.col.decks.current()
    self.sid = deck.get("sharedFrom")
    if self.sid:
        self.sidVer = deck.get("ver", None)
        shareLink = '<a class=smallLink href="review">Reviews and Updates</a>'
    else:
        shareLink = ""
    if "::"in deck["name"]:
        sub = deck["name"].replace("::"," .. ")
    if "'" in deck["name"]:
        sub = deck["name"].replace("'","’")
        
    else:
        sub = deck["name"]
    content = OverviewContent(
        deck=sub,
        shareLink=shareLink,
        desc=self._desc(deck),
        table=self._table(),
    )
    gui_hooks.overview_will_render_content(self, content)
    self.web.stdHtml(
        self._body % content.__dict__,
        css=["overview.css"],
        js=["jquery.js", "overview.js"],
        context=self,
    )


####################################################################################################################3
heatmapStyle=""
if THEME["heatmap-background"]:
    heatmapStyle="""
        .rh-container{{
            background-color: {THEME[large-areas-color]};
            box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
            min-width: max-content;
            width:110%%;
            text-align: center;


        }}
        .streak{{
            background-color: {THEME[large-areas-color]};
            padding:10px;
            

        }}
     """.format(THEME=THEME)
     



Overview._body = """
<style>
body{{
     background: linear-gradient(20deg,{THEME[overlay-color1]}, {THEME[overlay-color2]}) fixed, url('{base}/user_files/assets/deck_backgrounds/%(deck)s.jpg'),url('{base}/user_files/assets/background.jpg') ;
     background-size: 100%%;
     }}

@font-face {{
    font-family: '{OVERVIEW[wedgits-font-family]}';
    src: url('{base}/user_files/assets/fonts/{OVERVIEW[wedgits-font-src]}');   
}}

.widget{{
font-size:{OVERVIEW[wedgits-font-size]};
font-family:{OVERVIEW[wedgits-font-family]};
color:{OVERVIEW[wedgits-font-color]};

}}

@font-face {{
    font-family: '{OVERVIEW[deck-name-font-family]}';
    src: url('{base}/user_files/assets/fonts/{OVERVIEW[deck-name-font-src]}');   
}}

h1{{
font-family:{OVERVIEW[deck-name-font-family]};
font-size:{OVERVIEW[deck-name-font-size]}
}}

{heatmapStyle}
</style>
<!----------------------END OF STYLE------------------------------->

<div class='container  grey-text text-darken-4'>

    <div class = 'row align-items-center' >
        <!-------------left side (title and description)------------------------------->
        <div class=' col col-md-4 col-sm-12 text-center'>
        
            <h1 class="animate__animated  animate__delay animate__backInDown">%(deck)s</h1>
            %(shareLink)s
            %(desc)s
        
        </div>
         <div class=' col col-md-1 col-sm-0 right-col'></div>

        <!-------------right side (stats)------------------------------->

        <div class=' col col-md-6 col-sm-12 right-col'>
             %(table)s

        </div>
    </div>
</div>



""".format(THEME=THEME,OVERVIEW=OVERVIEW,base=base,heatmapStyle=heatmapStyle)


#####################################################################################################################

def renderDeckBottom(self, _old):
    links = [
        ["O", "opts", _(            
            "<img src=\"{base}/user_files/assets/icons/deck overview icons/options.svg\" style=\"margin-top: -5px; margin-right:5px\"> Options").format(base=base)],
    ]
    if self.mw.col.decks.current()["dyn"]:
        links.append(
            ["R", "refresh", _( "<img src=\"{base}/user_files/assets/icons/deck overview icons/rebuild.svg\" style=\"margin-top: -5px; margin-right:5px\"> Rebuild").format(base=base)])
        links.append(
            ["E", "empty", _( "<img src=\"{base}/user_files/assets/icons/deck overview icons/empty.svg\" style=\"margin-top: -5px; margin-right:5px\"> Empty").format(base=base)])
    else:
        links.append(["C", "studymore", _(
            "<img src=\"{base}/user_files/assets/icons/deck overview icons/custom study.svg\" style=\"margin-top: -5px; margin-right:5px\"> Custom Study").format(base=base)])
        # links.append(["F", "cram", _("Filter/Cram")])
    if self.mw.col.sched.haveBuried():
        links.append(["U", "unbury", _(
            "<img src=\"{base}/user_files/assets/icons/deck overview icons/unbury.svg\" style=\"margin-top: -5px; margin-right:5px\"> Unbury").format(base=base)])
    buf = """<style> 
    
    #outer{{
     background-color: {THEME[bottombar-color]};
    }}
     </style>""".format(THEME=THEME)
    for b in links:
        if b[0]:
            b[0] = _("Shortcut key: %s") % shortcut(b[0])
        buf += """
<button style="background:{THEME[buttons-color]}; color:{THEME[buttons-label-color]} " class='btn btn-sm' title="%s" onclick='pycmd("%s")'>%s</button>""".format(THEME=THEME) % tuple(
            b
        )

    self.bottom.draw(
        buf=buf, link_handler=self._linkHandler, web_context=OverviewBottomBar(
            self)
    )

#####################################################################################################################


def finishedMsg(self, _old) -> str:
    return (
        "<div class='deck-desc finish-msg animate__animated animate__rubberBand' style='background-color:{THEME[large-areas-color]};'>".format(THEME=THEME)
        + _("Congratulations! You have finished this deck for now.")
        + "<br></div>"
        #+ self._nextDueMsg()
    )


def nextDueMsg(self, _old) -> str:
    line = []

    #learn_msg = self.next_learn_msg()
    #if learn_msg:
    #    line.append(learn_msg)

    # the new line replacements are so we don't break translations
    # in a point release
    if self.revDue():
        line.append(
            _(
                """\
<div class=' animate__animated animate__fadeInUp animate__slow deck-desc' style='background-color:{THEME[large-areas-color]}'>
Today's review limit has been reached, but there are still cards
waiting to be reviewed. For optimum memory, consider increasing
the daily limit in the options.</div>"""
            ).replace("\n", " ").format(THEME=THEME)
        )
    if self.newDue():
        line.append(
            _(
                """\
<div class=' animate__animated animate__fadeInUp animate__slow deck-desc' style='background-color:{THEME[large-areas-color]}'>
There are more new cards available, but the daily limit has been
reached. You can increase the limit in the options, but please
bear in mind that the more new cards you introduce, the higher
your short-term review workload will become.</div>"""
            ).replace("\n", " ").format(THEME=THEME)
        )
    if self.haveBuried():
        if self.haveCustomStudy:
            now = " " + _("To see them now, click the Unbury button below.")
        else:
            now = ""
        line.append(
            _(
                """\
<div class=' animate__animated animate__fadeInUp animate__slow deck-desc lighten-4' style='background-color:{THEME[large-areas-color]}'>
Some related or buried cards were delayed until a later session.</div>""".format(THEME=THEME)
            )
            + now
        )
    if self.haveCustomStudy and not self.col.decks.current()["dyn"]:
        line.append(
            _(
                """\
<div class=' animate__animated animate__fadeInUp animate__slow deck-desc lighten-4' style='background-color:{THEME[large-areas-color]}'>
 To study outside of the normal schedule, click the Custom Study button below.</div>""".format(THEME=THEME)
            )
            )
        
    return "".join(line)


#####################################################################################################################

def updateRenderingDeckOverview():

    Overview._desc = wrap(Overview._desc, desc, "around")
    Overview._renderPage = wrap(Overview._renderPage, renderPage, "around")
    Overview._table = table
    Overview._renderBottom = wrap(
        Overview._renderBottom, renderDeckBottom, "around")

    Scheduler._nextDueMsg = wrap(Scheduler._nextDueMsg, nextDueMsg, "around")
    Scheduler.finishedMsg = wrap(Scheduler.finishedMsg, finishedMsg, "around")

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
from .helpers import *
from .config import *


def desc(self, deck, _old):
    button = mw.button
    desc = ""

    counts = list(self.mw.col.sched.counts())
    finished = not sum(counts)
    if finished:
        finish_msg = u'''
      <div style="white-space: pre-wrap;"> {:s}</div>
    '''.format(self.mw.col.sched.finishedMsg())
        btn = ""
        desc = finish_msg
    else:
        finish_msg = ""
        btn = u'''      
            {button:s} 
            '''.format(button=button('study', _('<i class=\"  material-icons right\">exit_to_app</i>  Study Now'), id='study', class_='waves-effect waves-light {MAIN[bg-color]} btn-large'.format(MAIN=MAIN)))

    if deck["dyn"]:
        desc += """
<div class='card-panel animate__animated animate__fadeInUp animate__slow amber amber lighten-4'>This is a special deck for studying outside of the normal schedule.
Cards will be automatically returned to their original decks after you review 
them.Deleting this deck from the deck list will return all remaining cards 
to their original deck.</div>"""

    else:
        desc += "<div class=''>"
        desc += deck.get("desc", "")
        desc += """
        </div>
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


bg_path = "assets/deck_backgrounds/"+"%(deck)s.jpg"
background_style = "body{ background-image:linear-gradient(311deg,#9E9E9E, #033155cc), url('" + \
    bg_path + "') ,url('assets/background.jpg');background-size:100%% }"


def table(self):
    current_deck_name = self.mw.col.decks.current()['name']

    try:
        learn_per_day = self.mw.col.decks.confForDid(
            self.mw.col.decks.current()['id'])['new']['perDay']
    except:
        learn_per_day = 0

    correction_for_notes = 1
    count_label = "Cards"
    last_match_length = 0

    if 'note_correction_factors' in CONFIG['MAIN']:
        for fragment, factor in CONFIG['MAIN']['note_correction_factors'].items():
            if current_deck_name.startswith(fragment):
                if len(fragment) > last_match_length:
                    correction_for_notes = int(factor)
                    count_label = "Notes"
                    last_match_length = len(fragment)

        # prevent division by zero and negative results
        if correction_for_notes <= 0:
            correction_for_notes = 1

    if 'date_format' in CONFIG['MAIN']:
        if CONFIG['MAIN']['date_format'].strip().lower() == 'us':
            date_format = "%m/%d/%Y"
        elif CONFIG['MAIN']['date_format'].strip().lower() == 'asia':
            date_format = "%Y/%m/%d"
        elif CONFIG['MAIN']['date_format'].strip().lower() == 'eu':
            date_format = "%d.%m.%Y"
        else:
            date_format = CONFIG['MAIN']['date_format']
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
        cards['daysLeft'] = '{} day'.format(daysUntilDone)
    else:
        cards['daysLeft'] = '{} days'.format(daysUntilDone)

    output = u'''
    <div class="conatiner" ><div class='row'>

<script type="text/javascript">

window.onload = function () {{
    var data = [{{
  type: "pie",
  hole: .5,
  automargin: true,
  values: [{cards[mature]:d}, {cards[young]:d}, {cards[unseen]:d},  {cards[suspended]:d}],
  labels: ["Mature", "Young", "Unseen", "Suspended"],
  marker: {{
  colors:["#2e7d32","#a5d6a7","#424242","#dd2c00"]

  }},
  textinfo: "label+percent",
  insidetextorientation: "radial"
}}]

var layout = {{
  showlegend: true,
  height: 387,
  width: 350,
  margin: {{"t": 0, "b": 0, "l": 0, "r": 0}},
	legend: {{"orientation": "h"  }}  
  }};
 
Plotly.newPlot('myDiv', data, layout);
}}

</script>

  <div class='col s6 '>
  
    <div class='row'>

      <div class= 'col s6 {DECKSTATS[label-bg1]} {DECKSTATS[labels-color]} top'>
      
      <span class='number'> {cards[total]:d}<br> </span> Total {cards[count_label]}
      </div>

      <div class='top {DECKSTATS[label-bg2]} {DECKSTATS[labels-color]} col s6 flex'>
      <i class=" material-icons">{DECKSTATS[icon2]}</i>
      done in 
      {cards[daysLeft]:s} {cards[doneDate]:s} 
      </div>

      <div class='number-container {DECKSTATS[label-bg3]} {DECKSTATS[labels-color]} col s6 '>
      <div class='number'>
      <i class=" material-icons">{DECKSTATS[icon3]}</i><br>
      {cards[new]:d}
      </div>
      New 
      </div>

      <div class='number-container {DECKSTATS[label-bg4]} {DECKSTATS[labels-color]} col s6 '>
      <div class='number'>
        <i class=" material-icons">{DECKSTATS[icon4]}</i><br>
      {cards[learning]:d}
      </div>
      Learning
      </div>

      <div class='number-container  {DECKSTATS[label-bg5]} {DECKSTATS[labels-color]} col s6 '>
      <div class='number'>
      <i class=" material-icons">{DECKSTATS[icon5]}</i><br>
      {cards[review]:d}
      </div>
      Review      
      </div>

      <div class='number-container  {DECKSTATS[label-bg6]} {DECKSTATS[labels-color]} col s6 '>
      <div class='number'>
      <i class=" material-icons">{DECKSTATS[icon6]}</i><br>
      {cards[todo]:d}
      </div>
      Total      
      </div>




      </div>
  

</div>  

    <div id='myDiv' class='col s6'  style="height:387px;width: 50%; ">

  </div> 

  </div>

  '''.format(cards=cards, DECKSTATS=DECKSTATS)

    return output


Overview._body = """
<style>
{}
</style>
<center class='container  grey-text text-darken-4'>
<div class = 'row flex' >
<div class=' col s5 '>
<div class='container'>
<h1 class="animate__animated  animate__delay animate__backInDown">%(deck)s</h1>
%(shareLink)s
%(desc)s
</div>
</div>
<div class=' col s7 right-col'>
%(table)s

</div>
</div>

</center>



""".format(background_style,)


def renderDeckBottom(self, _old):
    links = [
        ["O", "opts", _(
            "<i class=\" material-icons left\">settings_applications</i> Options")],
    ]
    if self.mw.col.decks.current()["dyn"]:
        links.append(
            ["R", "refresh", _("<i class=\" material-icons left\">build</i> Rebuild")])
        links.append(
            ["E", "empty", _("<i class=\" material-icons left\">delete</i> Empty")])
    else:
        links.append(["C", "studymore", _(
            "<i class=\" material-icons left\">event</i>Custom Study")])
        # links.append(["F", "cram", _("Filter/Cram")])
    if self.mw.col.sched.haveBuried():
        links.append(["U", "unbury", _(
            "<i class=\" material-icons left\">do_not_disturb_off</i>Unbury")])
    buf = ""
    for b in links:
        if b[0]:
            b[0] = _("Shortcut key: %s") % shortcut(b[0])
        buf += """
<button class='{MAIN[bg-color]} btn-small' title="%s" onclick='pycmd("%s")'>%s</button>""".format(MAIN=MAIN) % tuple(
            b
        )

    self.bottom.draw(
        buf=buf, link_handler=self._linkHandler, web_context=OverviewBottomBar(
            self)
    )

#####################################################################################################################


def finishedMsg(self, _old) -> str:
    return (
        "<div class='finish-msg animate__animated animate__rubberBand amber card-panel'>"
        + _("Congratulations! You have finished this deck for now.")
        + "<br></div>"
        + self._nextDueMsg()
    )


def nextDueMsg(self, _old) -> str:
    line = []

    learn_msg = self.next_learn_msg()
    if learn_msg:
        line.append(learn_msg)

    # the new line replacements are so we don't break translations
    # in a point release
    if self.revDue():
        line.append(
            _(
                """\
<div class='card-panel animate__animated animate__fadeInUp animate__slow amber amber lighten-4'>
Today's review limit has been reached, but there are still cards
waiting to be reviewed. For optimum memory, consider increasing
the daily limit in the options.</div>"""
            ).replace("\n", " ")
        )
    if self.newDue():
        line.append(
            _(
                """\
<div class='card-panel animate__animated animate__fadeInUp animate__slow amber amber lighten-4'>
There are more new cards available, but the daily limit has been
reached. You can increase the limit in the options, but please
bear in mind that the more new cards you introduce, the higher
your short-term review workload will become.</div>"""
            ).replace("\n", " ")
        )
    if self.haveBuried():
        if self.haveCustomStudy:
            now = " " + _("To see them now, click the Unbury button below.")
        else:
            now = ""
        line.append(
            _(
                """\
<div class='card-panel animate__animated animate__fadeInUp animate__slow amber amber lighten-4'>
Some related or buried cards were delayed until a later session.</div>"""
            )
            + now
        )
    if self.haveCustomStudy and not self.col.decks.current()["dyn"]:
        line.append(
            _(
                """\
<div class='card-panel animate__animated animate__fadeInUp animate__slow amber amber lighten-4'>
 To study outside of the normal schedule, click the Custom Study button below.</div>"""
            )
        )
    return "".join(line)


#####################################################################################################################

def updateRenderingDeckOverview():

    Overview._desc = wrap(Overview._desc, desc)
    Overview._table = table
    Overview._renderBottom = wrap(Overview._renderBottom, renderDeckBottom)

    Scheduler._nextDueMsg = wrap(Scheduler._nextDueMsg, nextDueMsg)
    Scheduler.finishedMsg = wrap(Scheduler.finishedMsg, finishedMsg)

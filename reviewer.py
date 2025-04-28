# -*- coding: utf-8 -*-
"""
Beautify Anki
an Addon for Anki
Github (https://github.com/my-Anki/Beautify-Anki)
Copyright (c) 2020 Shorouk Abdelaziz (https://shorouk.dev)

updated and upgraded by mizmu addons (c) 2023
new icons: google fonts

Further maintained by Yakaru and the community
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
from typing import Optional

from anki.hooks import wrap
from aqt import gui_hooks
from aqt.reviewer import Reviewer
from aqt.toolbar import BottomBar
from aqt.utils import *
import json
from anki.scheduler.v3 import Scheduler as V3Scheduler

from .config import *


reviewer_style = """<style> 
    
    body{{
  background-color: {THEME[bottombar-color]} ;
  background-image:unset !important;
    }}
    
      td{{
    /* text-align: center !important; */
    background-color:  {THEME[bottombar-color]};
  }}

    td[align="center"]{{
    padding-top: 10px; !important;
  }}
      td[align="start"]{{
    padding-top: 25px !important;
  }}
    button{{
        bottom: -3px !important;
  }}
     </style>""".format(THEME=THEME)


def bottomHTML(self):
    return """
<center id=outer>
<table id=innertable width=100%% cellspacing=0 cellpadding=0>
<tr>
<td align=start valign=top class=stat>
<button style="color: {THEME[buttons-label-color]}; background-color:{THEME[buttons-color]} "  class='btn btn-sm'
title="%(editkey)s" onclick="pycmd('edit');">%(edit)s</button></td>
<td align=center valign=top id=middle>
</td>
<td align=end valign=top class=stat>
</span><br>
<button style="color: {THEME[buttons-label-color]} ; background-color:{THEME[buttons-color]} "class=' btn btn-sm'
 title="%(morekey)s" onclick="pycmd('more');">%(more)s %(downArrow)s
 <span id=time class=stattxt></span>
</button>
</td>
</tr>
</table>
</center>
<script>
time = %(time)d;
</script>
""".format(THEME=THEME) % dict(
        edit=tr.studying_edit(),
        editkey=tr.actions_shortcut_key(val="E"),
        more=tr.studying_more(),
        morekey=tr.actions_shortcut_key(val="M"),
        downArrow=downArrow(),
        time=self.card.time_taken() // 1000,
    )


def showAnswerButton(self) -> None:
        middle = """
<button style='color: {THEME[buttons-label-color]} ;background-color:{THEME[buttons-color]}' title="{shortcut_key}" id="ansbut" onclick='pycmd("ans");'>{show_answer}<span class=stattxt>{remaining}</span></button>""".format(
            THEME=THEME,
            shortcut_key=tr.actions_shortcut_key(val=tr.studying_space()),
            show_answer=tr.studying_show_answer(),
            remaining=self._remaining(),
        )
        # wrap it in a table so it has the same top margin as the ease buttons
        middle = (
            "<table cellpadding=0><tr><td class=stat2 align=center>%s</td></tr></table>"
            % middle
        )
        if self.card.should_show_timer():
            maxTime = self.card.time_limit() / 1000
        else:
            maxTime = 0
        self.bottom.web.eval("showQuestion(%s,%d);" % (json.dumps(middle), maxTime))
        self.bottom.web.adjustHeightToFit()
        self.bottom.web.eval(
            f"""$('head').append(`{reviewer_style}`);"""
        )

    # def adjust_bottom_height(c):
        def _onHeight(qvar: Optional[int]) -> None:
            from aqt import mw

            # if qvar is None:
            #     mw.progress.single_shot(1000, mw.reset)
            #     return
            #
            self.bottom.web.setFixedHeight(int(qvar + 10))

        self.bottom.web.evalWithCallback("document.documentElement.offsetHeight", _onHeight)


# gui_hooks.reviewer_did_show_question.append(adjust_bottom_height)

def answerButtons(self):
    default = self._defaultEase()

    if v3 := self._v3:
        assert isinstance(self.mw.col.sched, V3Scheduler)
        labels = self.mw.col.sched.describe_next_states(v3.states)
    else:
        labels = None

    def but(i, label):
        if i == default:
            extra = "id=defease"
        else:
            extra = ""
        due = self._buttonTime(i, v3_labels=labels)

        return """
<td align=center><button class='btn btn-sm ' %s title="%s" data-ease="%s" onclick='pycmd("ease%d");'>\
%s%s</button></td>""" % (
            extra,
            tr.actions_shortcut_key(val=i),
            i,
            i,
            label,
            due,
        )

    buf = "<center><table cellpading=0 cellspacing=0><tr>"
    for ease, label in self._answerButtonList():
        buf += but(ease, label)
    buf += "</tr></table>"
    script = """
<script>$(function () { $("#defease").focus(); });</script>"""
    return buf + script




def renderReviewer():
    Reviewer._bottomHTML = wrap(Reviewer._bottomHTML, bottomHTML)
    Reviewer._showAnswerButton = wrap(Reviewer._showAnswerButton, showAnswerButton)
    Reviewer._answerButtons = wrap(Reviewer._answerButtons, answerButtons)

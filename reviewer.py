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
from anki.hooks import wrap
from aqt import  gui_hooks
from aqt.reviewer import Reviewer
from aqt.utils import *
import json
from .config import *


def bottomHTML(self):
    return """
<center id=outer>
<table id=innertable width=100%% cellspacing=0 cellpadding=0>
<tr>
<td align=left width=50 valign=top class=stat>
<br>
<button style="color: {THEME[buttons-label-color]}; background-color:{THEME[buttons-color]} "  class='btn btn-sm'title="%(editkey)s" onclick="pycmd('edit');">%(edit)s</button></td>
<td align=center valign=top id=middle>
</td>
<td width=50 align=right valign=top class=stat><span id=time class=stattxt>
</span><br>
<button style="color: {THEME[buttons-label-color]} ; background-color:{THEME[buttons-color]} "class=' btn btn-sm' onclick="pycmd('more');">%(more)s %(downArrow)s</button>
</td>
</tr>
</table>
</center>
<script>
time = %(time)d;
</script>
""".format(THEME=THEME) % dict(
        rem=self._remaining(),
        edit=_("Edit"),
        editkey=_("Shortcut key: %s") % "E",
        more=_("More"),
        downArrow=downArrow(),
        time=self.card.timeTaken() // 1000,
    )

def showAnswerButton(self):
    if not self.typeCorrect:
        self.mw.web.setFocus()
    middle = """
<span class=stattxt>%s</span><br>
<button style='color: {THEME[buttons-label-color]} ;background-color:{THEME[buttons-color]}' class='btn btn-sm' title="%s" id=ansbut onclick='pycmd("ans");'>%s</button>""".format(THEME=THEME) % (
        self._remaining(),
        _("Shortcut key: %s") % _("Space"),
        _("Show Answer"),
    )
    # wrap it in a table so it has the same top margin as the ease buttons
    middle = (
        "<tr><td class=stat2 align=center>%s</td></tr>"
        % middle
    )
    if self.card.shouldShowTimer():
        maxTime = self.card.time_limit() / 1000
    else:
        maxTime = 0
    self.bottom.web.eval("showQuestion(%s,%d);" % (json.dumps(middle), maxTime))
    self.bottom.web.adjustHeightToFit()





def answerButtons(self):
    default = self._defaultEase()

    def but(i, label):
        if i == default:
            extra = "id=defease"
        else:
            extra = ""
        due = self._buttonTime(i)
        
        return """
<td align=center>%s<button class='btn btn-sm ' %s title="%s" data-ease="%s" onclick='pycmd("ease%d");'>\
%s</button></td>""" % (
            due,
            extra,
            _("Shortcut key: %s") % i,
            i,
            i,
            label,
        )

    buf = "<center><table cellpading=0 cellspacing=0><tr>"
    for ease, label in self._answerButtonList():
        buf += but(ease, label)
    buf += "</tr></table>"
    script = """
<script>$(function () { $("#defease").focus(); });</script>"""
    return buf + script


def renderReviewer():
    Reviewer._bottomHTML = wrap (Reviewer._bottomHTML , bottomHTML)
    Reviewer._showAnswerButton = wrap (Reviewer._showAnswerButton , showAnswerButton)
    Reviewer._answerButtons = wrap (Reviewer._answerButtons , answerButtons)
    
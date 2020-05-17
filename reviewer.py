from anki.hooks import wrap
from aqt import  gui_hooks
from aqt.reviewer import Reviewer
from aqt.utils import *
import json


def bottomHTML(self):
    return """
<center id=outer>
<table id=innertable width=100%% cellspacing=0 cellpadding=0>
<tr>
<td align=left width=50 valign=top class=stat>
<br>
<a class='waves-effect waves-light btn-small'title="%(editkey)s" onclick="pycmd('edit');">%(edit)s</a></td>
<td align=center valign=top id=middle>
</td>
<td width=50 align=right valign=top class=stat><span id=time class=stattxt>
</span><br>
<a class='waves-effect waves-light btn-small' onclick="pycmd('more');">%(more)s %(downArrow)s</a>
</td>
</tr>
</table>
</center>
<script>
time = %(time)d;
</script>
""" % dict(
        rem=self._remaining(),
        edit=_("Edit"),
        editkey=_("Shortcut key: %s") % "E",
        more=_("More"),
        downArrow=downArrow(),
        time=self.card.timeTaken() // 1000,
    )

def showAnswerButton(self):
    if not self.typeCorrect:
        self.bottom.web.setFocus()
    middle = """
<span class=stattxt>%s</span><br>
<a class='waves-effect waves-light btn-small' title="%s" id=ansbut onclick='pycmd("ans");'>%s</a>""" % (
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
        maxTime = self.card.timeLimit() / 1000
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
        if label == 'Good':
            color= 'green'
        elif label == 'Again' :
            color ='red'
        elif label == 'Easy' :
            color ='blue'
        elif label == 'Hard' :
            color ='yellow darken-3'
        return """
<td align=center>%s<a class='waves-effect waves-light btn-small %s' %s title="%s" data-ease="%s" onclick='pycmd("ease%d");'>\
%s</a></td>""" % (
            due,
            color,
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
    
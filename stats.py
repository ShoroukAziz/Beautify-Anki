# -*- coding: utf-8 -*-
# based on Carlos Duarte in add-on (More Decks Stats and Time Left) https://ankiweb.net/shared/info/1556734708 
#License        | GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


from anki.hooks import wrap
from anki.lang import _, ngettext
from aqt.deckbrowser import DeckBrowser
from aqt import mw


#-------------Configuration------------------
if getattr(getattr(mw, "addonManager", None), "getConfig", None): #Anki 2.1
    config = mw.addonManager.getConfig(__name__)
else:
    # The default steps for "New" Anki cards are 1min and 10min meaning that you see New cards actually a minimum of *TWO* times that day
    # You can now configure how many times new cards will be counted.
    # CountTimesNew = 1 (old version)
    # Quantify '1' time the "new card" time | Example: Steps (10 1440)
    # CountTimesNew = 2 (default)
    # Quantify '2' times the "new card" time | Example: Steps (1 10)
    # CountTimesNew = n
    # Quantify 'n' times the "new card" time | Example: Steps (1 10 10 20 30...)

    CountTimesNew = 2
#-------------Configuration------------------
CountTimesNew = 2
def updateStatsMethod():
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

        
        
        stats = _old(self)
        
        
        # def getHeatMapData():
        #     heat_map = _old(self).split('card)')[1]      
        #     heat_map = """
        # <div class="row">
        # <div class="card">
        # <div class="card-content">
        # {}
        # </div>
        # </div>
        # </div>
        # """.format(heat_map)   
        #     return ("" , "" , "","" , "" , "" ,heat_map)
            
            # longest_streak = heat_map.split('Longest streak')[1].split('day')[0].split('">')[1]
            # longest_streak_icon='stars'
            # longest_streak_color = 'amber-text'

            # if int(longest_streak) >= 2:
            #     longest_streak +=" days"
            # else :
            #     if int(longest_streak) == 0:
            #         longest_streak_icon = 'sentiment_very_dissatisfied'
            #         longest_streak_color = ' grey-text text-darken-3'
            #     longest_streak +=" day"
        
            # current_streak = heat_map.split('Current streak')[1].split('day')[0].split('">')[1]
            # current_streak_icon = 'grade'
            # current_streak_color = 'amber-text'
            # if int(current_streak) >= 2:
            #     current_streak +=" days"            
            # else :       
            #     if int(current_streak) == 0:
            #         current_streak_icon = 'sentiment_very_dissatisfied'
            #         current_streak_color = ' grey-text text-darken-3'
            #     current_streak +=" day"
            
            # return (current_streak_color,current_streak_icon,current_streak,longest_streak_color,longest_streak_icon ,longest_streak,heat_map)

        
       
        new_cards = " <i class=' material-icons  small indigo-text   left'>fiber_new</i>   New Cards :  &nbsp;  %(d)s" % dict(d=new)
        
        learn_cards = " Learn : &nbsp;  %(c)s <br> "% dict(c=lrn)
        review_cards = " Review : &nbsp; %(c)s  "% dict(c=due)       
        due_cards = "<i class=' material-icons  small red-text text-darken-2  left'>schedule</i>   Due  :  &nbsp;   %(c)s<br> " %dict(c=(lrn+due))
        due_cards+= learn_cards +review_cards 
        
        totals_cards = "<i class=' material-icons  small light-blue-text left'>donut_small </i> Total :  &nbsp;  %(c)s" % dict(c=(totalDisplay))
        
        average_remaining =   _("%.01f") % (speed) + "&nbsp;" + (_("Cards") + "/" + _("Minutes").replace("s", "")).lower()  


        new_due_row="""
        <div class="row">
        <div class='col s6 valign-wrapper card horizontal small red-text indigo lighten-4 grey-text text-darken-4'>
        {}
        </div>
        <div class='col s6 valign-wrapper card horizontal small white-text red lighten-4 grey-text text-darken-4'>
        {}
        </div>
 
        </div>
        """.format(new_cards,due_cards)


        # streak_row="""
        #  <div class="row">
        # <div class='col s6 valign-wrapper card horizontal small  grey lighten-3  grey-text text-darken-4'>
        #  <i class=" material-icons  small  {}  left">{}</i> Current Streak <br>
        #     {}
        # </div>
        # <div class='col s6 valign-wrapper card horizontal small   grey lighten-3  grey-text text-darken-4'>
        #    <i class=" material-icons  small  {}  left">{}</i> Longest Streak <br> {} 
        # </div>
        # </row></div>
        # """.format(HeatMapData[0],HeatMapData[1],HeatMapData[2],HeatMapData[3],HeatMapData[4],HeatMapData[5])
        
        original_stats_row="""
        <div class="row">
        <div class='col s12 valign-wrapper card horizontal small white-text green lighten-4 grey-text text-darken-4'>
             <i class=" material-icons  small green-text   left">playlist_add_check</i>
            {}
        </div>
        </div>
        """.format(stats)

        average_remaining_row="""
        <div class="row">
        <div class='col s6 valign-wrapper card horizontal small lime lighten-4 grey-text text-darken-4'>
         <i class=" material-icons  small lime-text   left">access_alarm</i> Average:
            {}
        </div>
        <div class='col s6 valign-wrapper card horizontal small  red lighten-4 grey-text text-darken-4'>
           <i class=" material-icons  small red-text text-darken-2   left">timer</i> {} &nbsp;more
        </div>
        </row></div>
        """.format(average_remaining, str(ngettext("%s minute", "%s minutes", minutes) % (minutes)))

        total_row="""
        <div class='row'>
         <div class='col s12 valign-wrapper card horizontal small light-blue lighten-4 grey-text text-darken-4'>
        {}
        </div>

        </div>
        </div></div>
        """.format(totals_cards)

        
        buf = original_stats_row+ average_remaining_row+new_due_row+total_row
        return buf


    DeckBrowser._renderStats = wrap(DeckBrowser._renderStats, renderStats, 'around')


        
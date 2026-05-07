"""Double-click this file in Finder to open the web_intel stats popup."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from web_intel._popup_window import StatsPopup

StatsPopup().run()

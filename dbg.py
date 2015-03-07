# -*- coding: UTF-8 -*-

import pdb
import sys

from PyQt4.QtCore import pyqtRemoveInputHook

def pyqt_set_trace():
    pyqtRemoveInputHook()

    debugger = pdb.Pdb()
    debugger.reset()

    debugger.do_next(None)
    users_frame = sys._getframe().f_back
    debugger.interaction(users_frame, None)

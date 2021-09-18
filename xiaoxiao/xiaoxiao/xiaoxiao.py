#! $PATH/python
# -*- coding: utf-8 -*-

# file name: xiaoxiao.py
# author: lianghy
# time: 2018/11/7 14:30:48

"""电路设计程序"""
import os
from os.path import join, isfile
import sys
import logging as lg
import tkinter as tk

import view
import project
import action

#sys.path.append(join(os.environ["HOME"], "work", "nuanfeng", "nuanfeng"))
#import nfmodel as nfm
# TODO: remove sys after nuanfeng is setuped to system.
#from nuanfeng import nfcircuit as nfc
#lc = nfm.Circuit()
#lc = None

lg.basicConfig(level=lg.DEBUG)

# SOURCE_DIR = os.path.dirname(os.path.realpath(__file__))
# CONFIG_FILE = join(SOURCE_DIR, 'config.ini')

pj = project.Project()
ac = action.ACRecord()
vw = view.View(pj, ac)
vw.init_gui()
vw.mw.tw.active_project()
vw.new_project()
vw.mw.tw.create_module()
vw.start_gui()
#ac.init_view(view.View)


if __name__ == "__main__":
    #BeanDesigner()
    print("xiaoxiao.py")

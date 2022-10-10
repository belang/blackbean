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

import view as xv
#import graph as xg
import action as xa
import circuit as xc
import project

#sys.path.append(join(os.environ["HOME"], "work", "nuanfeng", "nuanfeng"))
#import nfmodel as nfm
# TODO: remove sys after nuanfeng is setuped to system.
#from nuanfeng import nfcircuit as nfc

lg.basicConfig(level=lg.DEBUG)

# SOURCE_DIR = os.path.dirname(os.path.realpath(__file__))
# CONFIG_FILE = join(SOURCE_DIR, 'config.ini')

root = tk.Tk()

ac = xa.Action(root)
cc = xc.Circuit()
vw = xv.View(root, ac)
pr = project.Project(ac)
#lc = nfm.Circuit()
lc = None

#cc.link(cc, lc, ac, vw)
#lc.link(cc, lc, ac, vw)
ac.link(pr, vw, cc, lc)
vw.link()

#ac.active_project()
#ac.new_circuit()
#pr.new_project()
ac.create_module()

w = 1400
h = 800
#w = root.winfo_screenwidth() - 20
#h = root.winfo_screenheight() - 100
##print(w, h)
x = 0
y = 0
root.geometry("%dx%d+%d+%d" %(w,h,x,y))
#root.attributes("-topmost",True)
root.mainloop()


if __name__ == "__main__":
    #BeanDesigner()
    print("xiaoxiao.py")

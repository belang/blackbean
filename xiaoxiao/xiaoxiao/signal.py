#! $PATH/python
# -*- coding: utf-8 -*-

# file name: circuit.py
# author: lianghy
# time: 2019/12/13 17:22:48

"""数据模型：电路模型和工程数据。"""

import os
from os.path import join, isfile, isdir
#import pickle
import logging as lg
#import yaml
import sys
#import tkinter as tk
#from tkinter import messagebox as xm

#import view as xv
#import graph as xg
import text as xt
tx = xt.init_text()
#import action as xa
# config as user path
#sys.path.append(join(os.environ["HOME"], "private_work", "nuanfeng", "nuanfeng"))
#import nfmodel as nfm
# TODO: remove sys after nuanfeng is setuped to system.

# 约束：constrains on circuit properties.
def check_attr_name(name):
    """检查名称合法：名称必须是asicii和id。
    """
    if name.isascii() and name.isidentifier():
        return True
    raise ValueError(f"器件名称不合法！ {name}")
def check_attr_width(width):
    """检查位宽合法：位宽必须是非零数字。
    """
    if width != '0' and width.isdecimal():
        return True
    raise ValueError(f"器件位宽不合法！ {width}")

class Signal(object):
    """docstring for Signal"""
    def __init__(self, pin_dir='i', width='1', name='pin', dtype='UInt'):
        super(Signal, self).__init__()
        self.pin_dir = pin_dir
        self.width =   width
        self.name =    name
        self.dtype =   dtype
    def __str__(self):
        return f"Signal {self.name} with width {self.width}"

class Bundle():
    """Bundle is a group of signals, useful for IO, pipe registers.
    Bundle([Sig(DataType), Sig(DataType).N
    ]
    )"""
    def __init__(self, name, signal_list=[]):
        super(Bundle, self).__init__()
        check_attr_name(name)
        self.name = name
        self.signals = signal_list
    def add_signal(self, signal):
        self.signals.append(signal)
    def P(self):
        pass
    def N(self):
        pass
    def reverse_signals(self):
        raise NotImplementedError()
    def _new_bundle(self):
        """copy a Bundle of self"""
        pass


if __name__ == "__main__":
    print("circuit.py")

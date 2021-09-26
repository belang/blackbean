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

class Parameters(object):
    """docstring for Parameters"""
    def __init__(self):
        super(Parameters, self).__init__()
        pass
    def para(self, ars):
        pass
    def new(self, *paras_name):
        for one in paras_name:
            self.paras[one] = ''
    def config(self, *paras_name):
        for one in paras_name:
            self.paras[one] = ''


class LModule(object):
    """docstring for Module"""
    def __init__(self, mid, name='module'):
        super(LModule, self).__init__()
        self.mid = mid
        self.name = name
        self.port_list = []
        self.wire_list = [] # wire means signal and connection
        self.inst_list = []
        self.view = None
        self.p = Parameters()
    @property
    def devices(self):
        return self.port_list + self.wire_list + self.inst_list
    def _generate_logic(self, p):
        """ """
        pass

class LDevice(object):
    """docstring for Module"""
    def __init__(self, dname='device'):
        self.name = dname
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, name):
        check_attr_name(name)
        # TODO: check if it has the same name with other device in the same module
        self._name = name

class LInstance(LDevice):
    """docstring for Instance"""
    def __init__(self, name, ref_module=None):
        super(Instance, self).__init__(name)
        self.parameters = {}
        self.ref_module = ref_module
    def update_config(self, kwgs):
        "element, row, column, rch_count, wch_count"
        for key, value in kwgs.items():
            if key in self.parameters:
                setattr(self, key, value)

class LPort(LDevice):
    """Logic interface of a module"""
    def __init__(self, name, width):
        super(LPort, self).__init__(name)
        self.width = width
        # if isinstance(signal, Signal):
            # self.signal = signal
        # elif isinstance(signal, Bundle):
            # for one in signal.signals:
                # self.signals.add_signal(signal = one)

class LPortIn(LPort):
    """docstring for LPortIn"""
    def __init__(self, did, name='i_', width='1'):
        super(LPortIn, self).__init__(did, name, width)
        
        
class PipeReg(LModule):
    """pipeline register."""
    def __init__(self):
        super(PipeReg, self).__init__(name="PipeReg")
        self.p.new('bundle')
        self.graph = xg.GPipeReg

class Signal(object):
    """docstring for Signal"""
    def __init__(self, pin_dir='i', width='1', name='pin', dtype='UInt'):
        super(Signal, self).__init__()
        self.pin_dir = pin_dir
        self.width =   width
        self.name =    name
        self.dtype =   dtype
        
class Bundle():
    """Bundle is a group of signals, useful for IO, pipe registers.
    Bundle([Sig(DataType), Sig(DataType).N
    ]
    )"""
    def __init__(self, name, signal_list=[]):
        super(Bundle, self).__init__()
        self.name = name
        self.signals = signal_list
    def add_signal(signal):
        self.signals.append(signal)

if __name__ == "__main__":
    print("circuit.py")

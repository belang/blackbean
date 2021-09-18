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

import symbol
import logic
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

class Circuit():
    """The design.
    """
    def __init__(self, c):
        super(Circuit, self).__init__()
        self.c = c
        self.module_list = []
        self._mid = 0
        self._did = 0
        self.cur_device = None
        self.cur_module = None
        #self._top_module = None # None means use default module. don't link it to a module object, or else when use remove the module, it will refer to a false one.
    @property
    def top_module(self):
        if self.module_list[0]:
            return self.module_list[0]
        return None
    def mid(self):
        """increase module identifer and return new id."""
        self._mid += 1
        return self._mid
    def did(self):
        """increase module identifer and return new id."""
        self._did += 1
        return self._did
    def new_module(self, name, canvas):
        """new module"""
        self.cur_module = UModule(self.mid(), name, canvas)
        self.module_list.append(self.cur_module)
    def new_template(self, name, canvas):
        """new module"""
        module = template.Template(self.mid(), name, canvas)
        self.module_list.append(module)
        return module
    def new_component(self, name, canvas):
        """new module"""
        module = UModule(name, canvas)
        self.module_list.append(module)
        return module
    def new_input(self, name, width, coord):
        """以默认名称创建输入端口"""
        self.cur_device = PortIn(self.c, self.did(), name, width, coord, self.cur_module.canvas)
        self.cur_module.port_list.append(self.cur_device)
        self.cur_device.draw()
    def get_module_by_index(self, index):
        return self.module_list[index]

class Module(object):
    """docstring for Module"""
    def __init__(self, mid, canvas):
        self.mid = mid
        self.canvas = canvas
        self.symbol = None
    def active(self):
        self.canvas.pack(fill='both', expand=True)
    def deactive(self):
        self.canvas.pack_forget()
    def new_inst(self, name, coord, ref_module):
        """new instance."""
        dev = Instance(did, name, coord, ref_module)
        self.devices.append(dev)
        dev.graph.draw()
        return dev
        
class UModule(Module, logic.LModule):
    """docstring for UModule"""
    def __init__(self, mid, name, canvas):
        Module.__init__(self, mid, canvas)
        logic.LModule.__init__(self, name)
        # super(UModule, self).__init__(mid, canvas)
        # self.logic = logic.LModule(name)
        self.symbol = symbol.VUInst
    def update_symbol(self):
        """supdate symbol manully after modify ports of module"""
        pass
    def place_pin(self, config_file=None):
        if config_file:
            #config_pin_from_file()
            pass
        else:
            for port in self.logic.port_list:
                self.pin['t'].append(port.id)
        
class PortIn(logic.LPortIn, symbol.VPortIn):
    """docstring for PortIn"""
    def __init__(self, c, did, name, width, coord, canvas):
        logic.LPortIn.__init__(self, did, name, width)
        symbol.VPortIn.__init__(self, c, did, coord, canvas)

class Wire():
    """docstring for Wire"""
    def __init__(self, module, name='w_'):
        super(Wire, self).__init__(module, name)
        pass

class Instance():
    """docstring for Instance"""
    def __init__(self, did, name='U_', coord=(0,0), ref_module=None):
        super(Instance, self).__init__(did, name, coord, ref_module)
        #self.p = logic.Parameters()
        #self.c = symbol.VConfig()
        self.symbol = VInst(did, self.ref_module.symbol)
    def update_config(self, kwgs):
        "element, row, column, rch_count, wch_count"
        for key, value in kwgs.items():
            if key in self.parameters:
                setattr(self, key, value)
    def generate(self):
        """generate instance by module parameters."""
        self.ref_module._generate_logic(self.p) # parameter is about logic
        self.symbol = self.ref_module.symbol(self.c, self.canvas) # config is about symbol

class UInst(Instance):
    """Instance of user module."""
    def __init__(self, arg):
        super(UInst, self).__init__()
        self.arg = arg
        pass

class PipeReg(Instance):
    """pipeline register."""
    def __init__(self, module, name='PR_', canvas=None, coord=(0,0), ref_module=None):
        super(PipeReg, self).__init__(module, name)
        self.ref_design = 'PipeReg'
        self.graph = xg.GPipeReg(coord, module.canvas, self)

if __name__ == "__main__":
    print("circuit.py")

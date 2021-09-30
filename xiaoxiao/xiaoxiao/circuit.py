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
#import logic
import text as xt
tx = xt.init_text()
#import action as xa
# config as user path
#sys.path.append(join(os.environ["HOME"], "private_work", "nuanfeng", "nuanfeng"))
#import nfmodel as nfm
# TODO: remove sys after nuanfeng is setuped to system.

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


class VConfig:
    """graph config options."""
    def __init__(self):
        self.show_name = False # show name in graph
    def config(self, **config):
        for key, value in config.items():
            setattr(self, key, value)

class SymbolC(object):
    """docstring for Symbol"""
    def __init__(self, color='black'):
        super(SymbolC, self).__init__()
        self.color = 'black'
        self.shape = None

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
    def new_module(self, name, canvas):
        """new module"""
        md = Module(self.mid(), name, canvas)
        self.module_list.append(md)
        return md
    def new_template(self, name, canvas):
        """new module"""
        module = template.Template(self.mid(), name, canvas)
        self.module_list.append(module)
        return module
    def new_component(self, name, canvas):
        """new module"""
        module = Module(name, canvas)
        self.module_list.append(module)
        return module
    def get_module_by_index(self, index):
        return self.module_list[index]

class Module(object):
    """docstring for Module"""
    def __init__(self, mid, name, canvas):
        self._did = 0
        self.mid = mid
        self.name = name
        self.dev_type = "User"
        self.port_list = []
        self.wire_list = [] # wire means signal and connection
        self.inst_list = []
        self.view = None
        #self.p = Parameters()
        self.canvas = canvas
        self.symbol = symbol.SModule()
    @property
    def devices(self):
        return self.port_list + self.wire_list + self.inst_list
    def did(self):
        """increase module identifer and return new id."""
        self._did += 1
        return self._did
    def active(self):
        self.canvas.pack(fill='both', expand=True)
    def deactive(self):
        self.canvas.pack_forget()
    def new_input(self, c, name, width, coord):
        """以默认名称创建输入端口"""
        dev = PortIn(c, self.did(), name, width, coord, self.canvas)
        self.port_list.append(dev)
        dev.draw()
        return dev
    def new_inst(self, c, name, coord, ref_module):
        """new instance."""
        dev = Instance(c, self.did, name, coord, self.canvas, ref_module)
        self.devices.append(dev)
        dev.draw()
        return dev
    def update_symbol(self):
        """supdate symbol manully after modify ports of module"""
        self.place_pin()
    def place_pin(self, config_file=None):
        if config_file:
            #config_pin_from_file()
            pass
        else:
            self.symbol.init_pin_placement(self.port_list)

class Device(object):
    """docstring for Device"""
    def __init__(self, c, did, name, coord, canvas):
        super(Device, self).__init__()
        self._fp_shape = (-3,-3, 3,3)
        self.config = VConfig()
        self.symbol= None
        self.c = c
        self.did = did
        self.name = name
        self.coord = coord
        self.canvas = canvas
        self.main_frame = SymbolC(color='black')
        self._item_fp = [] #[id1, id2...]
        self._item_main = []
        #self._fp_coords = [] #[(x1,y1), (x2,y2)...]
        self.tags = [f'id={did}']
    @property
    def all_items(self):
        return self._item_main + self._item_fp
    def draw(self):
        self.draw_items()
        self.move_all_items()
    def draw_items(self):
        self.draw_main_frame()
        self.draw_fp()
    def move_all_items(self):
        """move all items."""
        for item in self.all_items:
            self.canvas.move(item, self.coord[0], self.coord[1])
    def get_all_cp(self):
        pass
    def deactive(self):
        for item in self._item_fp:
            self.canvas.itemconfig(item, state='hidden')
            #self.canvas.itemconfigure(item, width=0, fill=self.main_frame.color)
    def active(self):
        for item in self._item_fp:
            #self.canvas.itemconfigure(item, width=1, fill=self.main_frame.color)
            self.canvas.itemconfig(item, state='normal')
    def _move(self, item):
        self.canvas.move(item, self.coord[0], self.coord[1])
    def mouse_in(self, e):
        """on device"""
        self.c.mouse_enter_item(self)
    def mouse_ou(self, e):
        """leave device"""
        self.c.mouse_leave_item(self)
    def draw_fp(self):
        """draw flag points."""
        length = len(self.symbol.main_frame)
        i = 0
        while i < length:
            x = self.symbol.main_frame[i]
            i += 1
            y = self.symbol.main_frame[i]
            i += 1
            item = self.canvas.create_rectangle(self._fp_shape, fill='light blue', tags=tx.TagFlagPoint, state='disabled')
            self._item_fp.append(item)
            self.canvas.move(item, x, y)

class PortIn(Device):
    """docstring for PortIn"""
    def __init__(self, c, did, name, width, coord, canvas):
        super(PortIn, self).__init__(c, did, name, coord, canvas)
        self.width = width
        self.symbol= symbol.VPortIn()
        self.tags.append('cp')
        self.tags.append('dev=input')
        self.pin_symbol = symbol.SPinIn
    def draw_main_frame(self):
        item = self.canvas.create_polygon(self.symbol.main_frame, fill=self.main_frame.color, tags=self.tags, disabledoutline='blue')
        #self.canvas.move(item, self.coord[0], self.coord[1])
        self.canvas.tag_bind(item, sequence='<Enter>', func=self.mouse_in, add=None)
        self.canvas.tag_bind(item, sequence='<Leave>', func=self.mouse_ou, add=None)
        self._item_main.append(item)
    def gen_pin_symbol(self, coord, side):
        return self.pin_symbol(coord, side)

class Instance(Device):
    """docstring for Instance"""
    def __init__(self, c, did, name, coord, canvas, ref_module=None):
        super(Instance, self).__init__(c, did, name, coord, canvas)
        #self.p = logic.Parameters()
        #self.c = symbol.VConfig()
        self.ref_module = ref_module
        self.symbol = ref_module.symbol
        #self.symbol = symbol.VInst(c, did)
        self.main_frame.color = 'white'
        self.tags.append('inst')
        self.text = [{'text':self.name, 'coord':self.symbol._name_coord},]
        self._item_pin = []
        self._item_text = []
    @property
    def all_items(self):
        return self._item_main + self._item_fp + self._item_pin + self._item_text
    def update_config(self, kwgs):
        "element, row, column, rch_count, wch_count"
        for key, value in kwgs.items():
            if key in self.parameters:
                setattr(self, key, value)
    def draw_items(self):
        self.draw_main_frame()
        self.draw_pin()
        self.draw_sub_shape()
        self.draw_text()
    def draw_main_frame(self):
        item = self.canvas.create_rectangle(self.symbol.main_frame, fill=self.main_frame.color,tags=self.tags)
        self._item_main.append(item)
    def draw_pin(self):
        for pin in self.symbol.pin_symbols:
            items = pin.draw(self.tags, self.canvas)
            self._item_pin.extend(items)
    def draw_sub_shape(self):
        pass
    def draw_text(self):
        for label in self.text:
            self._item_text.append(self.canvas.create_text(label['coord'], text=label['text'], tags=self.tags, anchor='nw'))

class Wire():
    """docstring for Wire"""
    def __init__(self, module, name='w_'):
        super(Wire, self).__init__(module, name)
        pass

class PipeReg(Instance):
    """pipeline register."""
    def __init__(self, module, name='PR_', canvas=None, coord=(0,0), ref_module=None):
        super(PipeReg, self).__init__(module, name)
        self.ref_design = 'PipeReg'
        self.graph = xg.GPipeReg(coord, module.canvas, self)

class Pin(object):
    """docstring for Pin"""
    def __init__(self, port, coord, loc):
        super(Pin, self).__init__()
        self.port = port
        self.loc = loc
        self.symbol = symbol.VPin()
        self.coord = coord

if __name__ == "__main__":
    print("circuit.py")

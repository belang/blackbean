#! $PATH/python
# -*- coding: utf-8 -*-

# file name: component.py
# author: lianghy
# time: Wed Jul 28 17:14:49 2021

""" """

import re
import symbol
import logic

class ClassName(object):
    """docstring for ClassName"""
    def __init__(self, arg):
        super(ClassName, self).__init__()
        self.arg = arg
        pass

class Component(object):
    """docstring for Component"""
    def __init__(self, arg):
        super(Component, self).__init__()
        self.arg = arg
        pass
    def active(self):
        """docstring for active"""
        create_module()

class LStraightPipeline():
    """docstring for LPipeline"""
    def __init__(self, name='pipeline'):
        super(LStraightPipeline, self).__init__(name)
        self._inner_signals = ["valid", "stall", "flush"]
        self.stages = None
        self.bundles = parse_bundle(config['BUNDLE'])
        self.stages = parse_stage(config['PIPELINE']['stage'])
        self.port_list = parse_port(config['PIPELINE']['port'])
        self.pipe_signal = parse_pipe_signal(config['PIPELINE']['pipesig'])
        self.pin_layout = parse_pin(config['PIN'])
        #self.p.config(stages=self.stages, signals=self.signals)
    @property
    def stage_length(self):
        return len(self.stages)
    def has_bundle(self, name):
        for one in self.bundles:
            if one.name == name:
                return True
        return False

class VStraightPipeline():
    """Show the main block, and in another module show stages."""
    def __init__(self, logic, coord, canvas):
        super(VStraightPipeline, self).__init__(logic, coord, canvas)
        y = self._stage_height * [self.logic.stage_length - 1] + self._stage_height 
        self.main_frame = [0, 0, 100, y]
        self.tags.append('StPipe')
        #self.pin = {'l':[], 'r':[], 't':[], 'd':[]}

class StraightPipeline(LStraightPipeline):
    """docstring for StraightPipeline"""
    def __init__(self, config):
        super(StraightPipeline, self).__init__()
        self.symbol = symbol.VStraightPipeline
        self.submodule = None
    def pa(self, config):
        self.name = config['PIPELINE']['name']
        self.bundles = parse_bundle(config['BUNDLE'])
        self.stages = parse_stage(config['PIPELINE']['stage'])
        self.port_list = parse_port(config['PIPELINE']['port'])
        self.pipe_signal = parse_pipe_signal(config['PIPELINE']['pipesig'])
        self.pin_layout = parse_pin(config['PIN'])


def config_token(exprs):
    """get token of unit from xx config file.
    the token is seperated by comma"""
    return filter(len, [one.strip() for one in exprs.split(',')])

def parse_bundle(exprs):
    """parse bundle from xx config file"""
    re_signal = re.compile(r"(?P<dir>[i,o]) +(?P<width>\d+) +(?P<name>[a-z,A-Z,0-9,_]+),?")
    all_bundle = []
    for key in exprs:
        bundle = logic.Bundle(key)
        for one in config_token(exprs[key]):
            smatch = re_signal.search(one)
            bundle.add_signal(logic.Signal(smatch['dir'], smatch['width'], smatch['name']))
        all_bundle.append(bundle)
    return all_bundle

def parse_stage(exprs):
    """parse stage from xx config file"""
    return list(config_token(exprs))

def parse_port(exprs):
    """parse port from xx config file."""
    return [logic.Port(one) for one in config_token(exprs)]


def parse_pin(exprs):
    """docstring for parse_pin"""
    layout = {}
    for key in exprs:
        pass
    #layout[key] = pass
    return layout

####################################### to resymbol

class VPipeReg():
    """The layout of Regfile is::

               +-----------------------------+
               |     name                    |
               +-----------------------------+ 
               |                             |
           In>-|    (Pipe)                   |->Out
               |    bunlde                   |
               +-----------------------------+

    I0 is the default input from upper pipeline stage;
    I1 is the input from logic module(usually the implementation of the pipe stage)
    """
    def __init__(self, coord, canvas, logic):
        super(VPipeReg, self).__init__(coord, canvas, logic)
        self.config.config(show_name=True)
        self.name = logic.name
        self._shape = [0, 0, 80, 80]
        self._pipe_text = "(Pipe)"
        self.tags.append("T=pipereg")
        self.sub_items = []
        self.bundle_items = []
        self.pin_items = []
        self.item_block.append(self.sub_items)
        self.item_block.append(self.bundle_items)
        self.item_block.append(self.pin_items)
        self.pin_list = []
    def compute_shape(self):
        self.shape = self._shape
        self._name_coord = [5, 2]
        self._seperate_line = [0, 20, self.shape[2], 20]
        self._pipe_text_coord = [5, self._seperate_line[1]+10]
        self._bundle_coord = [10, self._seperate_line[1]+10] # future compute by the size of text
    def draw(self):
        """在画布上绘图。"""
        self.draw_main_frame()
        self.draw_sub_frame()
        self.draw_name()
        self.draw_bundle_text()
        self.draw_pin()
    def draw_main_frame(self):
        """docstring for draw_main_frame"""
        item = self.canvas.create_rectangle(self.shape, tags=self.tags, disabledoutline='blue')
        self.main_frame_items.append(item)
        self.move_items(self.main_frame_items)
    def draw_sub_frame(self):
        item = self.canvas.create_line(self._seperate_line, tags=self.tags)
        self.sub_items.append(item)
        self.move_items(self.sub_items)
    def draw_bundle_text(self):
        item = self.canvas.create_text(self._pipe_text_coord, text=self._pipe_text, tags=self.tags, anchor='nw')
        self.bundle_items.append(item)
        item = self.canvas.create_text(self._bundle_coord, text=self.logic.bundle, tags=self.tags, anchor='nw')
        self.move_items(self.bundle_items)
    def draw_pin(self):
        """draw regfile connection pins according circuit logic, such as one port, 1w1r, or 1w2r."""
        for port in self.rport_list:
            port.draw()
        self.pin_items.extend(port.main_frame_items)
        for port in self.wport_list:
            port.draw()
        self.pin_items.extend(port.main_frame_items)
        self.move_items(self.pin_items)
    def update(self):
        """docstring for update"""
        self.compute_shape()
        self.redraw()

rlib = [VPipeReg]



if __name__ == "__main__":
    print("component.py")

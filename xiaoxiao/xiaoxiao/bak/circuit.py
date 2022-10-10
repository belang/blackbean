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

import view as xv
import graph as xg
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
    """电路模型。用于存储电路逻辑层次。
    dir: 工作目录"""
    def __init__(self):
        super(Circuit, self).__init__()
        self.name = 'default'
        self.cur_module = None # 当前模块
        self.cur_device = None # 当前器件
        self.module_list = []

    def new_module(self, name, canvas):
        """new module"""
        self.cur_module = Module(self, name, canvas, index=len(self.module_list))
        self.module_list.append(self.cur_module)
    def new_input(self, name, width, coord):
        """new input"""
        self.cur_device = LPortIn(self.cur_module, name, width, coord)
        self.cur_device.pack()
        self.cur_device.graph.draw()
    def new_output(self, name, width, coord):
        """new output"""
        self.cur_device = LPortOut(self.cur_module, name, width, coord)
        self.cur_device.pack()
        self.cur_device.graph.draw()
    def new_inst(self, name, coord, ref_module):
        """new instance"""
        self.cur_device = LInst(self.cur_module, name, coord, ref_module)
        self.cur_device.pack()
        self.cur_device.graph.draw()
    def new_regb(self, name, coord, regb):
        """new register bundle"""
        self.cur_device = BundleReg(self.cur_module, name, coord, regb)
        self.cur_device.pack()
        self.cur_device.graph.draw()
    def new_regfile(self, name, coord):
        """new register bundle"""
        self.cur_device = Regfile(self.cur_module, name, coord)
        self.cur_device.pack()
        self.cur_device.draw()
    def new_wire(self, name, width, coord, item):
        """new wire"""
        # wire has been drawn
        self.cur_device = LWire(self.cur_module, name, width, coord, item)
        self.cur_device.pack()
    # 删除
    def del_device(self, device=None):
        """删除器件，如果device为None，则删除当前器件。"""
        if not isinstance(device, Device):
            device = self.cur_device
        device.delete()
        self.cur_device = None
    def rm_module_by_index(self, index):
        """根据index删除模块。"""
        self.module_list.pop(index)
        self.cur_module = None
    def insert_module(self, index, module):
        """insert a module to circuit by the index。"""
        self.module_list.insert(index, module)
    # 辅助功能
    def get_module(self, name):
        """通过模块名，查找模块，返回模块。如果没有找到则报错。"""
        for module in self.module_list:
            if module.name == name:
                return module
        raise ValueError(f'没有找到模块:{name}')
    def get_module_by_index(self, index):
        """通过模块的序号查找模块对象。如果没有找到则报错。"""
        return self.module_list[module]
    def find_device_by_id(self, item_id):
        """search device by id"""
        for dev_list in self.cur_module.device_list:
            for one_device in dev_list:
                if item_id in one_device.graph.all_items:
                    return one_device
        raise ValueError(f"not found item: id {item_id}, tags are {self.cur_module.canvas.gettags(item_id)}")
    def active_module_by_index(self, index):
        """根据index激活模块。"""
        if index is not None:
            self.cur_module = self.module_list[index]
        self.cur_module.active()
    def deactive_device(self):
        """不激活器件。"""
        self.cur_device.graph.deactive()
        self.cur_device = None
    def deactive_module(self):
        """不激活模块和器件。"""
        self.cur_device = None
        self.cur_module = None
    def active_device(self, item_id=None):
        """根据器件canvas item ID激活器件。"""
        if item_id is not None:
            self.cur_device = self.find_device_by_id(item_id)
        if self.cur_device:
            self.cur_device.graph.active()

    def save_circuit(self):
        """保存电路"""
        data = []
        for module in self.module_list:
            data.append(module.save_data())
        return data
    def close(self):
        """关闭电路"""
        for mod in self.module_list:
            mod.canvas.destroy()
        self.cur_module = None
        self.cur_device = None
        self.module_list.clear()
    # circuit related function

    ############################# to review
    # function
    def _save_canvas_info(self):
        """save all canvas related info about circuit from attribute windows."""
        data = []
        for one_page in self.aw.module_list:
            page = {'name': one_page.name}
            page['device'] = [one_dev.save_data() for one_dev in one_page.device_list]
            canvas = one_page.canvas
            page['item'] = [(canvas.coords(one_item), canvas.gettags(one_item)) for one_item in canvas.find_all()]
            data.append(page)
        return data


class Module():
    """module
    属性列表：
       * source          The design source: circuit, empty, verilog ...
       * name            模块名
       * canvas          canvas画布
       * index           模块在电路中的index, same as in list_win
       * input_list      输入端口列表
       * output_list     输出端口列表
       * inst_list       模块中的实例单元列表
       * wire_list       线列表（连接器）
       * block_list      块列表
       * inst_view       实例化的参考图形pin config
       * device_list     模块所有器件列表
    """
        #port_list       输入输出端口列表（总线）
    def __init__(self, circuit, name, canvas, index):
        super(Module, self).__init__()
        self.source = 'circuit'
        self.circuit = circuit
        self._name = "module"
        self.name = name
        self.canvas = canvas
        self.index = index
        #self.port_list = []
        self.input_list  = []
        self.output_list = []
        self.inst_list   = []
        self.wire_list   = []
        self.block_list  = []
        self.reg_list   = []
        self.inst_view = []
        self.device_list = [self.input_list, self.output_list, self.inst_list, self.wire_list, self.block_list, self.reg_list]
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, name):
        check_attr_name(name)
        # TODO: 检查模块是否重名
        self._name = name
    def is_init_view(self):
        """check if the graph init the view."""
        if self.inst_view == []:
            return False
        return True
    def init_instance_view(self):
        """重新生成实例图形。"""
        self.inst_view.clear()
        self.inst_view.append(self.input_list)
        self.inst_view.append(self.output_list)
        self.inst_view.append([])
        self.inst_view.append([])
        #self.inst_view.config_pin_placement([self.input_list, self.output_list])
    def get_pin(self, name):
        """get pin by name"""
        for one in self.input_list:
            if one.name == name:
                return one
        for one in self.output_list:
            if one.name == name:
                return one
    def save_data(self):
        """save logic and graph."""
        return {'name':self.name,
            'input' :[dev.save_data() for dev in self.input_list ],
            'output':[dev.save_data() for dev in self.output_list],
            'inst'  :[dev.save_data() for dev in self.inst_list  ],
            'wire'  :[dev.save_data() for dev in self.wire_list  ],
            'block' :[dev.save_data() for dev in self.block_list ],
            'shape' :self.inst_view
                }
    def active(self):
        self.canvas.pack(fill='both', expand=True)

        
class Device():
    """device class
    * shape: shapes of device, class::Graph
    * module: used to search canvas, logic
    """
    def __init__(self, module, name):
        self.module = module
        self._name = "device"
        self.name = name
        self.graph = None
        self.module_device_list = self.module.inst_list
        self.parameters = []

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, name):
        check_attr_name(name)
        # TODO: check if it has the same name with other device in the same module
        self._name = name
    def pack(self):
        """add device to module"""
        self.module_device_list.append(self)
        #self.module.inst_list.append(self)
        #raise NotImplementedError
    def delete(self):
        """delete device from module and remove the graph."""
        self.module_device_list.remove(self)
        self.graph.destroy()
    def save_data(self):
        """save data"""
        raise NotImplementedError

class SSDevice(Device):
    """device class
    """
    def __init__(self, module, name, width):
        super(SSDevice, self).__init__(module, name)
        self._width = width

    @property
    def width(self):
        return self._width
    @width.setter
    def width(self, width):
        try:
            check_attr_width(width)
            self._width = width
        except ValueError as exp:
            raise exp

class LPort(SSDevice):
    """port
    """
    def __init__(self, module, name, width):
        super(LPort, self).__init__(module, name, width)
        pass
    def gen_pin(self, name, coord, canvas, side='l'):
        """generate pin graph for instance."""
        return self.pin_graph(name, coord, canvas, side)
    def save_data(self):
        """save data"""
        return {'name':self.name,
                'width':self.width,
                'coord':self.graph.coord}

class LPortIn(LPort):
    """input
    """
    def __init__(self, module, name, width, coord):
        super(LPortIn, self).__init__(module, name, width)
        self.graph = xg.GPortIn(coord, module.canvas)
        self.pin_graph = xg.GPinIn
    def pack(self):
        self.module.input_list.append(self)

class LPortOut(LPort):
    """output """
    def __init__(self, module, name, width, coord):
        super(LPortOut, self).__init__(module, name, width)
        self.graph = xg.GPortOut(coord, module.canvas)
        self.pin_graph = xg.GPinOut
    def pack(self):
        self.module.output_list.append(self)

class LWire(SSDevice):
    """线。"""
    def __init__(self, module, name, width, coord, item):
        super(LWire, self).__init__(module, name, width)
        self.graph = xg.GWire(coord, module.canvas, item)
    def pack(self):
        self.module.wire_list.append(self)
    def save_data(self):
        """save data"""
        return {'name':self.name,
                'width':self.width,
                'coord':self.graph.border_coord}

class LInst(Device):
    """实例单元; """
    def __init__(self, module, name, coord, ref_module):
        super(LInst, self).__init__(module, name)
        self.ref_module = ref_module # 模块对象
        if not ref_module.is_init_view():
           ref_module.init_instance_view()
        self.graph = xg.GInst(coord, module.canvas, ref_module.inst_view, self)
    def pack(self):
        self.module.inst_list.append(self)
    def save_data(self):
        """save data"""
        return {'name':self.name,
                'ref_name':self.ref_module.name,
                'coord':self.graph.coord}

class Register(SSDevice):
    """docstring for Register"""
    def __init__(self, module, name, width, v_reset):
        super(Register, self).__init__(module, name, width)
        self.v_reset = v_reset

class Bundle(Device):
    """docstring for Vector"""
    def __init__(self, module, name, units):
        super(Bundle, self).__init__(module, name)
        self.elements = units
        pass

class BundleReg(Bundle):
    """docstring for BundleReg"""
    def __init__(self, module, name, coord, reg_list):
        super(BundleReg, self).__init__(module, name, [Register(module, one[0], one[1], one[2]) for one in reg_list])
        #self.graph = xg.GBReg(coord, module.canvas) # TODO
        pass
    def pack(self):
        self.module.reg_list.append(self)

class Vector(Device):
    """docstring for Vector"""
    def __init__(self, module, name, units):
        super(Vector, self).__init__(module, name)
        self.units = units
        pass

class Regfile(Device):
    """docstring for Regfile"""
    def __init__(self, module, name, coord):
        super(Regfile, self).__init__(module, name)
        self.element   = "32"
        self.row       = "32"
        self.column    = "1"
        self.rch_count = "1"
        self.wch_count = "1"
        self.graph = xg.GRegfile(coord, module.canvas, self)
    def update_config(self, kwgs):
        "element, row, column, rch_count, wch_count"
        for key, value in kwgs.items():
            setattr(self, key, value)
        # self.element   = element  
        # self.row       = row      
        # self.column    = column   
        # self.rch_count = rch_count
        # self.wch_count = wch_count
        #self.graph.update(self)
    def draw(self):
        self.graph.draw()

class Component(Device):
    """docstring for PipeReg"""
    def __init__(self, module, name, coord):
        super(PipeReg, self).__init__(module, name)
        self.arg = arg
        self.parameters = ['name']
    def update_config(self, kwgs):
        "element, row, column, rch_count, wch_count"
        for key, value in kwgs.items():
            if key in self.parameters:
                setattr(self, key, value)

class PipeReg(Component):
    """pipeline register."""
    def __init__(self, module, name, coord, bundle=''):
        super(PipeReg, self).__init__(module, name)
        self.bundle = ''
        self.parameters.append('bundle')
        self.graph = xg.GPipeReg(coord, module.canvas, self)

# bus: in a lib file, with A pin and B pin for module pins.
#dev_none = Device(None, tx.NameNone)

class Design(object):
    """docstring for Logic"""
    def __init__(self, arg):
        super(Logic, self).__init__()
        self.arg = arg
        self.module_list = []

class Module(object):
    """docstring for Module"""
    def __init__(self, arg):
        super(Module, self).__init__()
        self.arg = arg
        self.device_list = []

class Device(object):
    """docstring for Device"""
    def __init__(self, module, name):
        super(Device, self).__init__()
        self._name = "device"
        self.module = module
        self.name = name
        self.graph = None
        pass
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, name):
        check_attr_name(name)
        # TODO: check if it has the same name with other device in the same module
        self._name = name

class Port(Device):
    """docstring for Port"""
    def __init__(self, module, name='p_'):
        super(Port, self).__init__(module, name)
        self.module, name= = module, name=
        pass

class Wire(Device):
    """docstring for Wire"""
    def __init__(self, module, name='w_'):
        super(Wire, self).__init__(module, name)
        pass

class Instance(Device):
    """docstring for Instance"""
    def __init__(self, module, name='I_'):
        super(Instance, self).__init__(module, name)
        self.ref_name = ''
        self.
        pass



if __name__ == "__main__":
    print("circuit.py")

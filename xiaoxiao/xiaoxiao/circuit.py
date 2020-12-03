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
        self.cur_module = None # 当前模块
        self.cur_device = dev_none # 当前器件
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
    def new_wire(self, name, width, coord, item):
        """new wire"""
        # wire has been drawn
        self.cur_device = LWire(self.cur_module, name, width, coord, item)
        self.cur_device.pack()
    # 删除
    def del_device(self, device=None):
        """删除器件，如果device为None，则删除当前器件。"""
        if isinstance(device, Device):
            self.cur_module.del_device(device)
        else:
            self.cur_module.del_device(self.cur_device)
        self.cur_device = dev_none
    def del_module_by_index(self, index):
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
    def active_module_by_index(self, index):
        """根据index激活模块。"""
        if index is not None:
            self.cur_module = self.module_list[index]
        self.deactive_device()
        self.cur_device = dev_none
    def deactive_device(self):
        """不激活器件。"""
        self.cur_device.graph.deactive()
    def deactive_module(self):
        """不激活模块和器件。"""
        self.cur_device = dev_none
        self.cur_module = None
    def active_device(self, item_id):
        """根据器件canvas item ID激活器件。"""
        if item_id is not None:
            self.deactive_device()
            for dev_list in self.cur_module.device_list:
                for one_device in dev_list:
                    if item_id in one_device.graph.items:
                        self.cur_device = one_device
                        break
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
        self.cur_device = dev_none
        self.module_list.clear()
    # project related function/ partly to move to NFCircuit
    def load_circuit(self):
        """加载电路"""
        for module in data:
            self.module_list.append()
    def new_circuit(self):
        """新电路"""
        # 是否已打开电路
        # 询问电路目录和名称
        # 检查目录存在
        # 创建电路文件
        if self.logic.name != "":
            lg.error("请关闭当前电路！")
            return False
        tdata = {"name":'default', 'dir':'.'}
        xv.DiaNewProject(self.top.aw, tdata)
        if tdata['name'].isidentifier():
            self.name = tdata['name']
            if not isdir(tdata['dir']):
                self.dir = "."
            lg.info("创建电路: %s", self.name)
            return True
        else:
            lg.error("请检查电路名称！")
            return False
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
       * name            模块名
       * canvas          canvas画布
       * index           模块在电路中的index, same as in list_win
       * input_list      输入端口列表
       * output_list     输出端口列表
       * inst_list       模块中的实例单元列表
       * wire_list       线列表（连接器）
       * block_list      块列表
       * inst_view       实例化的参考图形
       * device_list     模块所有器件列表
    """
        #port_list       输入输出端口列表（总线）
    def __init__(self, circuit, name, canvas, index):
        super(Module, self).__init__()
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
        self.inst_view = xg.GModuleView((0,0), self.canvas)
        self.device_list = [self.input_list, self.output_list, self.inst_list, self.wire_list, self.block_list]
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
        if self.inst_view.mbox == (0, 0, 0, 0):
            return False
        return True
    def init_instance_view(self):
        """重新生成实例图形。"""
        self.inst_view.config_pin_placement([self.input_list, self.output_list])
    def del_device(self, device):
        """模块中删除器件"""
        if isinstance(device, LPortIn):
            self.input_list.remove(device)
        elif isinstance(device, LPortOut):
            self.output_list.remove(device)
        elif isinstance(device, LInst):
            self.inst_list.remove(device)
        elif isinstance(device, Device):
            return
        else:
            raise NotImplementedError()
        self.delete_graph(device)
    def get_pin(self, name):
        """get pin by name"""
        for one in self.input_list:
            if one.name == name:
                return one
        for one in self.output_list:
            if one.name == name:
                return one
    def delete_graph(self, device):
        """remove graph"""
        # TODO:删除时，设置状态为hidden
        for item in device.graph.items:
            self.canvas.delete(item)
    def save_data(self):
        """save logic and graph."""
        return [self.name,
                [dev.save_data() for dev in self.input_list ],
                [dev.save_data() for dev in self.output_list],
                [dev.save_data() for dev in self.inst_list  ],
                [dev.save_data() for dev in self.wire_list  ],
                [dev.save_data() for dev in self.block_list ],
                self.inst_view.save_data()
                ]

gnone = xg.Graph((0,0), None)

class Device():
    """device class
    coord: 原点坐标，未来预留，图形变化功能
    items: [canvas items]
    """
    def __init__(self, module, name, width):
        self._name = "device"
        self._width = '1'
        self.name = name
        self.width = width
        self.graph = gnone
        self.module = module

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, name):
        check_attr_name(name)
        # TODO: 检查器件是否重名
        self._name = name
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
    def pack(self):
        """add device to module"""
        raise NotImplementedError
    def save_data(self):
        """save data"""
        raise NotImplementedError


class LPort(Device):
    """port
    """
    def __init__(self, module, name, width):
        super(LPort, self).__init__(module, name, width)
        pass
    def gen_pin(self):
        """generate pin graph for instance."""
        return self.pin_graph
    def save_data(self):
        """save data"""
        return [self.name, self.width, self.graph.coord]

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

class LWire(Device):
    """线。"""
    def __init__(self, module, name, width, coord, item):
        super(LWire, self).__init__(module, name, width)
        self.graph = xg.GWire(coord, module.canvas, item)
    def pack(self):
        self.module.wire_list.append(self)
    def save_data(self):
        """save data"""
        return [self.name, self.width, self.graph.border_coord]

class LInst(Device):
    """实例单元; """
    def __init__(self, module, name, coord, ref_module):
        super(LInst, self).__init__(module, name, width='1')
        self.ref_module = ref_module # 模块对象
        if not ref_module.is_init_view():
            ref_module.init_instance_view()
        self.graph = xg.GInst(coord, module.canvas, ref_module.inst_view)
    def pack(self):
        self.module.inst_list.append(self)
    def save_data(self):
        """save data"""
        return [self.name, self.graph.coord, self.ref_module.name]

dev_none = Device(None, xt.NameNone, '1')

if __name__ == "__main__":
    print("circuit.py")

#! $PATH/python
# -*- coding: utf-8 -*-

# file name: func_model.py
# author: lianghy
# time: 2019/2/26 17:00:48

"""
这是电路逻辑模型库。
没有前缀的是逻辑模型，使用P前缀的是物理库。
"""

import logging as lg
import copy

class Circuit():
    """电路模型。管理电路对象，组织电路层次。
    * cur_module : 当前模块对象
    * cur_device : 当前器件对象
    * modules : 模块列表，第一个是顶层模块
    """
    def __init__(self):
        self.modules = []
        self.cur_module = None
    @property
    def top_module(self):
        """返回顶层模块"""
        return self.cur_module[0]
    # 功能函数，用于生成、修改、获取电路信息
    def new_module(self, name=""):
        """创建新的模块"""
        lg.debug("create module %s in circuit", name)
        module = NFModule(name)
        self.modules.append(module)
        self.cur_module = module
        return module
    def active_device_by_device(self, dev):
        """active_device"""
        self.cur_module.cur_device = dev
    def active_module_by_name(self, name):
        """active module by name"""
        for one in self.modules:
            if one.name == name:
                self.cur_module = one
                return True
        lg.error("can't find module %s in circuit", name)
        return False
    def close(self):
        """关闭电路"""
        for one in self.modules:
            del one
        self.modules = []

    ## unuse
    def add_connection(self, cp_id, wire_id_str):
        """add connection to both wire and cp"""
        if isinstance(self.cur_module.cur_device, Input):
            self.cur_module.cur_device.load = int(wire_id_str)
        elif isinstance(self.cur_module.cur_device, Output):
            self.cur_module.cur_device.driver = int(wire_id_str)
        else:
            lg.error("unknow type, in circuit:add_connection")
            lg.error(type(self.cur_module.cur_device))
            pass
    ## end unuse


class NFModule(object):
    """电路模块。
    """
    def __init__(self, name):
        super(NFModule, self).__init__()
        # name = 模块名称
        # devices = 器件列表
        # self.cur_device : 器件对象
        self.name = name
        self.devices = []
        self.inputs = []
        self.outputs = []
        self.wires = []
        self.instances = []
        self.cur_device = None

    def add_input(self, name, width):
        """模块增加一个输入端口。"""
        dev = Input(name, width)
        self.inputs.append(dev)
        return dev
    def add_output(self, name, width):
        """模块增加一个输出端口。"""
        dev = Output(name, width)
        self.outputs.append(dev)
        return dev
    def add_wire(self, name, width):
        """模块增加一个信号线。"""
        dev = Wire(name, width)
        self.wires.append(dev)
        return dev
    def add_instance(self, name, module):
        """模块增加一个实例。
        module: 电路中的一个模块对象。"""
        dev = Instance(name, module)
        self.instances.append(dev)
        return dev

    def has_pin(self, name):
        """检查是否有这个端口"""
        if name in [one.name for one in self.inputs] or name in [one.name for one in self.outputs]:
            return True
        return False



class Device:
    """device of a module"""
    def __init__(self, name):
        self.name = name

class Port(Device):
    """port of a module"""
    def __init__(self, name):
        super(Port, self).__init__(name)

class Input(Port):
    """input of a module"""
    def __init__(self, name, width):
        super(Input, self).__init__(name)
        self.width = width
        self.driver = "" # wire name

class Output(Port):
    """output of a module"""
    def __init__(self, name, width):
        super(Output, self).__init__(name)
        self.width = width
        self.load = "" # wire name

class PBus(Port):
    """bus port of a module"""
    def __init__(self, name):
        super(Output, self).__init__(name)
        self.inputs = []
        self.outputs = []

class Instance(Device):
    """instance of a module"""
    def __init__(self, name, module):
        super(Instance, self).__init__(name)
        self.module = copy.deepcopy(module) # 仿真时，需要存储中间状态，所以模块不能复用
        self.inputs = self.module.inputs
        self.outputs = self.module.outputs


class Wire(Device):
    """信号线。
    如果信号连接的位宽不同，则自动低位连接。
    load 或 driver是[0,0]代表连接到模块端口。
    """
    def __init__(self, name, width):
        super(Wire, self).__init__(name)
        self.width = width
        self.load = ["", ""]   # device name, pin name
        self.driver = ["", ""] # device name, pin name

class Bus(Device):
    """总线信号。
    """
    def __init__(self, name):
        super(Bus, self).__init__(name)
        self.signals = []


if __name__ == "__main__":
    print("func_model.py")

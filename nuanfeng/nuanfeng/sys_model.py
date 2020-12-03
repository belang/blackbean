#! $PATH/python
# -*- coding: utf-8 -*-

# file name: sys_model.py
# author: lianghy
# time: 11/10/2020 11:39:56 AM

"""功能设计模块"""

import typing
from collections import deque
from . import error as nfe
from . import func_model

class Module(object):
    """功能模块基本类。"""
    def __init__(self):
        super(Module, self).__init__()
        self._blocks = deque([])
    def run_all(self):
        """run all function block of module."""
        for block in self._blocks:
            block()
        return
    def run_one(self, module):
        """run one sub block in a module."""
        module()
        pass
    def block(self, func):
        """a block of code."""
        self._blocks.append(func)
        return

class Signal(func_model.Signal):
    """
    Parameter:
        * width: 信号的位宽。
        * d: 信号的驱动信号。"""
    def __init__(self, width=32, d=None):
        super(Signal, self).__init__()
    def _set_value(self, value):
        """actual store a value to _value."""
        value = self._round(value)
        self._value = value
    def _round(self, value):
        """round the value to the data width."""
        if self._value is None:
            dtype = type(value)
        else:
            dtype = type(self._value)
        if dtype is type(int):
            pass

class Port(Signal):
    """docstring for Port"""
    def __init__(self, arg=None):
        super(Port, self).__init__()
        self.arg = arg
        return

class Input(Port):
    """input"""
    def __init__(self, dtype=int):
        super(Input, self).__init__()
        self.dtype = dtype
        return

class Output(Port):
    """Output"""
    def __init__(self, dtype=int):
        super(Output, self).__init__()
        self.dtype = dtype
        return

if __name__ == "__main__":
    print("sys_model.py")

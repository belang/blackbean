#! $PATH/python
# -*- coding: utf-8 -*-

# file name: func_model.py
# author: lianghy
# time: 11/10/2020 11:39:56 AM

"""功能设计模块"""

import typing
import copy
from collections import deque
import logging
from . import error as nfe

class Module(object):
    """功能模块基本类。"""
    def __init__(self):
        super(Module, self).__init__()
        self._modes = {'0':deque()}
        self.lg = logging.Logger('module')
        self.lg.setLevel(logging.info)
        self.simu_para = {
                "profiling":True,
                "debug":True,
                }
    def run_all(self):
        """run all function mode of module."""
        for mode in self._modes.values():
            for module in mode:
                module()
    def run_mode(self, mode_index):
        """run one sub mode in a module."""
        for module in self._modes[mode_index]:
            module()
    def mode(self, func, mode_index=0):
        """a mode of code."""
        if mode_index not in self._modes.keys():
            self._modes[mode_index] = deque()
        self._modes[mode_index].append(func)
    def config(self, **argv):
        """config simulation mode.
        Parameters
        ==========
        * profiling: True, print the run time.
        * debug: True, print the Signal data.
        """
        for prop, value in argv:
            try:
                eval(f"self.simu_para[{prop}] = {value}")
            except Exception as e:
                raise e


class Signal(object):
    """
    Parameter:
        * d: 信号的驱动信号。
        """
    def __init__(self, d=None):
        super(Signal, self).__init__()
        self._driver = d
        self._value = self._driver
        self._value_state = 'idle'

    #def l(self, driver: typing.Union[Signal, Output]):
    def l(self, driver):
        """as a load of one port or signal."""
        if not isinstance(driver, Signal) and not isinstance(driver, Output):
            raise TypeError(nfe.wrong_driver_type)
        self._driver = driver
        return
    def force(self, value):
        """强制设置信号数据"""
        self._value_state = 'force'
        if isinstance(value, Signal):
            self._set_value(copy.deepcopy(value.v))
        else:
            self._set_value(value)
    def release(self):
        """恢复信号数据传递状态"""
        self._value_state = 'idle'
        if isinstance(self._driver, Signal):
            self._set_value(self._driver)

    @property
    def v(self):
        """get the value or signal"""
        if self._value_state == 'force':
            return self._vaule
        if isinstance(self._driver, Signal):
            return self._driver.v
        return self._value

    @v.setter
    def v(self, value):
        """set a value"""
        if isinstance(self._value, Signal):
            raise TypeError(nfe.forbid_set_load)
        else:
            self._set_value(value)
    def _set_value(self, value):
        """actual store a value to _value."""
        self._value = value

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
    print("func_model.py")

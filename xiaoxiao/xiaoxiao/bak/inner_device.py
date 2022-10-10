#! $PATH/python
# -*- coding: utf-8 -*-

# file name: inner_device.py
# author: lianghy
# time: Wed Jul 28 11:03:31 2021

"""pp"""

Pipeline

fc = PipeReg('FC')
dc = PipeReg('DC')
alu = PipeReg('alu')
mm = PipeReg('MM')
wb = PipeReg('WB')
mul = PipeReg('MUL')

fc.next = [dc]
dc.next = [alu, mul]
aul.next = [mm]
mm.next = [wb]
mul.next = [wb]

if __name__ == "__main__":
    print("inner_device.py")

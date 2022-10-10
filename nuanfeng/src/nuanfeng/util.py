#! $PATH/python
# -*- coding: utf-8 -*-

# file name: util.py
# author: lianghy
# time: 11/10/2020 5:39:58 PM

"""软件使用的一些工具。
"""
import numpy

def str2bitlist(din: str) -> list:
    """将二进制字符串转化为二进制数据（01）列表。"""
    return [int(x) for x in din]

def str2bitarray(din: str) -> list:
    """将二进制字符串转化为二进制数据（01）numpy.array。"""
    return numpy.array([int(x) for x in din])

if __name__ == "__main__":
    print("util.py")

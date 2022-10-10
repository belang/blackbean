#! $PATH/python
# -*- coding: utf-8 -*-

# file name: test_FSM.py
# author: lianghy
# time: 9/2/2022 3:05:25 PM

"""test FSM"""

import sys
sys.path.append('../nuanfeng')

import logging
logging.basicConfig(level=logging.DEBUG)

import nfparser
import nfsv

with open('../example/model.rst', 'r') as fin:
    document = nfparser.parse_rst_file(fin)

#print(document)
module = nfparser.parse_module(document)
print("module tree:")
print(module)
print("module in SystemVerilog:")
rtl_module = nfsv.Module(module)
rtl_module.gen_circuit()
print(rtl_module.rtl)

if __name__ == "__main__":
    print("end test")

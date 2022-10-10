#! $PATH/python
# -*- coding: utf-8 -*-

# file name: config.py
# author: lianghy
# time: 10/9/2021 5:24:34 PM

"""parse and modify config.ini"""

import re
import signal

RE_SIG_IN_BUNDLE = re.compile(r"(?P<dir>[i,o]) +(?P<width>\d+) +(?P<name>[a-z,A-Z,0-9,_]+),?")

def config_token(exprs):
    """get token of unit from xx config file.
    the token is seperated by comma"""
    return filter(len, [one.strip() for one in exprs.split(',')])

def parse_bundle(exprs):
    """parse bundle from xx config file"""
    all_bundle = []
    for key, values in exprs.items():
        bundle = signal.Bundle(key)
        for one in config_token(values):
            smatch = RE_SIG_IN_BUNDLE.search(one)
            bundle.add_signal(signal.Signal(smatch['dir'], smatch['width'], smatch['name']))
        all_bundle.append(bundle)
    return all_bundle

def parse_pin(exprs):
    """docstring for parse_pin"""
    return pin



def test_bundle():
    import configparser
    config = configparser.ConfigParser()
    bundle = """
    [BUNDLE]
    io_insn = i 32  insn,
              i 1   insn_vld,
              o 32  pc_r_addr,
              o 1   pc_r_vld
    pipe_rf = i 1   rf_r_vld,
              i 32  rf_rdata,
              o 32  rf_raddr,
              o 1   rf_w_vld,
              o 32  rf_wdata,
              o 32  rf_waddr
    io_mem = i 1   mem_data_vld,
               i 32  mem_data,
               o 32  mem_data,
               o 32  mem_addr,
               o 1   mem_w_vld
    ctrl_signal = i 32  insn,
                  i 32  pc 
    """
    config.read_string(bundle)
    bundle_obj = parse_bundle(config['BUNDLE'])
    for one in bundle_obj:
        print(f"signals in bundle {one.name} are:")
        for sig in one.signals:
            print(sig)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='self test.')
    # parser.add_argument('integer', metavar='D', type=int, nargs='+',
                        # help='an integer for the accumulator')
    parser.add_argument('mode', metavar='M', type=str, nargs='?', default='bundle',
            #action='store_true', default=False,
            help='There are three modes: run, debug, test')
    args = parser.parse_args()
    if args.mode == 'bundle':
        test_bundle()

    print("config.py")


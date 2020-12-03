#! $PATH/python
# -*- coding: utf-8 -*-

# file name: nfexample.py
# author: lianghy
# time: 2019/8/30 17:37:14

"""本文件使用暖风工具描述一个电路模块。"""

import sys
import numpy as np
import logging as lg

sys.path.append("C:\\Users\\l110084\\lhy\\work\\nuanfeng\\project_nf")
from nuanfeng.nffunc import *
from nuanfeng.util import *


class MSKModulator(Module):
    """msk modulation."""
    def __init__(self, arg=None):
        super(MSKModulator, self).__init__()
        self.arg = arg
        self.en =        Input()
        self.data_in =   Input()
        self.config =    Input()
        self.data_out = Output()
        self.block(self.func_config)
        self.block(self.func_main)
        pass
    def func_config(self):
        """config"""
        data_rate = self.config.v['data_rate']
        fsub =      self.config.v['fsub']
        fsamp =     self.config.v['fsamp']

        wd = 2*np.pi*data_rate/4
        wc = 2*np.pi*fsub

        # I, Q wave periode are 2 times of data periode.
        # So, here just caculate one periode of It, Qt as I0, Q0
        # I0 is a two element list, with each is a half periode of the wave.
        t = np.arange(0, 2/data_rate, 1/fsamp) # t: time in the 2 period of data_in .
        #points = data_rate//fsamp
        points = fsamp//data_rate
        td_cos = np.cos(wd*t) # time domain data of cosin wave
        td_sin = np.sin(wd*t)
        tc_cos = np.cos(wc*t)
        tc_sin = np.sin(wc*t)
        It = td_cos * tc_cos
        Qt = td_sin * tc_sin
        self.I0 = [It[0:points], It[points:]]
        self.Q0 = [Qt[0:points], Qt[points:]]
        # # test
        # import matplotlib.pyplot as plt
        # fg, ax = plt.subplots()
        # #x = np.arange(0, len(data_in)/self.config.v['data_rate'], 1/self.config.v['fsamp'])
        # x = np.arange(0, 10/self.config.v['data_rate'], 1/self.config.v['fsamp'])
        # ax.plot(x, np.tile(It, 10//2))
        # ax.plot(x, np.tile(Qt, 10//2))
    def func_main(self):
        """docstring for modulate"""
        data_in = self.data_in.v
        if not self.en:
            return
        dlen = len(data_in)
        nd = data_in*2-1
        di = [1]
        xp = nd[0]
        for i in range(1, dlen, 1):
            x = nd[i]
            if i%2==0:
                di.append(di[-1])
            else:
                if x != xp:
                    di.append(di[-1]*-1)
                else:
                    di.append(di[-1])
            xp = x
        dq = di*nd

        st = np.array([])
        I = np.array([])
        Q = np.array([])
        for x in range(0, dlen, 2):
            Ip = di[x]*self.I0[0]
            Qp = dq[x]*self.Q0[0]
            I = np.concatenate([I,Ip])
            Q = np.concatenate([Q,Qp])
            st = np.concatenate([st, (Ip-Qp)])
            Ip = di[x+1]*self.I0[1]
            Qp = dq[x+1]*self.Q0[1]
            I = np.concatenate([I,Ip])
            Q = np.concatenate([Q,Qp])
            st = np.concatenate([st, (Ip-Qp)])
        self.data_out.v = st
        # # test
        # import matplotlib.pyplot as plt
        # fg, ax = plt.subplots()
        # #x = np.arange(0, len(data_in)/self.config.v['data_rate'], 1/self.config.v['fsamp'])
        # x = np.arange(0, 10/self.config.v['data_rate'], 1/self.config.v['fsamp'])
        # print(len(self.I0[0]), len(self.I0[1]))
        # #ax.plot(x, numpy.concatenate((self.I0[0], self.I0[1])))
        # #ax.plot(x, numpy.concatenate((self.Q0[0], self.Q0[1])))
        # #fg, ax = plt.subplots()
        # ax.plot(x, I)
        # ax.plot(x, Q)

class TestMsk(object):
    """docstring for TestMsk"""
    def setup(self):
        """docstring for setup"""
        self.en = Signal()
        self.config = Signal()
        self.data_in = Signal()
        self.data_out = Signal()
        self.construct()
        pass
    def construct(self):
        """docstring for construct"""
        self.msk_moduletor = MSKModulator()
        # connect, l=load
        self.msk_moduletor.config.l(self.config)
        self.msk_moduletor.en.l(self.en)
        self.msk_moduletor.data_in.l(self.data_in)
        pass
    def test_random(self):
        # init data
        self.en.v = 1
        config = {}
        config['data_rate'] = 1
        config['fsub'] = 5 * config['data_rate'] / 4
        config['fsamp'] = 100 * config['data_rate']
        self.config.v = config
        # config
        #self.msk_moduletor.run_one(self.msk_moduletor.config)
        self.msk_moduletor.func_config()
        # data case 1
        self.data_in.v = str2bitarray('0110001010')
        x = np.arange(0, len(self.data_in.v)/config['data_rate'], 1/config['fsamp'])
        # simu
        #self.msk_moduletor.run()
        self.msk_moduletor.func_main()
        # check
        import matplotlib.pyplot as plt
        plt.figure()
        plt.subplot(2, 1, 1)
        din = []
        for one in self.data_in.v:
            din.extend([one]*(config['fsamp']//config['data_rate']))
        plt.plot(x, din)
        plt.plot(x, self.msk_moduletor.data_out.v)


        # # data case 2
        # self.data_in.v = str2bitarray('0101001010')
        # x = np.arange(0, len(self.data_in.v)/config['data_rate'], 1/config['fsamp'])
        # self.msk_moduletor.func_main()
        # plt.subplot(2, 1, 2)
        # din = []
        # for one in self.data_in.v:
        #     din.extend([one]*(config['fsamp']//config['data_rate']))
        # plt.plot(x, din)
        # plt.plot(x, self.msk_moduletor.data_out.v)
        plt.show()

if __name__ == "__main__":
    print("nfexample.py")

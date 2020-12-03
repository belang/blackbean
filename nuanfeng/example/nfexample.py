#! $PATH/python
# -*- coding: utf-8 -*-

# file name: nfexample.py
# author: lianghy
# time: 2019/8/30 17:37:14

"""本文件使用暖风工具描述一个电路模块。"""

import sys
sys.path.append("C:\\Users\\l110084\\lhy\\work\\nuanfeng\\project_nf\\nuanfeng")
from nffunc import *

class Adder(nc.Module):
    """全加器"""
    def __init__(self):
        super(Adder, self).__init__()
        self.input("a", 1)
        self.input("b", 1)
        self.input("c", 1)
        self.output(reg('c'), 1)
        self.output(reg('r'), 1)
    def sfunc(self):
        """功能函数仿真"""
        re = self.a + self.b + self.c
        self.c = re[0]
        self.r = re[1]


class MSKModulator(nc.FuncModule):
    """MSK 调制器"""
    def __init__(self):
        super(MSKModulator, self).__init__()
        self.en =        Input()
        self.data_in =   Input()
        self.config =    Input()
        self.data_out = Output()
        self.add_combine(self.config_module(self.config), 
            self.modulate(self.en, self.data_in, self.data_out))
    def config_module(self, config):
        """docstring for setup"""
        # TODO: auto check the input activetion
        # if not config.changed:
            # return
        data_rate = config['data_rate']
        fsub =      config['fsub']
        fsamp =     config['fsamp']

        wd = 2*np.pi*self.data_rate/4
        wc = 2*np.pi*self.fsub

        t = np.arange(0, 2/data_rate, 1/fsamp) # t: time in the 2 period of data_in .
        points = data_rate//fsamp
        td_cos = np.cos(wd*t) # time domain data of cosin wave
        td_sin = np.sin(wd*t)
        tc_cos = np.cos(wc*t)
        tc_sin = np.sin(wc*t)
        It = td_cos * tc_cos
        Qt = td_sin * tc_sin
        self.I0 = [It[0:points], It[points:]]
        self.Q0 = [Qt[0:points], Qt[points:]]
    def modulate(self, en, din, dout):
        """docstring for modulate"""
        # TODO: support combine or sequence logic for if else type.
        if not en:
            return
        dlen = len(din)
        # nd = []
        # for x in din:
            # if x == 0:
                # nd.append(-1)
            # else:
                # nd.append(+1)
        nd = din*2-1
        di = [1]
        # dq = [di[0] * nd[0]]
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
            # dq.append(di[-1]*x)
            xp = x
        dq = di*nd

        st = np.array([])
        for x in range(0, dlen, 2):
            Ip = di[x]*I0[0]
            Qp = dq[x]*Q0[0]
            st = np.concatenate([st, (Ip-Qp)])
            Ip = di[x+1]*I0[1]
            Qp = dq[x+1]*Q0[1]
            st = np.concatenate([st, (Ip-Qp)])
        self.data_out = st



def test(nf.Module):
    config = Signals()
    en = Singals()
    data_in = Signals()
    data_out = Signals()

    init_one_signals(config,
            (0, config_data)]
    init_one_signals(en, 
            (0, 0),
            (10, 1),
            (20, 0),
            ]
    init_one_signals(data_in, 
            (10, 0),
            (11, 1),
            (12, 1),
            (13, 0),
            (14, 0),
            (15, 0),
            (16, 1),
            (17, 0),
            (18, 1),
            (19, 0),
            ]
    # init_signals(
            # [0, config, en],
            # [0, config_data, ],
            # )
    config_data = {}
    config_data['data_rate'] = 1
    config_data['fsub'] = 5 * config_data['data_rate'] // 4
    config_data['fsamp'] = 100 * config_data['data_rate']

    msk_moduletor = MSKModulator(),
    # connect, l=load, d=drive
    self.msk_moduletor.config.l(config)
    self.msk_moduletor.en.l(en)
    self.msk_moduletor.data_in.l(data_in)
    self.msk_moduletor.data_out.d(data_out)

    # simu
    self.simu(20)
    # elaborate, add instance to module space

def test(nf.Module):
    en = Signal(1)
    data_in = Signal(nf.str2bitlist('0110001010'))
    config = {}
    config['data_rate'] = 1
    config['fsub'] = 5 * config['data_rate'] // 4
    config['fsamp'] = 100 * config['data_rate']
    config_data = Signal(config)

    msk_moduletor = MSKModulator(),
    # connect, l=load
    self.msk_moduletor.config.l(config_data)
    self.msk_moduletor.en.l(en)
    self.msk_moduletor.data_in.l(data_in)

    msk_moduletor.config_module()
    msk_moduletor.run()

    # result
    data_out = self.msk_moduletor.data_out
    # elaborate, add instance to module space

    data_in = Signal(nf.str2bitlist('0101001010'))
    msk_moduletor.run()
    data_out = self.msk_moduletor.data_out


class MSKMod(nf.Module):
    """msk modulation."""
    def __init__(self, arg=None):
        super(MSKMod, self).__init__()
        self.arg = arg
        self.en =        Input()
        self.data_in =   Input()
        self.config =    Input()
        self.data_out = Output()
        pass
    def config(self):
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
        points = data_rate//fsamp
        td_cos = np.cos(wd*t) # time domain data of cosin wave
        td_sin = np.sin(wd*t)
        tc_cos = np.cos(wc*t)
        tc_sin = np.sin(wc*t)
        It = td_cos * tc_cos
        Qt = td_sin * tc_sin
        self.I0 = [It[0:points], It[points:]]
        self.Q0 = [Qt[0:points], Qt[points:]]
    def function(self):
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
        for x in range(0, dlen, 2):
            Ip = di[x]*self.I0[0]
            Qp = dq[x]*self.Q0[0]
            st = np.concatenate([st, (Ip-Qp)])
            Ip = di[x+1]*self.I0[1]
            Qp = dq[x+1]*self.Q0[1]
            st = np.concatenate([st, (Ip-Qp)])
        self.data_out = st

class TestMsk(object):
    """docstring for TestMsk"""
    def setup(self):
        """docstring for setup"""
        self.en = Signal()
        self.config = Signal()
        self.data_in = Signal()
        self.data_out = Signal()
        pass
    def construct(self):
        """docstring for construct"""
        self.msk_moduletor = MSKModulator()
        # connect, l=load
        self.msk_moduletor.config.l(self.config_data)
        self.msk_moduletor.en.l(self.en)
        self.msk_moduletor.data_in.l(self.data_in)
        pass
    def test_random(self):
        import matplotlib.pyplot as plt
        plt.figure()
        # init data
        self.en.v = 1
        config = {}
        config['data_rate'] = 1
        config['fsub'] = 5 * config['data_rate'] // 4
        config['fsamp'] = 100 * config['data_rate']
        self.config.v = config
        # config
        self.msk_moduletor.config_module()
        # data case 1
        self.data_in.v = nf.str2bitlist('0110001010')
        x = np.arange(0, len(self.data_in.v)/config['data_rate'], 1/config['fsamp'])
        # simu
        self.msk_moduletor.run()
        # check
        plt.subplot(1)
        plt.plot(x, self.msk_moduletor.data_out.v)

        # data case 2
        self.data_in.v = nf.str2bitlist('0101001010')
        x = np.arange(0, len(self.data_in.v)/config['data_rate'], 1/config['fsamp'])
        self.msk_moduletor.run()
        plt.subplot(2)
        plt.plot(x, self.msk_moduletor.data_out.v)

if __name__ == "__main__":
    print("nfexample.py")

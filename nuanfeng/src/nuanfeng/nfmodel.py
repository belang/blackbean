#! $PATH/python
# -*- coding: utf-8 -*-

# file name: nfmodel.py
# author: lianghy
# time: 8/25/2022 4:07:26 PM

"""Nuanfeng(warm wind) model of circuit"""

import argparse
import sys

import logging

XValue = "'x"

class NFComponent(object):
    """A component is a logic function. It is initialed by a component defined in HAML"""
    def __init__(self, c_type, c_name):
        super(NFComponent, self).__init__()
        self.type = c_type
        self.name = c_name

class NFCFSM(NFComponent):
    """FSM: 
    states = [state_1, state_2, ...]
    rst_states = state_1
    condition = [(state, next_state, condition)]
    """
    def __init__(self, c_name):
        super(NFCFSM, self).__init__('FSM', c_name)
        self._state = []
        self._ex_state = []
        self._condition = []
        self._condition_table_col_head = ['state', 'next_state', 'condition']
    def __str__(self):
        doc = self.name
        doc += " state: ["
        for x in self._state:
            doc += str(x)
            doc += ', '
        doc += "]"
        doc += " condition: ["
        for x in self._condition:
            doc += str(x)
            doc += ', '
        doc += "]"
        return doc
    @property
    def states(self):
        return self._state
    @property
    def rst_state(self):
        return self._condition[0][0]
    @property
    def default_cond(self):
        return {self._condition_table_col_head[0]:self._condition[0][0],
            self._condition_table_col_head[1]:self._condition[0][1], 
            self._condition_table_col_head[2]:self._condition[0][2]}
    @property
    def conditions(self):
        return [{self._condition_table_col_head[0]:i[0],
            self._condition_table_col_head[1]:i[1], 
            self._condition_table_col_head[2]:i[2]} for i in self._condition]
    @property
    def cond_states(self):
        return [{self._condition_table_col_head[0]:i[0],
            self._condition_table_col_head[1]:i[1], 
            self._condition_table_col_head[2]:i[2]} for i in self._condition[1:]]
    def new_state(self, state):
        """add state"""
        try:
            self._state.index(state)
        except ValueError:
            self._state.append(state)
    def new_condition(self, state, next_state, condition):
        """condition: stage will transfer to next state when condition is met."""
        if next_state not in self._state:
            raise ValueError(f'{next_state} not found')
        if condition == 'RESET':
            self._condition.insert(0, (state, next_state, condition))
        else:
            if state not in self._state:
                raise ValueError(f'{state} not found')
            self._condition.append((state, next_state, condition))

class NFCIO(NFComponent):
    """IO: [name, direc, width, data]"""
    def __init__(self, c_name):
        super(NFCIO, self).__init__('IO', c_name)
        self._io = []
        pass
    def __str__(self):
        doc = self.name
        doc += " IO: ["
        for x in self.io:
            doc += str(x)
            doc += ', '
        doc += "]"
        return doc
    @property
    def io(self):
        return [{'name':io[0], 'direc':io[1], 'width':io[2]} for io in self._io]
    @property
    def io_list(self):
        return self._io
    def new_io(self, a):
        self._io.append(a)

class NFCSignal(object):
    """docstring for NFCSignal"""
    def __init__(self, name):
        super(NFCSignal, self).__init__()
        self.name = name
        self.default_value = ''
        self.branch = []
        pass
    def add_condition(self, cond, exp):
        self.branch.append({'condition':cond, 'expression':exp})

class NFCComb(NFComponent):
    """Combination logic: [name, condition, expression]"""
    def __init__(self, c_name):
        super(NFCComb, self).__init__('Comb', c_name)
        self._item = []
        pass
    def __str__(self):
        doc = self.name
        doc += " IO: ["
        for x in self.item:
            doc += str(x)
            doc += ', '
        doc += "]"
        return doc
    @property
    def item(self):
        signal_list = []
        f_new_signal = True # flag indicates next row is a new signal
        for item in self._item:
            if item[0] != '':
                # a name means a new signal; Future:: check if it is has been defined
                if f_new_signal is False:
                    signal.default_value = XValue
                signal = NFCSignal(item[0])
                signal_list.append(signal)
                f_new_signal = False
            elif f_new_signal is True:
                raise ValueError('Need a new signal!')
            if item[1] != '':
                f_new_signal = True
                signal.default_value = item[2]
            else:
                print(item)
                signal.add_condition(item[1], item[2])
        return signal_list
        #return [{'name':item[0], 'condition':item[1], 'expression':item[2]} for item in self._item]
    def new_item(self, a):
        self._item.append(a)


class NFModule(object):
    """module"""
    def __init__(self, name):
        super(NFModule, self).__init__()
        logging.debug(f'new module {name}')
        self.name = name
        self.components = []
        pass
    def __str__(self):
        doc = "Module: " + self.name
        for c in self.components:
            #doc += ' ' + c.__str__()
            doc += "\n  Component: "
            doc += str(c)
        return doc
    def new_component(self, c_type, c_name):
        logging.debug(f'new component {c_type} {c_name}')
        c = c_comp_sel[c_type](c_name)
        self.components.append(c)
        return c
    def get_component(self, ctype, cname):
        for x in self.components:
            if x.type == ctype:
                if x.name == cname:
                    return x
        raise ValueError(f'{ctype} {cname} is not defined.')

def new_circuit_component(c_type, c_name):
    return c_comp_sel[c_type](c_name)

c_comp_sel = {
        "FSM": NFCFSM,
        "IO" : NFCIO,
        "Comb" : NFCComb,
        }
if __name__ == "__main__":
    print("circuit module")

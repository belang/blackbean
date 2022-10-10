#! $PATH/python
# -*- coding: utf-8 -*-

# file name: common.py
# author: lianghy
# time: Wed Jun  9 18:08:52 2021

"""basic class"""

class XX:
    """Common class"""
    def link(self, project, window, action, circuit, logic):
        """link front and backend"""
        self.project = project
        self.cc = circuit
        self.vw = window
        self.ac = action
        self.lc = logic
        self.tw = window.tw
        self.lw = window.lw
        self.dw = window.dw
        self.aw = window.aw


if __name__ == "__main__":
    print("common.py")










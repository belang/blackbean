#! $PATH/python
# -*- coding: utf-8 -*-

# file name: project.py
# author: lianghy
# time: Thu Jun 10 14:56:08 2021

""" """


from os.path import isfile, isdir, join
import logging as lg

from tkinter import messagebox as xm

import circuit
import component
import text as xt
tx = xt.init_text()


class Project(object):
    """docstring for Project"""
    def __init__(self):
        self._name = 'project'
        self._dir = '.'
        self._default_ref_lib = component.rlib
        self.circuit = None
        self.is_changed = False
    @property
    def name(self):
        """docstring for name"""
        return self._name
    @name.setter
    def name(self, name):
        """docstring for name"""
        if name.isidentifier():
            self._name = name
        else:
            message = tx.MessageCheckCircuitName
            lg.error(message)
            xm.showerror(tx.ErrorModuleName, message)
            raise Exception()
    @property
    def dir(self):
        """docstring for dir"""
        return self._dir
    @dir.setter
    def dir(self, fdir):
        if isdir(fdir):
            self._dir = fdir
        else:
            message = tx.FileErrorDirNotExit
            lg.error(message)
            xm.showerror(tx.ErrorModuleName, message)
            raise Exception()
    @property
    def fullname(self):
        """docstring for filename"""
        return join(self.dir, self.name)

    def exist(self):
        """circuit save the data."""
        return self.circuit is not None
    def new_project(self, c, name, pdir):
        self.circuit = circuit.Circuit(c)
        return self.update_project(name, pdir)
    def close(self):
        """set project name to empty string"""
        self._name = ''
        self._dir = '.'
        self.circuit = None
    def save_project(self, name, pdir):
        """get a right project file name"""
        return self.update_project(name, pdir)
    def update_project(self, name, fdir):
        if not name.isidentifier():
            message = tx.MessageCheckCircuitName
            lg.error(message)
            xm.showerror(tx.ErrorModuleName, message)
            return False
        if not isdir(fdir):
            message = tx.FileErrorDirNotExit
            lg.error(message)
            xm.showerror(tx.ErrorModuleName, message)
            return False
        self._dir = fdir
        self._name = name
        return True



if __name__ == "__main__":
    print("project.py")


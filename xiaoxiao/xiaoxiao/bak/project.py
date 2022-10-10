#! $PATH/python
# -*- coding: utf-8 -*-

# file name: project.py
# author: lianghy
# time: Thu Jun 10 14:56:08 2021

""" """


from os.path import isfile, isdir, join
import logging as lg

from tkinter import messagebox as xm

import view as xv
import text as xt
tx = xt.init_text()


class Project(object):
    """docstring for Project"""
    def __init__(self, ac):
        self.ac = ac
        self._name = ''
        self._dir = '.'
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
        return self._name != ''
    def new_project(self, name, pdir):
        return self.update_project(name, pdir)
    def close_project(self):
        """set project name to empty string"""
        self._name = ''
        self._dir = '.'
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
    # def ask_save_project(self):
        # """docstring for ask_save_project"""
        # data = {}
        # xv.DiaSaveProject(self.ac.vw, data)
        # return data
    # def ask_project_name(self):
        # data = {}
        # xv.DiaNewProject(self.ac.vw, data)
        # return data



if __name__ == "__main__":
    print("project.py")


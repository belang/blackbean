#! $PATH/python
# -*- coding: utf-8 -*-

# file name: view.py
# author: lianghy
# time: 2018/11/7 13:58:21

"""图形界面"""

import os
from os.path import join, isfile, isdir
import sys
import logging as lg
import tkinter as tk
from tkinter import W,E,N,S,TOP,BOTTOM,LEFT,RIGHT,RIDGE,SUNKEN,SINGLE,ACTIVE,X,Y,BOTH,END
from tkinter import Frame,Toplevel,Button,Label,Listbox,Entry,Canvas,Radiobutton,IntVar
from tkinter import filedialog
from tkinter import messagebox as xm

#import action
import circuit
import text as xt
tx = xt.init_text()

# tag:
# term  terminal
# did*   did
# dir:in/out

class MainWin(Frame):
    """Top layer is the circuit.
    """
    def __init__(self, master, view, ac):
        super(MainWin, self).__init__(master)
        self.view = view
        self.ac = ac
        self._layout()
    def _layout(self):
        """init layout of main window"""
        self.tw = ToolWin(self)
        self.lw = ListWin(self)
        self.dw = DrawWin(self)
        self.aw = AttrWin(self)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        self.tw.grid(row=0, column=0, rowspan=1, columnspan=3, sticky=W+E+N+S)
        self.lw.grid(row=1, column=0, rowspan=1, columnspan=1, sticky=N+S)
        self.dw.grid(row=1, column=1, rowspan=1, columnspan=1, sticky=W+E+N+S)
        self.aw.grid(row=1, column=2, rowspan=1, columnspan=1, sticky=N+S)
        self.pack(fill=BOTH, expand=1)

class XWin(Frame):
    """基本框，用于设置基本属性。
    """
    def __init__(self, master):
        super(XWin, self).__init__(master)
        self.view = self.master.view
        self.ac = self.master.ac
        self._layout()
    def _layout(self):
        """_layout"""
        pass
    def _escape(self):
        """this is only a test purpose."""
        print("escape")


class ToolWin(XWin):
    """工具栏
    * undo stack = [function, [win list]]
    """
    def __init__(self, master):
        super(ToolWin, self).__init__(master)
    def _layout(self):
        """_layout"""
        self.config(height=2)
        bt_w = 6
        bt_h = 0
        bt_dev_w = 6
        bt_act_w = 3
        twt = tx.wt
        # first line
        Button(self, text=twt.project , height=bt_h, width=bt_w, bg='white', command=self.active_project    ).grid(row=0, column=0)
        #Button(self, text=twt.backward, height=bt_h, width=bt_w, bg='white', command=self.view.undo              ).grid(row=0, column=1)
        #Button(self, text=twt.forward , height=bt_h, width=bt_w, bg='white', command=self.view.forward           ).grid(row=0, column=2)
        #Button(self, text=twt.export  , height=bt_h, width=bt_w,             command=self.write_verilog        ).grid(row=0, column=3)
        #Button(self, text=twt.inport  , height=bt_h, width=bt_w, bg='grey',  command=self.read_verilog         ).grid(row=0, column=4)
        # 创建对象
        Button(self, text=twt.module  , height=bt_h, width=bt_w, bg='white', command=self.create_module     ).grid(row=1, column=0)
        #Button(self, text=twt.template, height=bt_h, width=bt_w, bg='white', command=self.view.create_template   ).grid(row=1, column=0)
        Button(self, text=twt.input   , height=bt_h, width=bt_w, bg='white', command=self.view.bind_new_input    ).grid(row=1, column=1)
        #Button(self, text=twt.output  , height=bt_h, width=bt_w,             command=self.view.bind_new_output   ).grid(row=1, column=2)
        Button(self, text=twt.inst    , height=bt_h, width=bt_w, bg='white', command=self.view.bind_new_inst     ).grid(row=1, column=3)
        #Button(self, text=twt.wire    , height=bt_h, width=bt_w,             command=self.view.bind_new_wire     ).grid(row=1, column=4)
        #Button(self, text=twt.regb    , height=bt_h, width=bt_w,             command=self.view.bind_new_regb     ).grid(row=1, column=5)
        #Button(self, text=twt.regfile , height=bt_h, width=bt_w,             command=self.view.bind_new_regfile  ).grid(row=1, column=6)
        #Button(self, text="反相", height=bt_h, width=bt_dev_w, command=self.new_inverter)
        #Button(self, text="模块", height=bt_h, width=bt_w, compound=tk.CENTER, image="./image/del_module.png" command=self.view.del_module).grid(row=1, column=4)
        # 修改对象
        #Button(self, text=twt.delete  , height=bt_h, width=bt_w,             command=self.view.delete            ).grid(row=2, column=0)
        #Button(self, text=twt.move    , height=bt_h, width=bt_w,             command=self.view.move_device       ).grid(row=2, column=1)
    def create_module(self):
        """create module"""
        #self.view.deactive_module()
        self.view.new_module()
        self.view.active_module()
    def active_project(self):
        """docstring for active_project"""
        self.view.deactive_device()
        self.view.mw.aw.active_project()

    def open_circuit(self):
        """打开项目文件。"""
        # 加载项目数据
        # 创建属性和图形
        if not self.cc.open_circuit():
            return
        for page in self.cc.data:
            self.view.new_module(page["name"])
            for dev in page['device']:
                if dev['type'] == 'input':
                    self.aw.cur_module.create_input(name=dev['name'], width=dev['width'])
                elif dev['type'] == 'output':
                    self.aw.create_output(name=dev['name'], width=dev['width'])
                elif dev['type'] == 'wire':
                    self.aw.create_wire(name=dev['name'], width=dev['width'])
                else:
                    lg.error("unkown device: %s", dev['type'])
            for item in page['item']:
                if 'shape=rectangle' in item[1]:
                    self.view.cur_canvas.create_rectangle(item[0][0], item[0][1], item[0][2], item[0][3], tags=item[1])
                elif 'shape=polygon' in item[1]:
                    self.view.cur_canvas.create_polygon(item[0], tags=item[1])
                elif 'shape=line' in item[1]:
                    self.view.cur_canvas.create_line(item[0], tags=item[1])
                else:
                    lg.error("unkown shape %s", item[1])

    def write_verilog(self):
        """write verilog"""
        self.aw.generate_circuit_module()
        xv.gen_verilog(self.cc, self.cc.proj_dir)
    def read_verilog(self):
        """read verilog file and generate to a module with block."""
        pass

class ListWin(XWin):
    """模块面列表。
    """
    def __init__(self, master):
        super(ListWin, self).__init__(master)
        self.config(bd=2, width=30, relief=SUNKEN)
        # layout
        tscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.module_list = tk.Listbox(self, selectmode=SINGLE, yscrollcommand=tscrollbar.set, activestyle='underline')
        tscrollbar.config(command=self.module_list.yview)
        tscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.module_list.pack(side=tk.LEFT, fill=BOTH)
        self.module_list.bind("<ButtonRelease-1>", self.active_sel_tag)

    def new_module(self, name):
        """add a module item to list and active it."""
        self.module_list.insert(tk.END, name)
    def active_module_by_index(self, index):
        """根据index激活模块"""
        self.module_list.activate(index)
    def active_sel_tag(self, event):
        """激活当前选择的模块"""
        mid = self.module_list.curselection()
        self.module_list.activate(mid[0])
        self.view.active_module_by_index(mid[0])
    def update_tag(self, name):
        """更新名称"""
        mid = self.module_list.index(tk.ACTIVE)
        #mid = self.module_list.curselection()[0]
        self.module_list.insert(mid, name)
        self.module_list.delete(mid+1)
    def update_tag_by_id(self, cid, name):
        """更新名称"""
        self.module_list.insert(cid, name)
        self.module_list.delete(cid+1)
    def remove_module(self, index):
        """remove module by index"""
        self.lw.module_list.delete(index)
    def insert_module(self, index, name):
        """insert module by index"""
        self.module_list.insert(index, name)

    def close(self):
        """关闭"""
        self.module_list.delete(0, END)

class DrawWin(XWin):
    """画图区.
    * undo_stack = [type, canvas]
    """
    def __init__(self, master):
        super(DrawWin, self).__init__(master)
        self.config(bd=2, relief=RIDGE)
        self.canvas_list = []
        self.cur_canvas = None
        

class AttrWin(XWin):
    """属性区"""
    def __init__(self, master):
        super(AttrWin, self).__init__(master)
        self.config(bd=2, width=200, relief=RIDGE)
        self.cur_win = None # 用于标记当前属性框类型：M=模块，D=器件
        #self.module = None # 模块类型窗口
        #device = None # 每种器件是一类窗口
        self.dict_dtype = { 'input': self.active_input,
                       'output': self.active_output,
                       'wire': self.active_wire,
                }
    def _layout(self):
        self._project = ProjectAttrFrame(self)
        self._module = ModuleAttrFrame(self)
        self._input = InputAttrFrame(self)
        self._output = OutputAttrFrame(self)
        self._wire = WireAttrFrame(self)
        self._instance = InstanceAttrFrame(self)
        self._regfile = RegfileAttrFrame(self)
        #self.cur_win = self._project
        #self.cur_win.pack(fill=tk.BOTH)
    def pack_module(self):
        """显示属性"""
        self.cur_win.pack_forget()
        self.cur_win = self._module
        self.cur_win.pack(fill=tk.BOTH)
    def pack_dev(self, device):
        """显示属性"""
        self.cur_win = device
        self.cur_win.pack(fill=tk.BOTH)

    def active_project(self):
        """show project attr"""
        self._project.set_attr(self.view.project)
        self.cur_win = self._project
        self.cur_win.pack(fill=tk.BOTH)
    def active_module(self, module):
        """链接模块属性，不创建新的模块面(模块)属性框"""
        self._module.set_attr(module)
        self.pack_module()
    def active_device(self, device):
        """加载器件属性框，并摆放位置。"""
        self.deactive()
        if isinstance(device, circuit.PortIn):
            self.active_input(device)
        # elif isinstance(device, circuit.PortOut):
            # self.active_output(device)
        # elif isinstance(device, circuit.Wire):
            # self.active_wire(device)
        # elif isinstance(device, circuit.Inst):
            # self.active_instance(device)
        # elif isinstance(device, circuit.Regfile):
            # self.active_regfile(device)
        else:
            raise NotImplementedError(f"device type: {type(device)}")
    def deactive(self):
        """静默当前器件。"""
        self.cur_win.pack_forget()
    def active_input(self, device):
        """加载模块端口属性框，并摆放位置。"""
        self._input.set_attr(device)
        self.pack_dev(self._input)
    def active_output(self, device):
        """加载模块端口属性框，并摆放位置。"""
        self._output.set_attr(device)
        self.pack_dev(self._output)
    def active_wire(self, device):
        """加载模块线属性框，并摆放位置。"""
        self._wire.set_attr(device)
        self.pack_dev(self._wire)
    def active_instance(self, device):
        """激活实例属性框。"""
        self._instance.set_attr(device)
        self.pack_dev(self._instance)
    def active_regfile(self, device):
        """激活regfile属性框。"""
        self._regfile.set_attr(device)
        self.pack_dev(self._regfile)
    def close(self):
        """close"""
        self.cur_win.pack_forget()
            ############# to review

    def generate_circuit_module(self):
        """generate circuit module"""
        # 提取模块连接关系
        # 从图形只能获得did，通过did在属性框可获得器件逻辑关系。
        # 添加连接关系：在电路模型中，器件中添加对应的pin和线；
        for module in self.module_list:
            self.cc.active_module_by_name(module.name)
            # get device
            for attr_dev in module.device_list:
                if isinstance(attr_dev, WireAttrFrame):
                    continue
                self.cc.active_device_by_device(attr_dev.lo)
                # get pins of device
                for item in module.canvas.find_withtag(f'did={attr_dev.did}'):
                    item_type = 'none'
                    all_tags = module.canvas.gettags(item)
                    for tag in all_tags:
                        if tag == 'type=cpin':
                            item_type = tag.split('=')[1]
                        elif tag == 'type=cpout':
                            item_type = tag.split('=')[1]
                        elif tag.startswith('did='):
                            dev_id = int(tag.split("=")[1])
                    if item_type != 'none':
                        wire_id = self._get_connected_wire_id(item)
                        #cp_name = self._get_cp_name(item)
                        #wire_name = self._get_wire_name(wire_id)
                        self.cc.add_connection(item, wire_id)
    def _get_connected_wire_id(self, did):
        """get cp connected wire did by cp did"""
        cp_box = self.cur_module.canvas.bbox(did)
        flag_found_wire = 0
        for one_item in self.cur_module.canvas.find_overlapping(cp_box[0], cp_box[1], cp_box[2], cp_box[3]):
            for one_tag in self.cur_module.canvas.gettags(one_item):
                if 'type=wire' == one_tag:
                    flag_found_wire = 1
                elif one_tag.startswith('did='):
                    wire_id = one_tag.split('=')[1]
            if flag_found_wire:
                return wire_id
        return -1
    def _get_cp_name(self, did):
        """get cp name by did"""
        return self.cur_module.cur_device.get_cp_name_by_id(did)
    def _get_wire_name(self, did):
        """get wire name by did"""
        pass


class SubAttrFrame(Frame):
    """电路逻辑对象的基本属性：
        lo,logic: 指向电路逻辑对象
        name: 属性框内的名称，初始化是模块逻辑名称。"""
    def __init__(self, master):
        super(SubAttrFrame, self).__init__(master)
        #self.mw = master.cc
        self.view = master.view
        self.view = master.view
        self.logic = None
    def _layout(self):
        """layout"""
        body = Frame(self)
        self.body(body)
        body.pack(side=TOP)
        self.buttonbox()
    def set_attr(self, logic):
        """set_attr"""
        self.logic = logic
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, self.logic.name)
        self.init_value()
    def init_value(self):
        """initial device value"""
        pass

class ProjectAttrFrame(SubAttrFrame):
    """Project属性结构：
    name: name Entry
    dir: directory
    """
    def __init__(self, master):
        super(ProjectAttrFrame, self).__init__(master)
        self._layout()
    @property
    def name(self):
        """docstring for name"""
        return self.name_entry.get()
    @property
    def pdir(self):
        """docstring for name"""
        return self.dir_entry.get()
    def body(self, master):
        """docstring for body"""
        Label(master, text=tx.LProjectName).grid(row=0, column=0)
        self.name_entry = Entry(master, text=self.view.project.name)
        self.name_entry.grid(row=0, column=1)
        Label(master, text=tx.LProjectDir).grid(row=1, column=0)
        self.dir_entry = Entry(master, text=self.view.project.dir)
        self.dir_entry.grid(row=1, column=1)
    def buttonbox(self):
        """button"""
        btbox = Frame(self)
        box = Button(btbox, text=tx.aw.reset, width=10, command=self.reset)
        box.grid(row=0, column=0)
        box = Button(btbox, text=tx.aw.newPro, width=20, command=self.view.new_project)
        box.grid(row=1, column=0, columnspan=2)
        box = Button(btbox, text=tx.aw.savePro, width=20, command=self.view.save_project)
        box.grid(row=2, column=0, columnspan=2)
        box = Button(btbox, text=tx.aw.closePro, width=20, command=self.view.close_project)
        box.grid(row=3, column=0, columnspan=2)
        box = Button(btbox, text=tx.aw.openPro, width=20, command=self.view.open_project)
        box.grid(row=4, column=0, columnspan=2)
        btbox.pack(side=TOP)
    def reset(self):
        """reset"""
        self.init_value(self.view.project)
    def init_value(self):
        """set default value"""
        self.dir_entry.delete(0, tk.END)
        self.dir_entry.insert(0, self.logic.dir)

class ModuleAttrFrame(SubAttrFrame):
    """模块属性结构：
    module: cc.module
    name: name Entry
    """
    def __init__(self, master):
        super(ModuleAttrFrame, self).__init__(master)
        self._layout()
    def body(self, master):
        """docstring for body"""
        self.name_entry = Entry(master)
        Label(master, text=tx.LModuleName).grid(row=0, column=0)
        self.name_entry.grid(row=0, column=1)
    def buttonbox(self):
        """button"""
        btbox = Frame(self)
        box = Button(btbox, text=tx.aw.apply, width=10, command=self.ok, default=ACTIVE)
        box.grid(row=0, column=0)
        box = Button(btbox, text=tx.aw.reset, width=10, command=self.reset)
        box.grid(row=0, column=1)
        box = Button(btbox, text=tx.aw.exportPin, width=20, command=self.export_pin)
        box.grid(row=1, column=0, columnspan=2)
        box = Button(btbox, text=tx.aw.importPin, width=20, command=self.import_pin)
        box.grid(row=2, column=0, columnspan=2)
        #box = Button(btbox, text=tx.aw.initView, width=20, command=self.view.init_instance_view)
        #box.grid(row=3, column=0, columnspan=2)
        btbox.pack()
    def ok(self):
        """docstring for ok"""
        # 检查是否能够更新，如果不能，则返回当前值。
        # 更新名称
        new_name = self.name_entry.get()
        self.view.update_module_name(new_name)
    def reset(self):
        """reset"""
        pass
    # def init_value(self, module):
        # """set default value"""
        # self.set_name(module.name)
    # def set_name(self, name=''):
        # """set module name to module entry"""
        # self.name_entry.delete(0, tk.END)
        # self.name_entry.insert(0, name)
        ############# to review
    def add_dev(self):
        """add a device to module"""
        self.device_list.append(self.cur_attr)
    def export_pin(self):
        """export pin to a file in form of config"""
        tleft = []
        tright = []
        ttop = []
        tdown = []
    def import_pin(self):
        """import pin from a file in form of config"""
        data = []
        DiaSelPinFile(self, data)
        ffull_name = data[0]
        self.view.config_pin_from_file(ffull_name)
    def active_attr(self, attr):
        """显示属性"""
        if self.cur_attr is not None:
            self.cur_attr.pack_forget()
        self.cur_attr = attr
        if self.cur_attr is not None:
            self.cur_attr.pack(fill=BOTH)
    def hide_device_win(self, attr):
        """隐藏属性"""
        if attr is None:
            return
        if attr is self.cur_attr:
            attr.pack_forget()
            self.cur_attr = None
    def append_self_instance_inst(self, inst):
        """增加本模块被实例化的一个对象"""
        self.self_instance_inst_list.append(inst)

class DevAttrFrame(SubAttrFrame):
    """基本器件属性框架。
    graph: 器件图形对象。
    """
    def __init__(self, master):
        super(DevAttrFrame, self).__init__(master)
        self._layout()
    def buttonbox(self):
        """button"""
        btbox = Frame(self)
        bok = Button(btbox, text=tx.aw.apply, width=10, command=self.ok, default=ACTIVE)
        bok.pack(side=LEFT)
        bok = Button(btbox, text=tx.aw.reset, width=10, command=self.reset)
        bok.pack(side=LEFT)
        btbox.pack()
    def ok(self):
        """docstring for ok"""
        name = self.name_entry.get()
        self.view.update_device_name(name)
        self.apply()
    def apply(self):
        """应用属性修改。"""
        pass
    def reset(self):
        """docstring for ok"""
        self.init_value()
    def save_data(self):
        """save attribute to database."""
        pass

class SingleDevAttrFrame(DevAttrFrame):
    def __init__(self, master):
        super(SingleDevAttrFrame, self).__init__(master)
    def ok(self):
        """docstring for ok"""
        name = self.name_entry.get()
        self.view.update_device_name(name)
        width = self.width_entry.get()
        self.view.update_device_width(width)
        self.apply()
    def init_value(self):
        """name, width"""
        self.width_entry.delete(0, tk.END)
        self.width_entry.insert(0, self.logic.width)
        self.init_sd()
    def init_sd(self):
        """initial single"""
        pass

class InputAttrFrame(SingleDevAttrFrame):
    def __init__(self, master):
        super(InputAttrFrame, self).__init__(master)
    def body(self, master):
        """docstring for body"""
        self.name_label = Label(master, text=tx.aw.pinName)
        self.name_entry = Entry(master)
        self.width_label = Label(master, text=tx.aw.width)
        self.width_entry = Entry(master)
        self.name_label.grid( row=0, column=0)
        self.name_entry.grid( row=0, column=1)
        self.width_label.grid(  row=1, column=0)
        self.width_entry.grid(  row=1, column=1)

class OutputAttrFrame(SingleDevAttrFrame):
    def __init__(self, master):
        super(OutputAttrFrame, self).__init__(master)
    def body(self, master):
        """docstring for body"""
        self.name_label = Label(master, text="引脚名")
        self.name_entry = Entry(master)
        self.width_label = Label(master, text="位宽")
        self.width_entry = Entry(master)
        self.name_label.grid( row=0, column=0)
        self.name_entry.grid( row=0, column=1)
        self.width_label.grid(  row=1, column=0)
        self.width_entry.grid(  row=1, column=1)

class WireAttrFrame(SingleDevAttrFrame):
    """模块属性结构"""
    def __init__(self, master):
        super(WireAttrFrame, self).__init__(master)
    def body(self, master):
        """wire body"""
        self.name_label = Label(master, text=tx.aw.signalName)
        self.name_entry = Entry(master)
        self.width_label = Label(master, text=tx.aw.width)
        self.width_entry = Entry(master)
        self.name_label.grid( row=0, column=0)
        self.name_entry.grid( row=0, column=1)
        self.width_label.grid(  row=1, column=0)
        self.width_entry.grid(  row=1, column=1)

class InstanceAttrFrame(DevAttrFrame):
    """模块实例属性"""
    def __init__(self, master):
        super(InstanceAttrFrame, self).__init__(master)
    def body(self, master):
        """docstring for body"""
        Label(master, text=tx.aw.name).grid(row=0, column=0)
        self.name_entry = Entry(master)
        self.name_entry.grid(row=0, column=1)
        Label(master, text=tx.aw.refType).grid(row=1, column=0)
        self.ref_type  = Label(master, text='')
        self.ref_type.grid(row=1, column=1)
        Label(master, text=tx.aw.refName).grid(row=2, column=0)
        self.ref_name  = Label(master, text='')
        self.ref_name.grid(row=2, column=1)
    def init_value(self):
        self.ref_type.config(text=self.logic.ref_module.source)
        self.ref_name.config(text=self.logic.ref_module.name)

class RegfileAttrFrame(DevAttrFrame):
    """模块实例属性"""
    def __init__(self, master):
        super(RegfileAttrFrame, self).__init__(master)
    def body(self, master):
        """docstring for body"""
        Label(master, text=tx.aw.name).grid(row=0, column=0)
        self.name_entry = Entry(master)
        self.name_entry.grid(row=0, column=1)
        Label(master, text=tx.aw.element  ).grid(row=1, column=0)
        Label(master, text=tx.aw.row      ).grid(row=2, column=0)
        Label(master, text=tx.aw.column   ).grid(row=3, column=0)
        Label(master, text=tx.aw.rch_count).grid(row=4, column=0)
        Label(master, text=tx.aw.wch_count).grid(row=5, column=0)
        self.element   = Entry(master)
        self.row       = Entry(master)
        self.column    = Entry(master)
        self.rch_count = Entry(master)
        self.wch_count = Entry(master)
        self.element   .grid(row=1, column=1)
        self.row       .grid(row=2, column=1)
        self.column    .grid(row=3, column=1)
        self.rch_count .grid(row=4, column=1)
        self.wch_count .grid(row=5, column=1)
        #self.element.grid(row=1, column=1)
        #self.row.grid(row=1, column=1)
        #self.column.grid(row=1, column=1)
        #self.rch_count.grid(row=1, column=1)
        #self.wch_count.grid(row=1, column=1)
    def init_value(self):
        self.element  .delete(0, tk.END)
        self.row      .delete(0, tk.END)
        self.column   .delete(0, tk.END)
        self.rch_count.delete(0, tk.END)
        self.wch_count.delete(0, tk.END)
        self.element  .insert(0, self.logic.element  )
        self.row      .insert(0, self.logic.row      )
        self.column   .insert(0, self.logic.column   )
        self.rch_count.insert(0, self.logic.rch_count)
        self.wch_count.insert(0, self.logic.wch_count)
    def apply(self):
        """apply"""
        config = {
            "element"   : self.element  .get(),
            "row"       : self.row      .get(),
            "column"    : self.column   .get(),
            "rch_count" : self.rch_count.get(),
            "wch_count" : self.wch_count.get(),
                } 
        self.view.update_regfile(config)


class InverterAttrFrame(SingleDevAttrFrame):
    """模块属性结构"""
    def __init__(self, master, circuit, device):
        super(InverterAttrFrame, self).__init__(master, circuit)
        self.did = device.did

    def body(self, master):
        """docstring for body"""
        pass

    def apply(self):
        """apply"""
        pass


class ClassName(object):
    """docstring for ClassName"""
    def __init__(self, arg):
        super(ClassName, self).__init__()
        self.arg = arg

class BundleReg(DevAttrFrame):
    """docstring for Bundle"""
    def __init__(self, master):
        super(Bundle, self).__init__(master)
        pass
    def body(self, master):
        Label(master, text=tx.aw.name).grid(row=0, column=0)
        self.name_entry = Entry(master)
        self.name_entry.grid(row=0, column=1)
        #hlayout = Frame(master)
        Label(master, text=tx.aw.name).grid(row=1, column=0)
        Label(master, text=tx.aw.width).grid(row=1, column=1)
        Label(master, text=tx.aw.reset).grid(row=1, column=2)
        tscrollbar = tk.Scrollbar(master, orient=tk.VERTICAL)
        self.name_list  = tk.Listbox(master, selectmode=SINGLE, yscrollcommand=tscrollbar.set)
        self.width_list = tk.Listbox(master, selectmode=SINGLE, yscrollcommand=tscrollbar.set)
        self.reset_list = tk.Listbox(master, selectmode=SINGLE, yscrollcommand=tscrollbar.set)
        tscrollbar.config(command=self.module_list.yview)
        self.name_list.grid( row=2, column=0)
        self.width_list.grid(row=2, column=1)
        self.reset_list.grid(row=2, column=2)
        tscrollbar.grid(     row=2, column=3)
        #hlayout.grid(row=1, column=0, columnspan=2)
    def init_value(self):
        for ele in self.logic.elements:
            self.name_list.insert(END, ele.name)
            self.width_list.insert(END, ele.width)
            self.reset_list.insert(END, ele.reset)
        self.ref_type.config(text=device.ref_module.source)
        self.ref_name.config(text=device.ref_module.name)

class VectorAttrFrame(DevAttrFrame):
    """docstring for VectorAttrFrame"""
    def __init__(self, master):
        super(VectorAttrFrame, self).__init__(master)
    def body(self, master):
        """docstring for body"""
        Label(master, text=tx.aw.name).grid(row=0, column=0)
        self.name_entry = Entry(master)
        self.name_entry.grid(row=0, column=1)
        Label(master, text=tx.aw.refType).grid(row=1, column=0)
        self.ref_type  = Label(master, text='')
        self.ref_type.grid(row=1, column=1)
        Label(master, text=tx.aw.refName).grid(row=2, column=0)
        self.ref_name  = Label(master, text='')
        self.ref_name.grid(row=2, column=1)
    def set_attr(self, device):
        self.set_name(device.name)
        self.ref_type.config(text=device.ref_module.source)
        self.ref_name.config(text=device.ref_module.name)
        
class VecRegAttrFrame(DevAttrFrame):
    """docstring for VectorAttrFrame"""
    def __init__(self, master):
        super(VecRegAttrFrame, self).__init__(master)
        
#################
# Dialog
#################

class BDDialog(Toplevel):
    """docstring for BDDialog"""
    def __init__(self, master, title=None):
        super(BDDialog, self).__init__(master)
        self.transient(master)
        if title:
            self.title(title)
        self.master = master
        self.result = None
        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)
        self.buttonbox()
        self.wait_visibility()
        self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (self.master.winfo_rootx()+50,
                                  self.master.winfo_rooty()+50))
        self.initial_focus.focus_set()
        self.wait_window(self)

    # construction hooks
    def body(self, master):
        """to override"""
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden
        pass
    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons
        box = Frame(self)
        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        box.pack()

    #
    # standard button semantics
    def ok(self, event=None):
        """ok button"""
        if not self.validate():
            self.initial_focus.focus_set() # put focus undo
            return
        self.withdraw()
        self.update_idletasks()
        self.apply()
        self.cancel()
    def cancel(self, event=None):
        """cancel button"""
        # put focus undo to the master window
        self.master.focus_set()
        self.destroy()
    #
    # command hooks
    def validate(self):
        """to override"""
        return 1 # override
    def apply(self):
        """to override"""
        pass # override

class DiaSaveProject(BDDialog):
    """docstring for DiaSaveProject"""
    def __init__(self, master, data):
        self.data = data
        super(DiaSaveProject, self).__init__(master, title=tx.MSaveProject)
    def body(self, master):
        """body"""
        Label(master, text=tx.LProjectName).grid(row=0, column=0)
        Label(master, text=tx.LProjectDir).grid(row=1, column=0)
        self.proj_name_entry = Entry(master)
        self.proj_dir_entry = Entry(master)
        self.proj_name_entry.grid(row=0, column=1)
        self.proj_dir_entry.grid(row=1, column=1)
        Button(master, text=tx.LOpen, command=self._open_dir).grid(row=1, column=2)
        self.proj_dir_entry.insert(0, '.')
    def apply(self):
        """apply"""
        lg.debug("inputed circuit name is %s", self.proj_name_entry.get())
        lg.debug("inputed circuit dir is %s", self.proj_dir_entry.get())
        self.data['name'] = self.proj_name_entry.get()
        self.data['dir'] = self.proj_dir_entry.get()
    def _open_dir(self):
        """打开工作目录"""
        dir_name = filedialog.askdirectory()
        self.proj_dir_entry.insert(0, dir_name)

class DiaNewModule(BDDialog):
    """docstring for DiaNewModule"""
    def __init__(self, master, data):
        self.data = data
        super(DiaNewModule, self).__init__(master, title="新建模块")

    def body(self, master):
        """body"""
        Label(master, text="模块名").grid(row=0, column=0)
        self.module_name_entry = Entry(master)
        self.module_name_entry.grid(row=0, column=1)

    def apply(self):
        """apply"""
        self.data['name'] = self.module_name_entry.get()

class DiaInstType(BDDialog):
    """选择模块属性的窗口。
    module: 模块属性"""
    def __init__(self, master, data, module_list):
        self.data = data
        self.module = module_list
        self.mtype = IntVar()
        super(DiaInstType, self).__init__(master, title=tx.InfoInstType)

    def body(self, master):
        """body"""
        # user module
        hlayout = Frame(master)
        tr = tk.Radiobutton(hlayout, text=tx.AttrInstCircuit, value=1, variable=self.mtype)
        tr.pack(side=LEFT)
        tr.select()
        tscrollbar = tk.Scrollbar(hlayout, orient=tk.VERTICAL)
        self.module_list = tk.Listbox(hlayout, selectmode=SINGLE, yscrollcommand=tscrollbar.set)
        for one_m in self.module:
            self.module_list.insert(END, one_m.name)
        tscrollbar.config(command=self.module_list.yview)
        tscrollbar.pack(side=RIGHT, fill=Y)
        self.module_list.pack(side=LEFT, fill=BOTH)
        hlayout.pack(side=TOP, fill=BOTH)
        # empty ref module
        hlayout = Frame(master)
        tk.Radiobutton(hlayout, text=tx.AttrInstEmpty, value=0, variable=self.mtype).pack(side=LEFT)
        Label(hlayout, text=tx.LModuleName).pack(side=LEFT)
        self.empty_name = Entry(hlayout, text='empty')
        self.empty_name.pack(side=LEFT)
        hlayout.pack(side=TOP, fill=BOTH)

    def apply(self):
        """apply"""
        #module_attr = None
        if self.mtype.get() == 0:
            self.data.append(xc.EmptyModule(self.empty_name.get()))
        elif self.mtype.get() == 1:
            self.data.append(self.module[self.module_list.index(tk.ACTIVE)])
        else:
            pass

class DiaSelPinFile(BDDialog):
    """窗口，选择模块引脚分布文件。
    """
    def __init__(self, master, data):
        self.data = data
        super(DiaSelPinFile, self).__init__(master, title=tx.DiaSelFileTitle)
    def body(self, master):
        """body"""
        Label(master, text="引脚文件").grid(row=0, column=0)
        self.in_file = Entry(master)
        self.in_file.grid(row=0, column=1)
        Button(master, text="打开", command=self._open_file).grid(row=0, column=2)
    def _open_file(self):
        """打开文件"""
        self.in_file.delete(0, END)
        file_name = filedialog.askopenfilename()
        self.in_file.insert(0, file_name)
    def apply(self):
        """apply"""
        self.data.append(self.in_file.get())

class DiaSelFile(BDDialog):
    """ask open register bundle define file.
    """
    def __init__(self, master, data, title):
        self.data = data
        super(DiaSelFile, self).__init__(master, title=title)
    def body(self, master):
        """body"""
        Label(master, text=tx.DiaDesignFile).grid(row=0, column=0)
        self.in_file = Entry(master)
        self.in_file.grid(row=0, column=1)
        Button(master, text=tx.DiaAskOpenFile, command=self._open_file).grid(row=0, column=2)
    def _open_file(self):
        """打开文件"""
        self.in_file.delete(0, END)
        file_name = filedialog.askopenfilename()
        self.in_file.insert(0, file_name)
    def apply(self):
        """apply"""
        self.data.append(self.in_file.get())


############
#  funciton
############

def center(bbox):
    """get the center coord of bbox"""
    return [(bbox[0]+bbox[2])/2, (bbox[1]+bbox[3])/2]

def tag_input(name):
    name = f"name={name}"
    tag_type = f"type={pin['type']}"
    tag_shape = "shape=polygon"
    tag_cp = f"cp={pin['cp']}"
    tag_type = "type=input"
    tag_shape = "shape=polygon"
    tag_cp = "cp=0"

def move_connected_wire(wid, moved_point, org_coord, delta_x, delta_y):
    """获得器件目标坐标后，移动器件连接的线。"""
    f_move_succeed = 0
    #wid = wire[0]
    #org_last_point = wire[1] #to moved coord of the wire
    if moved_point == org_coord[0:2]:
        org_coord = revert_wire_coord(org_coord) # 移动的是线的起点，反转后，移动终点。
    new_start_point = org_coord[0:2]
    new_last_point = [moved_point[0] + delta_x, moved_point[1] + delta_y]
    last_sec_p = org_coord[-4:-2]
    last_thr_p = org_coord[-6:-4]
    if last_sec_p[0] == last_thr_p[0]: 
        last_sec_p = [last_sec_p[0], new_last_point[1]]
    else:
        last_sec_p = [new_last_point[0], last_sec_p[1]]
    new_coord = org_coord[0:-4] + last_sec_p + new_last_point
    return new_coord

if __name__ == "__main__":
    print("view.py")

#! $PATH/python
# -*- coding: utf-8 -*-

# file name: action.py
# author: lianghy
# time: 2019/12/13 17:13:33

"""主要功能函数库。库中函数都是能够backward的功能函数。"""

import os
from os.path import isfile, isdir, join
import logging as lg
from io import StringIO
import json
#import circuit as qc
import tkinter as tk
from tkinter import messagebox as xm
import view as xv
import circuit as xc
import text as xt
tx = xt.init_text()

############################# to review

class ClassName(object):
    """docstring for ClassName"""
    def __init__(self, arg):
        super(ClassName, self).__init__()
        self.arg = arg

class ACRecord(object):
    """docstring for ACRecord"""
    def __init__(self):
        super(ACRecord, self).__init__()
        self.act_id = 0
        self.undo_stack = []
        self.redo_stack = []
    # action
    def clear_undo(self):
        """清空backward列表"""
        self.undo_stack.clear()
    def clear_forward(self):
        """清空forward列表"""
        self.redo_stack.clear()
    def clear_history(self):
        """清空undo表"""
        self.undo_stack.clear()
        self.redo_stack.clear()
    def record_act(self, act_type, **argv):
        """record action with name"""
        self.undo_stack.append((act_type, argv))
        self.clear_forward()
    def undo(self):
        """backward操作"""
        if len(self.undo_stack) == 0:
            return
        action = self.undo_stack.pop()
        self.redo_stack.append(action)
        action.undo(self)
        if action[0] == tx.ACTCreateModule:
            module = action[1]['module']
            index = module.index
            self.cc.rm_module_by_index(index)
            self.lw.remove_module(index)
            self.deactive_module()
            lg.info(f"{tx.InfoCancelCreateDevice}: {module.name}")
        elif action[0] == tx.ACTCreateDevice:
            device = action[1]['device']
            if device == self.cc.cur_device:
                self.deactive_device()
            self.cc.del_device(device)
            lg.info(f"{tx.InfoCancelCreateDevice}: {device.name}")
        else:
            raise NotImplementedError
        return
        if action[1] == 'del module':
            index = action[2]['index']
            module = action[2]['module']
            self.cc.cur_module = module
            self.cc.module_list.insert(index, module)
            #self.dw.active_canvas(module.canvas)
            self.aw.active_module()
            self.lw.insert_module(index, module.name)
        elif action.type == 'new device':
            attr = action.aw_stack['device']
            self.hide_item_by_id(attr.did)
            self.aw.cur_module.hide_device_win(attr)
            lg.info(f"undo {action.type}: {action.aw_stack['device'].did}")
        elif action.type == 'change module name':
            last_name = action.aw_stack['last_name']
            action.aw_stack['module'].set_name(last_name)
            self.lw.update_tag_by_id(action.lw_stack['index'], last_name)
            lg.info(f"undo {action.type}: {action.aw_stack['last_name']}")
        else:
            pass
    def forward(self):
        """forward操作"""
        if len(self.redo_stack) == 0:
            return
        action = self.redo_stack.pop()
        self.undo_stack.append(action)
        if action[0] == tx.ACTCreateModule:
            module = action[1]['module']
            index = module.index
            self.lw.insert_module(index, module.name)
            self.cc.insert_module(index, module)
            lg.info(f"{tx.InfoCreateModule}: {module.name}")
        elif action[0] == tx.ACTCreateDevice:
            device = action[1]['device']
            device.pack()
            device.graph.draw()
            lg.info(f"{tx.InfoCreateDevice}: {device.name}")
        else:
            raise NotImplementedError
        return

class ACProject(object):
    """docstring for ACProject"""
    # project
    def new_project(self):
        """new project, check if should save current project"""
        if self.project.exist():
            self.close_project()
        self.project.new_project(self.aw.cur_win.name, self.aw.cur_win.pdir)
        self.clear_history() # undo action will delete the top module!!
        lg.info(tx.ac.newProject + f":{self.project.name}")
    def close_project(self):
        """docstring for close_project"""
        if self.project.is_changed:
            if xm.askokcancel(title=tx.InfoAskSaveProject, message=tx.InfoAskSaveProjectM):
                self.save_project()
        self.project.close_project()
        self.lw.close()
        self.close()
        self.aw.close()
        self.cc.close()
        self.clear_history()
        lg.info(tx.InfoCloseCircuit)
        print("project name is ", self.project.name)
    def save_project(self):
        """docstring for save_project"""
        if isfile(join(self.aw.cur_win.pdir, self.aw.cur_win.name)):
            if not xm.askokcancel(title=tx.InfoAskOverwriteProject, message=tx.InfoAskOverwriteProjectM):
                return
        if self.project.save_project(self.aw.cur_win.name, self.aw.cur_win.pdir):
            self.save_circuit()
    def open_project(self):
        """open a circuit"""
        if self.project.exist():
            lg.info(f"请先关闭当前电路:{self.project.name}")
            return False
        name = self.aw.cur_win.name
        pdir = self.aw.cur_win.pdir
        tfile = join(pdir, name)
        if not isfile(tfile):
            tfile = tk.filedialog.askopenfilename()
            name = os.path.basename(tfile)
            pdir = os.path.abspath(os.path.dirname(tfile))
        #if not tfile.endswith('.xx'):
            #lg.error("电路名称后缀名称不正确（以.xx结尾）")
        try:
            with open(tfile, 'rb') as fin:
                ftext = fin.read()
                data = json.loads(ftext)
            lg.info("打开电路:{}".format(tfile))
            self.project.name = name
            self.project.dir = pdir
        except Exception as exp:
            lg.info("无法打开电路:{}".format(tfile))
            self.close_circuit()
            raise exp
        # load data
        for module in data:
            self.new_module(module['name'])
            for dev in module['input']:
                self.new_input(name=dev['name'], width=dev['width'], coord=dev['coord'])
            for dev in module['output']:
                self.new_output(name=dev['name'], width=dev['width'], coord=dev['coord'])
            for dev in module['inst']:
                self.new_inst(name=dev['name'], coord=dev['coord'], ref_module=dev['ref'])
            for dev in module['wire']:
                tid = self.cc.cur_module.canvas.create_line(dev['coord'])
                self.new_wire(name=dev['name'], width=dev['width'], coord=dev['coord'], tid=tid)
            for dev in module['block']:
                #self.new_block(dev[0], dev[1], dev[2])
                pass
            # set module shape
            pin_location = []
            for location in module['shape']:
                pin_location.append([self.cc.cur_module.get_pin[pin] for pin in location])
            self.cc.cur_module.inst_view.config_pin_placement(pin_location)

    # circuit
    def save_circuit(self):
        circuit = self.cc.save_circuit()
        try:
            with open(self.project.fullname, 'w') as fin:
                output = json.dumps(circuit)
                fin.write(output)
        except Exception as exp:
            lg.error(exp)
            xm.showerror(tx.ErrorModuleName, exp)
        lg.info(f"{tx.InfoSaveCircuit}: {self.project.name}")
    def close_circuit(self):
        """close circuit"""
        lg.info(tx.InfoCloseCircuit)
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.lw.close()
        self.close()
        self.aw.close()
        self.cc.close()

class ACDesign(object):
    """docstring for ACDesign"""
    def create_module(self, name='module'):
        """以默认名称创建模块"""
        self.deactive_device()
        self.new_module(name)
        self.active_module()
        #self.record_act(tx.ACTCreateModule, module=self.cc.cur_module)
        self.record_act(ACTNewModule(self.cc.cur_module))
    def create_input(self, e):
        """以默认名称创建输入端口"""
        name='i_'
        coord = (e.x, e.y)
        self.deactive_device()
        self.new_input(name, '1', coord)
        self.active_device()
        self.record_act(tx.ACTCreateDevice, device=self.cc.cur_device)
        lg.info(f"{tx.InfoCreateInput}: {name}")
        self.end_action()
    def create_output(self, e):
        """以默认名称创建输出端口"""
        name='o_'
        coord = (e.x, e.y)
        self.deactive_device()
        self.new_output(name, '1', coord)
        self.active_device()
        self.record_act(tx.ACTCreateDevice, device=self.cc.cur_device)
        lg.info(f"创建输出 {name}")
        self.end_action()
    def create_inst(self, e):
        """以默认名称创建实例"""
        coord = (e.x, e.y)
        # get module name
        data = [] # get selected module attr frame
        xv.DiaInstType(self.vw, data, self.cc.module_list)
        if data == []:
            return
        ref_module = data[0]
        name = f'u_{ref_module.name}'
        self.deactive_device()
        self.new_inst(name, coord, ref_module)
        self.active_device()
        self.record_act('new device', device=self.cc.cur_device)
        lg.info(f"创建实例 {name}")
        self.end_action()
    def create_regb(self, e):
        """create register bundle"""
        # get module name
        data = [] # get selected module attr frame
        xv.DiaSelFile(self.vw, data, tx.DiaSelFileTitle)
        if data == []:
            return
        name = f'regb_'
        coord = (e.x, e.y)
        self.deactive_device()
        self.new_regb(name, coord, data[0])
        self.active_device()
        self.record_act('new regb', device=self.cc.cur_device)
        lg.info(tx.InfoCreateReg)
        self.end_action()
    def create_regfile(self, e):
        """create register bundle"""
        # get module name
        name = f'rf_'
        coord = (e.x, e.y)
        self.deactive_device()
        self.new_regfile(name, coord)
        self.active_device()
        self.record_act('new regfile', device=self.cc.cur_device)
        lg.info(tx.InfoCreateRegfile)
        self.end_action()
    def create_wire(self, coord, item):
        """以默认名称创建普通连线。"""
        name = "w_"
        self.deactive_device()
        self.new_wire(name, '1', coord, item)
        self.active_device()
        self.record_act('new device', device=self.cc.cur_device)
        lg.info(f"创建线 {name}")
        self.end_action()
    def new_module(self, name='module'):
        """以默认名称创建模块"""
        self.lw.new_module(name) # index
        # canvas
        if self.cur_canvas:
            self.cur_canvas.pack_forget()
        self.cur_canvas = self.dw.new_module()
        self.cc.new_module(name, self.cur_canvas)
        self.bind_mouse_default_action()
    def new_input(self, name, width, coord):
        """以默认名称创建输入端口"""
        self.cc.new_input(name, width, coord)
    def new_output(self, name, width, coord):
        """以默认名称创建输出端口"""
        self.cc.new_output(name, width, coord)
    def new_inst(self, name, coord, ref_module):
        """call create instance function"""
        self.cc.new_inst(name, coord, ref_module)
    def new_regfile(self, name, coord):
        """call create instance function"""
        self.cc.new_regfile(name, coord)
    def new_wire(self, name, width, coord, item):
        """在画布上确定画出线后，再创建线逻辑。"""
        self.cc.new_wire(name, width, coord, item)
    def new_regb(self, name, coord, fname):
        """call create instance function"""
        with open(fname) as fin:
            regb = json.load(fin)
            self.cc.new_regb(name, coord, regb)
    def delete(self):
        """删除动作。"""
        if self.cc.cur_device.name == tx.NameNone:
            self.del_module()
        else:
            self.del_device()
    def del_module(self):
        """删除模块:删除当前激活的模块。"""
        module = self.cc.cur_module
        index = module.index
        self.cc.rm_module_by_index(index)
        self.lw.remove_module(index)
        self.deactive_module()
        lg.info(f"删除模块:{module.name}")
        self.record_act('del module', module=module)
    def del_device(self):
        """删除器件:删除当前激活的器件。"""
        device = self.cc.cur_device
        self.cc.del_device()
        self.aw.active_module(self.cc.cur_module)
        self.record_act('del device', device=device)
        lg.info(f"删除器件:{device.name}")
    def move_device(self):
        """移动器件。如果当前选中器件，则直接移动；如果没有，则进行选择器件过程。
        移动器件时，会同时移动器件连接的线。
        移动的起始点是器件的坐标。"""
        # for multi devices, create new device type to support this function.
        if isinstance(self.cc.cur_device, xc.LWire):
            self.bind_move_wire()
            #self.end_move_wire()
            raise NotImplementedError("移动线")
        elif self.cc.cur_device:
            lg.debug("move device: %s", self.cc.cur_device.name)
            start_point = self.cc.cur_device.graph.coord
            lg.debug(f"start move device {start_point}")
            self.bind_move_device(start_point)
            #self.end_move_device() # for multi devices movement.
        else:
            lg.warning("请选择器件")
    def config_pin_placement(self, fname):
        with open(tname, 'rb') as fin:
            ftext = fin.read()
        ports = json.loads(ftext)
        port_location = []
        for side in ports:
            port_location.append([self.cur_device.module.get_port(name) for name in ports])
        self.cur_device.set_inst_view(port_location)

    ## no record action: only front end action
    def active_project(self):
        """docstring for active_project"""
        self.deactive_device()
        self.aw.active_project()
    def active_module(self, index=None):
        """激活模块。当前模块或列表窗口选中的模块。"""
        self.deactive_device()
        self.cc.active_module_by_index(index)
        self.lw.active_module_by_index(self.cc.cur_module.index)
        self.aw.active_module(self.cc.cur_module)
        lg.debug("激活模块: %s", self.cc.cur_module.name)
    def deactive_module(self, index=None):
        """不激活任何模块。"""
        self.cc.deactive_module()
        self.deactive_module()
        self.aw.deactive_module()
    def active_device(self, item_id=None):
        """激活器件。当前器件或当前canvas选中的器件。"""
        if item_id is not None:
            if self.cc.cur_device:
                if item_id in self.cc.cur_device.graph.all_items:
                    return
        self.cc.active_device(item_id)
        self.aw.active_device(self.cc.cur_device)
        lg.debug("激活器件: %s", self.cc.cur_device.name)
    def deactive_device(self):
        """不激活当前器件。"""
        if self.cc.cur_device:
            self.cc.deactive_device()
        self.aw.deactive_device()
    def active_module_by_name(self, name=''):
        """根据模块名激活模块:属性、逻辑"""
        if not name == '':
            for mod in self.cc.module_list:
                if name == mod.name:
                    self.cc.cur_module = mod
                    break
        self.active_module()
    ###module related function
    def init_instance_view(self):
        """initial instance view"""
        self.cc.cur_module.init_instance_view()
        #self.clear_undo()
        #self.clear_forward()
    def update_module_name(self, name):
        """修改模块名称"""
        last_name = self.cc.cur_module.name
        if last_name == name:
            return
        # 电路逻辑修改模块名称(当前module就是要修改的)
        self.cc.cur_module.name = name
        # lw窗口修改模块名称(当前tag就是要修改的)
        self.lw.update_tag(name)
        self.record_act('change module name', last_name=last_name)
        lg.info(f'修改模块名:{last_name} 变为 {name}')
    def update_device_name(self, new_name):
        """set device name from attribute."""
        old_name = self.cc.cur_device.name
        if old_name == new_name:
            return
        self.cc.cur_device.name = new_name
        self.cc.cur_device.graph.update_name()
        self.record_act('change device name', last_name=old_name)
        #lg.info(f'修改器件名:{last_name} 变为 {name}')
        lg.info(tx.InfoDevUpdateName.format(old_name, new_name))
    def update_device_width(self, new_width):
        """set device width from attribute."""
        old_width = self.cc.cur_device.width
        if old_width == new_width:
            return
        self.cc.cur_device.width = new_width
        self.record_act('change device width', last_width=old_width)
        #lg.info(f'修改器件位宽:{last_width} 变为 {width}')
        lg.info(tx.InfoDevUpdateName.format(old_width, new_width))
    def update_regfile(self, config):
        """update regfile configuration"""
        self.cc.cur_device.update_config(config)
        self.cc.cur_device.graph.update()
    def get_all_cp(self):
        """得到当前器件的所有连接点。"""
        return self.cc.cur_device.graph.get_all_cp()

class ACEvent(object):
    """docstring for ACEvent"""
    def __init__(self):
        super(ACEvent, self).__init__()
        self.temp_coord = []
        self.temp_item = []
        self.md_connected_wire = []  # 与当前移动器件相连的线did, 连接点移动前的中心坐标, 线的连接点顺序:1=正序（连接点是线的最后一个坐标点）-1=倒序
    def end_action(self):
        """end the action."""
        self.bind_mouse_default_action()
    ## mouse action
    def bind_mouse_default_action(self):
        """bind"""
        lg.debug("bind mouse action")
        self.cur_state = 'idle'
        #self.bind("<ButtonPress-1>", self._bind_select) # this does not work
        self.cur_canvas.bind("<ButtonPress-1>", self._bind_select)
        #self.cur_canvas.bind("<ButtonRelease-1>", self._button_release)
        #self.cur_canvas.bind("<ButtonRelease-3>", self._cancle)
        #self.cur_canvas.bind("<B1-Motion>", self._button_motion)
        self.cur_canvas.bind("<ButtonPress-3>", self._null)
        self.cur_canvas.bind("<Motion>", self._null)
        self.bind_top_key_default()
    def bind_top_key_default(self):
        """bind"""
        self.root.bind("<Escape>", self._escape)
    def _bind_select(self, event):
        '''select module, device, or point or segment of a wire.
        '''
        #self._drag_data["item"] = self.cur_canvas.find_closest(event.x, event.y)[0]
        #self._drag_data["item"] = self.cur_canvas.find_enclosed(event.x-1, event.y-1, event.x+1, event.y+1)[0]
        ids = self.cur_canvas.find_overlapping(event.x-5, event.y-5, event.x+5, event.y+5)
        #if isinstance(self.cur_graph, xg.GWire):
        if isinstance(self.cc.cur_device, xc.LWire):
            for one in ids:
                tags = self.cur_canvas.gettags(one)
                if tx.TagFlagPoint in tags:
                    if self.cur_graph.select_point(one):
                        # selece flag point of the wire again
                        return
        for one in ids:
            if tx.TagFlagPoint in self.cur_canvas.gettags(one):
                # flag point is not in the all_items of a device.
                continue
            #self.event_x = event.x
            #self.event_y = event.y
            self.deactive_device()
            self.active_device(ids[0])
            break
        else:
            self.active_module_by_name()
    def bind_new_input(self):
        """设置鼠标行为，选择器件起始点。"""
        self._escape(None)
        self.cur_canvas.bind("<ButtonPress-1>", self.create_input)
    def bind_new_output(self):
        """设置鼠标行为，选择器件起始点。"""
        self._escape(None)
        self.cur_canvas.bind("<ButtonPress-1>", self.create_output)
    def bind_new_inst(self):
        """设置鼠标行为，选择器件起始点。"""
        self._escape(None)
        self.cur_canvas.bind("<ButtonPress-1>", self.create_inst)
    def bind_new_regb(self):
        """create bundle of register."""
        self._escape()
        self.cur_canvas.bind("<ButtonPress-1>", self.create_regb)
    def bind_new_regfile(self):
        """create bundle of register."""
        self._escape()
        self.cur_canvas.bind("<ButtonPress-1>", self.create_regfile)
    def bind_new_wire(self):
        """设置鼠标行为，选择起始连接点，设置新的鼠标行为。"""
        self._escape()
        self.cur_canvas.bind("<ButtonPress-1>", self._create_temp_wire)
    def bind_move_device(self, start_point):
        """移动器件"""
        self._escape(None)
        self.cur_state = "move_device"
        for cp_coord in self.get_all_cp():
            self._get_dev_connected_wire(cp_coord)
        self.temp_coord.append(start_point)
        self.cur_graph.coord = start_point
        self.cur_canvas.bind("<Motion>", self._show_device_md)
        self.cur_canvas.bind("<ButtonPress-1>", self._get_end_point_md)
    def bind_move_wire(self):
        """移动线，只移动线的线段。"""
        self._escape(None)
        #self.cur_canvas.bind("<Motion>", self._indicate_moveable_segment)
        self.cur_canvas.bind("<ButtonPress-1>", self._get_start_point_mw)
        self.cur_state = "move_wire"
    def _cancle(self, event=None):
        """取消当前行为。"""
        self._escape(None)
    def _null(self, event):
        """no action"""
        pass

    ## action
    def _end_action(self):
        """succeed in finishing one action."""
        self.md_connected_wire.clear()
        self.temp_item.clear()
        self.temp_coord.clear()
        self.bind_mouse_default_action()
    def _escape(self, event=None):
        """cancel current action"""
        if self.cur_state == "move_device":
            dx = self.cur_graph.coord[0] - self.temp_coord[-1][0]
            dy = self.cur_graph.coord[1] - self.temp_coord[-1][1]
            for item in self.cur_items:
                self.cur_canvas.move(item, dx, dy)
        for item in self.temp_item:
            self.cur_canvas.delete(item)
        self.temp_coord.clear()
        self.cur_state = 'idle'
        self.bind_mouse_default_action()
    # wire related
    def _create_temp_wire(self, event):
        """找到线的起点:在鼠标附件查找cp；画临时的线。"""
        cp = self.find_cp(event.x, event.y)
        if cp is None:
            self._cancle()
            return
        #tbox = [cp[0], cp[1], cp[0]+4, cp[1], cp[0]+8, cp[1]]
        tbox = [cp[0], cp[1], cp[0]+4, cp[1]]
        tag_type = "type=wire"
        tags = (tag_type)
        tid = self.cur_canvas.create_line(tbox, tags=tags)
        self.temp_item.append(tid) # 画默认的线
        self.cur_canvas.bind("<ButtonPress-3>", self._get_next_point_wire)
        self.cur_canvas.bind("<ButtonPress-1>", self._get_end_point_wire)
        self.cur_canvas.bind("<Motion>", self._show_line_wire)
    def _get_next_point_wire(self, event):
        """get next cp = the second point of the temp wire """
        item = self.temp_item[-1]
        tbox = self.cur_canvas.coords(item)
        new_coord = tbox + [tbox[-2]+4, tbox[-1]]
        self.cur_canvas.coords(item, new_coord)
        if self.check_line_cross_device():
            self._cancle()
    def _get_end_point_wire(self, event):
        """找到终点，开始生成线。重置鼠标行为。"""
        # 根据cp点调整最后一个segment的位置.
        # 需要判断当前线上是否只有一个segment。
        cp = self.find_cp(event.x, event.y)
        if cp is None:
            self._cancle()
            return
        item = self.temp_item[-1]
        tbox = self.cur_canvas.coords(item)
        start_x = tbox[-4]
        start_y = tbox[-3]
        dx = cp[0] - start_x
        dy = cp[1] - start_y
        if len(tbox) > 4:
            # more than one point
            fix_point = tbox[:-4]
            #new_point = tbox[-4:-2]
            new_point = [cp[0], cp[1]]
            if tbox[-6] == tbox[-4]:
                # same x: vertical
                start_point = [start_x, cp[1]]
            else:
                start_point = [cp[0], start_y]
            new_coord = fix_point + start_point + new_point
        else:
            fix_point = tbox[:-2]
            if cp[0] == start_x:
                mid_p = [cp[0], (cp[1]+start_y)//2]
            else:
                mid_p = [(cp[0]+start_x)//2, cp[1]]
            new_coord = fix_point + mid_p + mid_p + cp
        self.cur_canvas.coords(item, new_coord)
        self._end_action()
        self.create_wire(new_coord, item)
    def _show_line_wire(self, event):
        """draw temp wire line from last point."""
        item = self.temp_item[-1]
        tbox = self.cur_canvas.coords(item)
        start_x = tbox[-4]
        start_y = tbox[-3]
        dx = event.x - start_x
        dy = event.y - start_y
        if len(tbox) > 4:
            # more than two point
            fix_point = tbox[:-4]
            #new_point = tbox[-4:-2]
            new_point = [event.x, event.y]
            if tbox[-6] == tbox[-4]:
                # same x: vertical
                start_point = [start_x, event.y]
            else:
                start_point = [event.x, start_y]
            new_coord = fix_point + start_point + new_point
        else:
            fix_point = tbox[:-2]
            if abs(dx) > abs(dy):
                new_point = [event.x, start_y]
            else:
                new_point = [start_x, event.y]
            new_coord = fix_point + new_point
        self.cur_canvas.coords(item, new_coord)
    def find_cp(self, x, y):
        """search for a cp near the cursor, return coord."""
        ids = self.cur_canvas.find_overlapping(x-3, y-3, x+3, y+3)
        if ids:
            for one_id in ids:
                tags = self.cur_canvas.gettags(one_id)
                for one_tag in tags:
                    if one_tag.startswith("cp"):
                        dev_coord = self.cur_canvas.coords(one_id)
                        cp_coord = dev_coord[0:2]
                        # cp_index = one_tag.split("=")[1]
                        # dev_coord = self.cur_canvas.coords(one_id)
                        # cp_coord = dev_coord[int(cp_index):int(cp_index)+2]
                        return cp_coord
        lg.debug("do not find cp in %s,%s", x,y)
        return None
    def check_line_cross_device(self):
        """return True if line cross divecs."""
        return False
    # move action
    def _show_device_md(self, event):
        """show device when move the mouse."""
        dx = event.x-self.temp_coord[-1][0]
        dy = event.y-self.temp_coord[-1][1]
        self.temp_coord[0] = [event.x, event.y]
        for item in self.cur_items:
            self.cur_canvas.move(item, dx, dy)
    def _get_end_point_md(self, event):
        """get the end point and move all connected wires."""
        # 方案：重新布线从线的与移动点相连的第二个和第三个点之间的线段。
        # 不支持增加新的线段，只能调整当前线段与被移动器件相连的两段区间。
        delta_x = event.x - self.cur_graph.coord[0]
        delta_y = event.y - self.cur_graph.coord[1]
        for one_wire in self.md_connected_wire:
            wid = one_wire[0]
            moved_point = one_wire[1]
            org_coord = self.cur_canvas.coords(wid)
            new_coord = move_connected_wire(wid, moved_point, org_coord, delta_x, delta_y)
            self.cur_canvas.coords(wid, new_coord)
        self.cur_graph.coord = (event.x, event.y)
        self.active_device()
        self._end_action()
    def _get_dev_connected_wire(self, cp_coord):
        """获取所有与器件相连的线。"""
        # 获取所有的线，检查线的哪个端点在bbox中。
        # 使用cp+/-1来查找线。
        bbox = [cp_coord[0]-1, cp_coord[1]-1, cp_coord[0]+1, cp_coord[1]+1,]
        for one_id in self.cur_canvas.find_overlapping(bbox[0], bbox[1], bbox[2], bbox[3]):
            tags = self.cur_canvas.gettags(one_id)
            if 'type=wire' in tags:
                #wire_coord = self.cur_canvas.coords(one_id)
                self.md_connected_wire.append([one_id, cp_coord]) # wire id and connect point
    def _get_start_point_mw(self, e):
        """获取要移动的线段。"""
        raise NotImplementedError("移动线")
        to_move_seg = xa.get_to_move_seg((e.x, e.y), self.cur_canvas.coord(self.cur_items[0]))
        self.cur_canvas.bind("<Motion>", self._show_wire_mw)

    def close(self):
        """关闭"""
        self.cur_canvas = None
        self.cur_state = 'idle'
        self.temp_coord = []
        self.temp_item = []
        self.md_connected_wire = []

    def hide_item_by_id(self, did):
        """hide item ty id"""
        # TODO: remove.
        for item in self.cur_canvas.find_withtag(xg.tag_did(did)):
            self.cur_canvas.itemconfig(item, state=tk.HIDDEN)
    def deactive_module(self):
        """关闭所有canvas。"""
        self.cur_canvas.pack_forget()
        self.cur_canvas = None

class ACType(object):
    """docstring for ACType"""
    def __init__(self):
        super(ACType, self).__init__()
        self.arg = None
        pass

class ACTNewModule(ACType):
    """docstring for ACTNewModule"""
    def __init__(self, module):
        super(ACTNewModule, self).__init__()
        self.module = module
        lg.info(f"{tx.InfoCreateModule}: {self.module.name}")
    def undo(self, ac):
        index = self.module.index
        ac.cc.rm_module_by_index(index)
        ac.lw.remove_module(index)
        ac.deactive_module()
        lg.info(f"{tx.InfoCancelCreateDevice}: {self.module.name}")
    def redo(self, ac):
        index = self.module.index
        self.lw.insert_module(index, self.module.name)
        self.cc.insert_module(index, self.module)
        lg.info(f"{tx.InfoCreateModule}: {self.module.name}")

class Action(ACRecord, ACProject, ACEvent, ACDesign):
    """docstring for ACDesign

    * create_*: actions triggered by toolbar or mouse
    * new_*: create a new element of circuit
    * undo stack = [function, [win list]]
    * del_module = [id, 'del module', module, index, command]
    """
    def __init__(self, root):
        super(Action, self).__init__()
        self.root = root
        self.state = 'IDLE'
        self.cur_canvas = None
    # 查找属性: TODO: move to circuit
    @property
    def cur_items(self):
        """当前器件的所有部分的canvas items id."""
        return self.cc.cur_device.graph.items
    @property
    def cur_graph(self):
        """当前器件的图形."""
        return self.cc.cur_device.graph

    def link(self, project, window, circuit, logic):
        """link front and backend"""
        self.project = project
        self.cc = circuit
        self.vw = window
        self.lc = logic
        self.tw = window.tw
        self.lw = window.lw
        self.dw = window.dw
        self.aw = window.aw


def revert_wire_coord(coord):
    """将canvas的wire坐标反转。"""
    t = []
    new_coord = []
    for x in range(0, len(coord), 2):
        t.append(coord[x:x+2])
    t.reverse()
    for x in t:
        new_coord.extend(x)
    return new_coord


class NormalAC:
    """normal action"""
    pass


        #self.ac.clear_undo() # undo action will delete the top module!!
if __name__ == "__main__":
    print("action.py")

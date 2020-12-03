#! $PATH/python
# -*- coding: utf-8 -*-

# file name: action.py
# author: lianghy
# time: 2019/12/13 17:13:33

"""主要功能函数库。库中函数都是能够backward的功能函数。"""

import os
from os.path import isfile, isdir, join
import logging as lg
import json
#import circuit as qc
import tkinter as tk
from tkinter import messagebox as xm
import view as xv
import circuit as xc
import text as xt

class ActionRecord(object):
    """
    * back stack = [function, [win list]]
    * del_module = [id, 'del module', module, index, command]
    """
    def __init__(self, aid, act_type, lw_stack=None, dw_stack=None, aw_stack=None, mf_stack=None, df_stack=None):
        super(ActionRecord, self).__init__()
        self.id = aid
        self.type = act_type
        self.lw_stack = lw_stack
        self.dw_stack = dw_stack
        self.aw_stack = aw_stack
        self.mf_stack = mf_stack # module frame
        self.df_stack = df_stack # device frame

class Action(object):
    """
    * back stack = [function, [win list]]
    * new 开头的函数是鼠标引发的动作
    """
    def __init__(self):
        super(Action, self).__init__()
        self.act_id = 0
        self.back_stack = []
        self.forward_stack = []
        self.name = ''
        self.dir = '.'
    def link(self, circuit, logic, view):
        """link front and backend"""
        self.cc = circuit
        self.lc = logic
        self.vw = view
        self.tw = self.vw.tw
        self.lw = self.vw.lw
        self.dw = self.vw.dw
        self.aw = self.vw.aw
    def end_action(self):
        """end the action."""
        self.dw.bind_mouse_default_action()

    def create_module(self, name='module'):
        """以默认名称创建模块"""
        self.deactive_device()
        self.new_module(name)
        self.active_module()
        self.record_act(xt.ACTCreateModule, module=self.cc.cur_module)
        lg.info(f"创建新模块:{name}")
    def create_input(self, e):
        """以默认名称创建输入端口"""
        name='i_'
        coord = (e.x, e.y)
        self.deactive_device()
        self.new_input(name, '1', coord)
        self.active_device()
        self.record_act(xt.ACTCreateDevice, device=self.cc.cur_device)
        lg.info(f"{xt.InfoCreateInput}: {name}")
        self.end_action()
    def create_output(self, e):
        """以默认名称创建输出端口"""
        name='o_'
        coord = (e.x, e.y)
        self.deactive_device()
        self.new_output(name, '1', coord)
        self.active_device()
        self.record_act(xt.ACTCreateDevice, device=self.cc.cur_device)
        lg.info(f"创建输出 {name}")
        self.end_action()
    def create_inst(self, e):
        """以默认名称创建实例"""
        coord = (e.x, e.y)
        # get module name
        module_attr = [] # get selected module attr frame
        xv.DiaSelModule(self.vw, module_attr, self.cc.module_list)
        if module_attr == []:
            return
        ref_module = module_attr[0]
        name = f'u_{ref_module.name}'
        self.deactive_device()
        self.new_inst(name, coord, ref_module)
        self.active_device()
        self.record_act('new device', device=self.cc.cur_device)
        lg.info(f"创建实例 {name}")
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
    def new_module(self, name):
        """以默认名称创建模块"""
        self.lw.new_module(name) # index
        self.dw.new_module() # canvas
        self.cc.new_module(name, self.dw.cur_canvas)
    def new_input(self, name, width, coord):
        """以默认名称创建输入端口"""
        self.cc.new_input(name, width, coord)
    def new_output(self, name, width, coord):
        """以默认名称创建输出端口"""
        self.cc.new_output(name, width, coord)
    def new_inst(self, name, coord, ref_module):
        """call create instance function"""
        self.cc.new_inst(name, coord, ref_module)
    def new_wire(self, name, width, coord, item):
        """在画布上确定画出线后，再创建线逻辑。"""
        self.cc.new_wire(name, width, coord, item)

    def delete(self):
        """删除动作。"""
        if self.cc.cur_device.name == xt.NameNone:
            self.del_module()
        else:
            self.del_device()
    def del_module(self):
        """删除模块:删除当前激活的模块。"""
        module = self.cc.cur_module
        index = module.index
        self.cc.del_module_by_index(index)
        self.lw.remove_module(index)
        self.deactive_module()
        lg.info(f"删除模块:{module.name}")
        self.record_act('del module', module=module)
    def del_device(self):
        """删除器件:删除当前激活的器件。"""
        device = self.cc.cur_device
        self.deactive_device()
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
            self.dw.bind_move_wire()
            #self.end_move_wire()
            raise NotImplementedError("移动线")
        elif self.cc.cur_device:
            lg.debug("move device: %s", self.cc.cur_device.name)
            start_point = self.cc.cur_device.graph.coord
            lg.debug(f"start move device {start_point}")
            self.dw.bind_move_device(start_point)
            #self.end_move_device() # for multi devices movement.
        else:
            lg.warning("请选择器件")

    ## no record action: only front end action
    def active_module(self, index=None):
        """激活模块。当前模块或列表窗口选中的模块。"""
        self.deactive_device()
        self.cc.active_module_by_index(index)
        self.lw.active_module_by_index(self.cc.cur_module.index)
        self.aw.active_module(self.cc.cur_module)
        self.dw.active_canvas(self.cc.cur_module.canvas)
        lg.debug("激活模块: %s", self.cc.cur_module.name)
    def deactive_module(self, index=None):
        """不激活任何模块。"""
        self.cc.deactive_module()
        self.dw.deactive_module()
        self.aw.deactive_module()
    def active_device(self, item_id=None):
        """激活器件。当前器件或当前canvas选中的器件。"""
        self.deactive_device()
        self.cc.active_device(item_id)
        self.aw.active_device(self.cc.cur_device)
        lg.debug("激活器件: %s", self.cc.cur_device.name)
    def deactive_device(self):
        """不激活当前器件。"""
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
        """修改模块属性"""
        self.cc.cur_module.init_instance_view()
        #self.clear_back()
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
    def set_cur_device_name(self, name):
        """set device name from attribute."""
        last_name = self.cc.cur_device.name
        self.cc.cur_device.name = name
        self.record_act('change device name', last_name=last_name)
        lg.info(f'修改器件名:{last_name} 变为 {name}')
    def set_cur_device_width(self, width):
        """set device width from attribute."""
        last_width = self.cc.cur_device.width
        self.cc.cur_device.width = width
        self.record_act('change device width', last_width=last_width)
        lg.info(f'修改器件位宽:{last_width} 变为 {width}')
    def get_all_cp(self):
        """得到当前器件的所有连接点。"""
        cps = []
        if isinstance(self.cc.cur_device, xc.LPort):
            cps.append(self.cc.cur_module.canvas.coords(self.cc.cur_device.graph.items[0])[0:2])
        elif isinstance(self.cc.cur_device, xc.LInst):
            for x in self.cc.cur_device.graph.items[1:]:
                cps.append(self.cc.cur_module.canvas.coords(x)[0:2])
        return cps

    # 查找属性
    @property
    def cur_items(self):
        """当前器件的所有部分的canvas items id."""
        return self.cc.cur_device.graph.items
    @property
    def cur_graph(self):
        """当前器件的图形."""
        return self.cc.cur_device.graph

    ############################# to review
    def new_circuit(self):
        """关闭当前电路；设置电路名称"""
        self.close_circuit()
        lg.info("新建电路")
        self.clear_back() # back action will delete the top module!!
    def open_circuit(self):
        """open a circuit"""
        if self.name != '':
            lg.info("请先关闭当前电路")
            return False
        tfile = tk.filedialog.askopenfilename()
        #if not tfile.endswith('.xx'):
            #lg.error("电路名称后缀名称不正确（以.xx结尾）")
        try:
            with open(tfile, 'rb') as fin:
                ftext = fin.read()
                data = json.loads(ftext)
            lg.info("打开电路:{}".format(tfile))
            self.name = os.path.basename(tfile)
            self.dir = os.path.abspath(os.path.dirname(tfile))
        except Exception as exp:
            lg.debug(exp)
            lg.info("无法打开电路:{}".format(tfile))
            self.close_circuit()
            return False
        # load data
        for module in data:
            self.new_module(module[0])
            for dev in module[1]:
                self.new_input(dev[0], dev[1], dev[2])
            for dev in module[2]:
                self.new_output(dev[0], dev[1], dev[2])
            for dev in module[4]:
                tid = self.cc.cur_module.canvas.create_line(dev[2])
                self.new_wire(dev[0], dev[1], dev[2], tid)
            for dev in module[5]:
                #self.new_block(dev[0], dev[1], dev[2])
                pass
            pin_location = []
            for location in module[6]:
                pin_location.append([self.cc.cur_module.get_pin[pin] for pin in location])
            self.cc.cur_module.inst_view.config_pin_placement(pin_location)
        for module in data:
            for dev in module[3]:
                for one_m in self.cc.module_list:
                    if one_m.name == dev[2]:
                        ref_module = one_m
                        break
                self.new_inst(dev[0], dev[1], ref_module)
    def save_circuit(self):
        """save circuit."""
        # 询问电路目录和名称
        # 检查目录存在
        # 创建电路文件
        if self.name == '':
            # save as
            data = {"name":'default', 'dir':'.'}
            xv.DiaNewProject(self.vw, data)
            if data['name'].isidentifier():
                self.name = data['name']
                if not isdir(data['dir']):
                    self.dir = "."
                else:
                    self.dir = data['dir']
            else:
                message = xt.MessageCheckCircuitName
                lg.error(message)
                xm.showerror(xt.ErrorModuleName, message)
                return
            project_name = join(self.dir, self.name)
            if isfile(project_name):
                if not xm.askokcancel(title=xt.InfoAskOverwriteProject, message=xt.InfoAskOverwriteProjectM):
                    return
        project_name = join(self.dir, self.name)
        # save data
        data = self.cc.save_circuit()
        print("debug", data)
        with open(project_name, 'w') as fin:
            output = json.dumps(data)
            fin.write(output)
        lg.info(f"{xt.InfoSaveCircuit}: {project_name}")
    def close_circuit(self):
        """close circuit"""
        lg.info(xt.InfoCloseCircuit)
        self.back_stack.clear()
        self.forward_stack.clear()
        self.lw.close()
        self.dw.close()
        self.aw.close()
        self.cc.close()
        self.name = ""


    ## 动作记录
    def record_act(self, act_type, **argv):
        """record action with name"""
        self.back_stack.append((act_type, argv))
        self.clear_forward()
    def back(self):
        """backward操作"""
        if len(self.back_stack) == 0:
            return
        action = self.back_stack.pop()
        self.forward_stack.append(action)
        if action[0] == xt.ACTCreateModule:
            module = action[1]['module']
            index = module.index
            self.cc.del_module_by_index(index)
            self.lw.remove_module(index)
            self.deactive_module()
            lg.info(f"{xt.InfoCancelCreateDevice}: {module.name}")
        elif action[0] == xt.ACTCreateDevice:
            device = action[1]['device']
            if device == self.cc.cur_device:
                self.deactive_device()
            self.cc.del_device(device)
            lg.info(f"{xt.InfoCancelCreateDevice}: {device.name}")
        else:
            raise NotImplementedError
        return
        if action[1] == 'del module':
            index = action[2]['index']
            module = action[2]['module']
            self.cc.cur_module = module
            self.cc.module_list.insert(index, module)
            self.dw.active_canvas(module.canvas)
            self.aw.active_module()
            self.lw.insert_module(index, module.name)
        elif action.type == 'new module':
            self.lw.del_module_by_index(action.lw_stack['item'])
            self.dw.hide_canvas(action.dw_stack['canvas'])
            self.aw.hide_module_win(action.aw_stack['module'])
            lg.info(f"back {action.type}: {action.lw_stack['module_name']}")
        elif action.type == 'new device':
            attr = action.aw_stack['device']
            self.dw.hide_item_by_id(attr.did)
            self.aw.cur_module.hide_device_win(attr)
            lg.info(f"back {action.type}: {action.aw_stack['device'].did}")
        elif action.type == 'change module name':
            last_name = action.aw_stack['last_name']
            action.aw_stack['module'].set_name(last_name)
            self.lw.update_tag_by_id(action.lw_stack['index'], last_name)
            lg.info(f"back {action.type}: {action.aw_stack['last_name']}")
        else:
            pass
    def forward(self):
        """forward操作"""
        # next: 0，恢复创建模块，创建器件。
        if len(self.forward_stack) == 0:
            return
        action = self.forward_stack.pop()
        self.back_stack.append(action)
        if action[0] == xt.ACTCreateModule:
            module = action[1]['module']
            index = module.index
            self.lw.insert_module(index, module.name)
            self.cc.insert_module(index, module)
            lg.info(f"{xt.InfoCreateModule}: {module.name}")
        elif action[0] == xt.ACTCreateDevice:
            device = action[1]['device']
            device.pack()
            device.graph.draw()
            lg.info(f"{xt.InfoCreateDevice}: {device.name}")
        else:
            raise NotImplementedError
        return
    def clear_back(self):
        """清空backward列表"""
        self.back_stack.clear()
    def clear_forward(self):
        """清空forward列表"""
        for action in self.forward_stack:
            if action[0] == 'new module':
                module = action[1]['module']
                self.cc.module_list.remove(module)
                module.canvas.destroy()
                del(module)
            else:
                lg.info("还未实现")
            return


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

if __name__ == "__main__":
    print("action.py")

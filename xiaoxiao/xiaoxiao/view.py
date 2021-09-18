#! $PATH/python
# -*- coding: utf-8 -*-

# file name: view.py
# author: lianghy
# time: 2019/5/8 22:46:56

"""基本器件图形。
cp: 标记此器件有连接点，器件连接点都是图形的第一个点。
items: 图形对象的id。默认第一个是图形外框。
coord: the origin point of the border.
    When create a new shape, create it at (0, 0) and then move it to coord.
"""

import os
from os.path import isfile
import logging as lg
import tkinter as tk

import window
import text as xt
tx = xt.init_text()

class View(object):
    """docstring for View"""
    def __init__(self, pj, ac=None):
        super(View, self).__init__()
        self.project = pj
        self.ac = ac
        self.module_list = []
        self.device_list = []
        # mouse action
        self.ac_move = ACMoveObj()
        self.temp_coord = []
        self.temp_item = []
        self.md_connected_wire = []  # 与当前移动器件相连的线did, 连接点移动前的中心坐标, 线的连接点顺序:1=正序（连接点是线的最后一个坐标点）-1=倒序
        self._mouse_enter_item = None
    def init_gui(self):
        """start gui"""
        self.root = tk.Tk()
        self.mw = window.MainWin(self.root, self, self.ac)
        w = 1400
        h = 800
        #w = root.winfo_screenwidth() - 20
        #h = root.winfo_screenheight() - 100
        x = 0
        y = 0
        self.root.geometry("%dx%d+%d+%d" %(w,h,x,y))
        #root.attributes("-topmost",True)
    def start_gui(self):
        self.root.mainloop()
    ## project
    def new_project(self):
        """new project, check if should save current project"""
        if self.project.exist():
            self.close_project()
        self.project.new_project(self, self.mw.aw.cur_win.name, self.mw.aw.cur_win.pdir)
        #self.clear_history() # undo action will delete the top module!! TODO: do not record action which not trigger by mouse.
        lg.info(tx.ac.newProject + f":{self.project.name}")
    def close_project(self):
        """docstring for close_project"""
        if not self.project.exist():
            return
        if self.project.is_changed:
            if xm.askokcancel(title=tx.InfoAskSaveProject, message=tx.InfoAskSaveProjectM):
                self.save_project()
        self.project.close()
        self.view.close_project()
        #self.project.circuit.close()
        #self.clear_history()
        lg.info(tx.InfoCloseCircuit)
    def save_project(self):
        """docstring for save_project"""
        if not self.project.exist():
            return
        if isfile(join(self.mw.aw.cur_win.pdir, self.mw.aw.cur_win.name)):
            if not xm.askokcancel(title=tx.InfoAskOverwriteProject, message=tx.InfoAskOverwriteProjectM):
                return
        if self.project.save_project(self.mw.aw.cur_win.name, self.mw.aw.cur_win.pdir):
            self.save_circuit()
    def open_project(self):
        """open a circuit"""
        if self.project.exist():
            lg.info(f"请先关闭当前电路:{self.project.name}")
            return False
        name = self.mw.aw.cur_win.name
        pdir = self.mw.aw.cur_win.pdir
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
                tid = self.project.circuit.cur_module.canvas.create_line(dev['coord'])
                self.new_wire(name=dev['name'], width=dev['width'], coord=dev['coord'], tid=tid)
            for dev in module['block']:
                #self.new_block(dev[0], dev[1], dev[2])
                pass
            # set module shape
            pin_location = []
            for location in module['shape']:
                pin_location.append([self.project.circuit.cur_module.get_pin[pin] for pin in location])
            self.project.circuit.cur_module.inst_view.config_pin_placement(pin_location)

    # circuit
    def save_circuit(self):
        circuit = self.project.circuit.save_circuit()
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
        self.mw.lw.close()
        self.close()
        self.mw.aw.close()
        #self.project.circuit.close()
    def active_project(self):
        """docstring for active_project"""
        self.deactive_device()
        self.mw.aw.active_project()
    def deactive_device(self):
        """不激活当前器件。"""
        try:
            self.project.circuit.cur_device.deactive()
            self.project.circuit.cur_device = None
        except:
            pass
    def active_module_by_index(self, index=None):
        if index is None:
            return
        self.active_module(self.project.circuit.module_list[index])
    def active_module(self, md=None):
        """激活模块。当前模块或列表窗口选中的模块。"""
        if md is not None:
            if self.project.circuit.cur_module:
                self.project.circuit.cur_module.deactive()
            self.deactive_device()
            self.project.circuit.cur_module = md
        self.project.circuit.cur_module.active()
        self.mw.aw.active_module(self.project.circuit.cur_module)
        self.mw.lw.active_module_by_index(self.project.circuit.module_list.index(self.project.circuit.cur_module))
        lg.debug((tx.ac.activeModule+" %s"), self.project.circuit.cur_module.name)
    def deactive_module(self, index=None):
        """不激活任何模块。"""
        if self.project.circuit.cur_module:
            self.project.circuit.cur_module.deactive()
        self.project.circuit.cur_module = None
        self.mw.aw.deactive()
    def active_device_by_id(self, item_id=None):
        """激活器件。当前器件或当前canvas选中的器件。"""
        if item_id is not None:
            if self.project.circuit.cur_device:
                if item_id in self.project.circuit.cur_device.graph.all_items:
                    return
            self.project.circuit.active_device(item_id)
        self.mw.aw.active_device(self.project.circuit.cur_device)
        lg.debug("激活器件: %s", self.project.circuit.cur_device.name)
    def active_device(self, dev=None):
        """激活器件。当前器件或当前canvas选中的器件。"""
        if dev:
            if dev == self.project.circuit.cur_device:
                return
            if self.project.circuit.cur_device:
                self.project.circuit.cur_device.deactive()
            self.project.circuit.cur_device = dev
            self.project.circuit.cur_device.active()
        self.mw.aw.active_device(self.project.circuit.cur_device)
        lg.debug("active device: %s", self.project.circuit.cur_device.name)
    def active_module_by_name(self, name=''):
        """根据模块名激活模块:属性、逻辑"""
        if not name == '':
            for mod in self.project.circuit.module_list:
                if name == mod.name:
                    self.project.circuit.cur_module = mod
                    break
        self.active_module()
    ###module related function
    def init_instance_view(self):
        """initial instance view"""
        self.project.circuit.cur_module.init_instance_view()
        #self.clear_undo()
        #self.clear_forward()
    def update_module_name(self, name):
        """修改模块名称"""
        last_name = self.project.circuit.cur_module.name
        if last_name == name:
            return
        # 电路逻辑修改模块名称(当前module就是要修改的)
        self.project.circuit.cur_module.name = name
        # lw窗口修改模块名称(当前tag就是要修改的)
        self.mw.lw.update_tag(name)
        #self.record_act('change module name', last_name=last_name)
        lg.info(f'修改模块名:{last_name} 变为 {name}')
    def update_device_name(self, new_name):
        """set device name from attribute."""
        old_name = self.project.circuit.cur_device.name
        if old_name == new_name:
            return
        self.project.circuit.cur_device.name = new_name
        lg.info(tx.InfoDevUpdateName.format(old_name, new_name))
    def update_device_width(self, new_width):
        """set device width from attribute."""
        old_width = self.project.circuit.cur_device.width
        if old_width == new_width:
            return
        self.project.circuit.cur_device.width = new_width
        #self.record_act('change device width', last_width=old_width)
        #lg.info(f'修改器件位宽:{last_width} 变为 {width}')
        lg.info(tx.InfoDevUpdateName.format(old_width, new_width))
    def update_regfile(self, config):
        """update regfile configuration"""
        self.project.circuit.cur_device.update_config(config)
        self.project.circuit.cur_device.graph.update()
    def get_all_cp(self):
        """得到当前器件的所有连接点。"""
        return self.project.circuit.cur_device.graph.get_all_cp()
    def close_project(self):
        """close project."""
        self.mw.lw.close()
        self.mw.aw.close()
        if self.project.circuit.cur_module:
            self.project.circuit.cur_module.canvas.pack_forget()
        self.project.circuit.cur_module = None
        self.project.circuit.cur_device = None
        self.temp_coord = []
        self.temp_item = []
        self.md_connected_wire = []
    def new_module(self, name='module'):
        self.project.circuit.new_module(name, tk.Canvas(self.mw.dw, bg='white', width=400, height=400))
        self.mw.lw.new_module(self.project.circuit.cur_module.name) # index
        #md = Module(md, tk.Canvas(self.mw.dw, bg='white', width=400, height=400))
        #self.module_list.append(md)
        self.bind_mouse_default_action()
    def create_inst(self, e):
        """以默认名称创建实例"""
        coord = (e.x, e.y)
        # get module name
        data = [] # get selected module attr frame
        xv.DiaInstType(self.mw, data, self.project.circuit.module_list)
        if data == []:
            return
        ref_module = data[0]
        name = f'u_{ref_module.name}'
        self.deactive_device()
        self.project.circuit.cur_device = self.project.circuit.cur_module.new_inst(name, coord, ref_module)
        self.active_device()
        self.record_act('new device', device=self.project.circuit.cur_device)
        lg.info(f"创建实例 {name}")
        self.end_action()
    def create_input(self, e):
        """以默认名称创建输入端口"""
        name='i_'
        coord = (e.x, e.y)
        self.deactive_device()
        self.project.circuit.new_input(name, '1', coord)
        self.active_device()
        lg.info(f"{tx.InfoCreateInput}: {name}")
        self.end_action()
    ## mouse action
    def end_action(self):
        """end the action."""
        self.bind_mouse_default_action()
    def bind_mouse_default_action(self):
        """bind"""
        self.cur_state = 'idle'
        self.project.circuit.cur_module.canvas.bind("<ButtonPress-1>", self._bind_button_left_click)
        #self.bind("<ButtonPress-1>", self._bind_select) # this does not work
        #self.project.circuit.cur_module.canvas.bind("<ButtonRelease-1>", self._button_release)
        #self.project.circuit.cur_module.canvas.bind("<ButtonRelease-3>", self._cancle)
        #self.project.circuit.cur_module.canvas.bind("<B1-Motion>", self._button_motion)
        #self.project.circuit.cur_module.canvas.bind("<ButtonPress-3>", self._null)
        #self.project.circuit.cur_module.canvas.bind("<Motion>", self._null)
        self.bind_top_key_default()
    def bind_top_key_default(self):
        """bind"""
        self.root.bind("<Escape>", self._escape)
    def _bind_button_left_click(self, event):
        '''select module.'''
        if self._mouse_enter_item:
            self.active_device(self._mouse_enter_item)
            return
        self.deactive_device()
        self.active_module()
    def mouse_enter_item(self, dev):
        """docstring for mouse_enter_item"""
        self._mouse_enter_item = dev
    def mouse_leave_item(self, dev):
        """docstring for mouse_enter_item"""
        if self._mouse_enter_item == dev:
            self._mouse_enter_item = None
    def bind_new_input(self):
        """设置鼠标行为，选择器件起始点。"""
        self._escape(None)
        self.project.circuit.cur_module.canvas.bind("<ButtonPress-1>", self.create_input)
    def bind_new_output(self):
        """设置鼠标行为，选择器件起始点。"""
        self._escape(None)
        self.project.circuit.cur_module.canvas.bind("<ButtonPress-1>", self.create_output)
    def bind_new_inst(self):
        """设置鼠标行为，选择器件起始点。"""
        self._escape(None)
        self.project.circuit.cur_module.canvas.bind("<ButtonPress-1>", self.create_inst)
    def bind_new_regb(self):
        """create bundle of register."""
        self._escape()
        self.project.circuit.cur_module.canvas.bind("<ButtonPress-1>", self.create_regb)
    def bind_new_regfile(self):
        """create bundle of register."""
        self._escape()
        self.project.circuit.cur_module.canvas.bind("<ButtonPress-1>", self.create_regfile)
    def bind_new_wire(self):
        """设置鼠标行为，选择起始连接点，设置新的鼠标行为。"""
        self._escape()
        self.project.circuit.cur_module.canvas.bind("<ButtonPress-1>", self._create_temp_wire)
    def bind_move_device(self, start_point):
        """移动器件"""
        self._escape(None)
        self.cur_state = "move_device"
        for cp_coord in self.get_all_cp():
            self._get_dev_connected_wire(cp_coord)
        self.temp_coord.append(start_point)
        self.cur_graph.coord = start_point
        self.project.circuit.cur_module.canvas.bind("<Motion>", self._show_device_md)
        self.project.circuit.cur_module.canvas.bind("<ButtonPress-1>", self._get_end_point_md)
    def bind_move_wire(self):
        """移动线，只移动线的线段。"""
        self._escape(None)
        #self.project.circuit.cur_module.canvas.bind("<Motion>", self._indicate_moveable_segment)
        self.project.circuit.cur_module.canvas.bind("<ButtonPress-1>", self._get_start_point_mw)
        self.cur_state = "move_wire"
    def _cancle(self, event=None):
        """取消当前行为。"""
        self._escape(None)
    def _null(self, event):
        """no action"""
        pass

    ## action
    def _end_action(self):
        """sucircuiteed in finishing one action."""
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
                self.project.circuit.cur_module.canvas.move(item, dx, dy)
        for item in self.temp_item:
            self.project.circuit.cur_module.canvas.delete(item)
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
        tid = self.project.circuit.cur_module.canvas.create_line(tbox, tags=tags)
        self.temp_item.append(tid) # 画默认的线
        self.project.circuit.cur_module.canvas.bind("<ButtonPress-3>", self._get_next_point_wire)
        self.project.circuit.cur_module.canvas.bind("<ButtonPress-1>", self._get_end_point_wire)
        self.project.circuit.cur_module.canvas.bind("<Motion>", self._show_line_wire)
    def _get_next_point_wire(self, event):
        """get next cp = the second point of the temp wire """
        item = self.temp_item[-1]
        tbox = self.project.circuit.cur_module.canvas.coords(item)
        new_coord = tbox + [tbox[-2]+4, tbox[-1]]
        self.project.circuit.cur_module.canvas.coords(item, new_coord)
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
        tbox = self.project.circuit.cur_module.canvas.coords(item)
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
        self.project.circuit.cur_module.canvas.coords(item, new_coord)
        self._end_action()
        self.create_wire(new_coord, item)
    def _show_line_wire(self, event):
        """draw temp wire line from last point."""
        item = self.temp_item[-1]
        tbox = self.project.circuit.cur_module.canvas.coords(item)
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
        self.project.circuit.cur_module.canvas.coords(item, new_coord)
    def find_cp(self, x, y):
        """search for a cp near the cursor, return coord."""
        ids = self.project.circuit.cur_module.canvas.find_overlapping(x-3, y-3, x+3, y+3)
        if ids:
            for one_id in ids:
                tags = self.project.circuit.cur_module.canvas.gettags(one_id)
                for one_tag in tags:
                    if one_tag.startswith("cp"):
                        dev_coord = self.project.circuit.cur_module.canvas.coords(one_id)
                        cp_coord = dev_coord[0:2]
                        # cp_index = one_tag.split("=")[1]
                        # dev_coord = self.project.circuit.cur_module.canvas.coords(one_id)
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
            self.project.circuit.cur_module.canvas.move(item, dx, dy)
    def _get_end_point_md(self, event):
        """get the end point and move all connected wires."""
        # 方案：重新布线从线的与移动点相连的第二个和第三个点之间的线段。
        # 不支持增加新的线段，只能调整当前线段与被移动器件相连的两段区间。
        delta_x = event.x - self.cur_graph.coord[0]
        delta_y = event.y - self.cur_graph.coord[1]
        for one_wire in self.md_connected_wire:
            wid = one_wire[0]
            moved_point = one_wire[1]
            org_coord = self.project.circuit.cur_module.canvas.coords(wid)
            new_coord = move_connected_wire(wid, moved_point, org_coord, delta_x, delta_y)
            self.project.circuit.cur_module.canvas.coords(wid, new_coord)
        self.cur_graph.coord = (event.x, event.y)
        self.active_device()
        self._end_action()
    def _get_dev_connected_wire(self, cp_coord):
        """获取所有与器件相连的线。"""
        # 获取所有的线，检查线的哪个端点在bbox中。
        # 使用cp+/-1来查找线。
        bbox = [cp_coord[0]-1, cp_coord[1]-1, cp_coord[0]+1, cp_coord[1]+1,]
        for one_id in self.project.circuit.cur_module.canvas.find_overlapping(bbox[0], bbox[1], bbox[2], bbox[3]):
            tags = self.project.circuit.cur_module.canvas.gettags(one_id)
            if 'type=wire' in tags:
                #wire_coord = self.project.circuit.cur_module.canvas.coords(one_id)
                self.md_connected_wire.append([one_id, cp_coord]) # wire id and connect point
    def _get_start_point_mw(self, e):
        """获取要移动的线段。"""
        raise NotImplementedError("移动线")
        to_move_seg = xa.get_to_move_seg((e.x, e.y), self.project.circuit.cur_module.canvas.coord(self.cur_items[0]))
        self.project.circuit.cur_module.canvas.bind("<Motion>", self._show_wire_mw)

    def close(self):
        """关闭"""
        self.project.circuit.cur_module.canvas = None
        self.cur_state = 'idle'
        self.temp_coord = []
        self.temp_item = []
        self.md_connected_wire = []

    def hide_item_by_id(self, did):
        """hide item ty id"""
        # TODO: remove.
        for item in self.project.circuit.cur_module.canvas.find_withtag(xg.tag_did(did)):
            self.project.circuit.cur_module.canvas.itemconfig(item, state=tk.HIDDEN)

class ACMoveObj(object):
    """docstring for ACMoveObj"""
    def __init__(self):
        super(ACMoveObj, self).__init__()
        self.start_point = (0,0)
        pass

if __name__ == "__main__":
    print("graph.py")

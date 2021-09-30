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

import logging as lg
import text as xt
tx = xt.init_text()

class VDevice(object):
    """docstring for VDevice
        * first item in all items is main frame item
        * c: controler, hear is view
        """
    _fp_shape = (-3,-3, 3,3)
    def __init__(self, c, did, coord, canvas):
        super(VDevice, self).__init__()
        self.config = VConfig()
        self.c = c
        self.coord = coord
        self.canvas = canvas
        self.all_items = []
        self._fp_items = [] #[id1, id2...]
        #self._fp_coords = [] #[(x1,y1), (x2,y2)...]
        self.tags = [f'id={did}']
    def draw(self):
        self.draw_items()
        self.move_all()
    def draw_items(self):
        self.draw_main_frame()
        self.draw_fp()
    def move_all(self):
        """move all items."""
        for item in self.all_items:
            self.canvas.move(item, self.coord[0], self.coord[1])
    def get_all_cp(self):
        pass
    def deactive(self):
        for item in self._fp_items:
            self.canvas.itemconfig(item, state='hidden')
            #self.canvas.itemconfigure(item, width=0, fill=self.main_frame.color)
    def active(self):
        for item in self._fp_items:
            #self.canvas.itemconfigure(item, width=1, fill=self.main_frame.color)
            self.canvas.itemconfig(item, state='normal')
    def _move(self, item):
        self.canvas.move(item, self.coord[0], self.coord[1])
    def mouse_in(self, e):
        """on device"""
        self.c.mouse_enter_item(self)
    def mouse_ou(self, e):
        """leave device"""
        self.c.mouse_leave_item(self)

class VPort(VDevice):
    """端口。
    * shape 是图形主要外形。
    """
    def __init__(self, c, did, coord, canvas):
        super(VPort, self).__init__(c, did, coord, canvas)
        self.tags.append('cp')
    def vpin(self, side, coord):
        pass

class VPortIn():
    """端口。
    * main_frame_shape 是图形主要外形。
    """
    def __init__(self):
        super(VPortIn, self).__init__()
        self.main_frame = [15,5, 10,10, 0,10, 0,0, 10,0]

class VWire(VDevice):
    """docstring for VWire"""
    def __init__(self, coord, canvas, logic):
        super(VWire, self).__init__(coord, canvas, logic)
        self.shape = [self.coord[0], self.coord[1], self.coord[0]+5, self.coord[1]]
    def init_wire(self):
        self.coord = self.find_cp(self.canvas, self.coord)
        if not self.coord:
            return False
        self.shape = [self.coord[0], self.coord[1], self.coord[0]+5, self.coord[1]]
        self.draw_main_frame()
        self.canvas.bind("<ButtonPress-3>", self._get_next_point_wire)
        self.canvas.bind("<ButtonPress-1>", self._get_end_point_wire)
        self.canvas.bind("<Motion>", self._show_line_wire)
        return True
    def draw_main_frame(self):
        tid = self.canvas.create_line(self.shape)
        self.all_items.append(tid)
    def redraw(self):
        self.canvas.coords(self.all_items[0], self.shape)
    def _add_next_point(self, event):
        """add a turn point to wire """
        self.shape.append(self.shape[-2]+4)
        self.shape.append(self.shape[-2])
    def _finish_wire(self, event):
        cp = self.find_cp(self.canvas, (event.x, event.y))
        if cp is None:
            return
        ex = cp[0]
        ey = cp[1]
        if self._has_two_point():
            if self._move_dir_horizon(ex, ey):
                mid_p = [(ex+self.shape[0])//2, ey]
            else:
                mid_p = [ex, (ey+self.shape[1])//2]
            self.shape.extend(mid_p)
            self.shape.extend(mid_p)
        mx = self.shape[-4]
        my = self.shape[-3]
        self._add_point_to_fold_line(mx, my, ex, ey)
        self.redraw()
    def _show_line_wire(self, event):
        """draw temp wire line from last point."""
        mx = self.shape[-4]
        my = self.shape[-3]
        if self._has_two_point():
            self._adjust_end_point(event.x, envent.y)
        else:
            self._add_point_to_fold_line(mx, my, event.x, event.y)
        self.redraw()
    def _has_two_point(self):
        return len(self.shape) == 4
    def _move_dir_horizon(self, x, y):
        return abs(x-self.shape[-4]) > abs(y-self.shape[-3])
    def _last_segment_vertical(self):
        return self.shape[-6] == self.shape[-4] # same x: vertical
    def _add_point_to_fold_line(self, mx, my, ex, ey):
        fix_point = self.shape[:-4]
        new_point = [ex, ey]
        if self._last_segment_vertical():
            mid_point = [mx, ey]
        else:
            mid_point = [ex, my]
        self.shape = fix_point + mid_point + new_point
    def _adjust_end_point(self, ex, ey):
        fix_point = self.shape[:-2]
        if self._move_dir_horizon(ex, ey):
            new_point = [ex, my]
        else:
            new_point = [mx, ey]
        self.shape = fix_point + new_point
    def _add_2_mid_point(self, ex, ey):
        # TODO
        pass

class SModule():
    """ symbol layout
          X = (-20,0)  Y = (0,0)
                      
                     +----------+               \n
                     | top pin  |               \n
          X----------Y----------+------------+  \n
          | left pin | main box |  right pin |  \n
          +----------+          +------------+  \n
                     |          |               \n
          +----------+          +------------+  \n
          | left pin | main box |  right pin |  \n
          +----------+----------+------------+  \n
                     | down pin |               \n
                     +----------+               \n
          \n
    """
    _name_coord = (5, 2)
    def __init__(self):
        self._size = (60, 40) # initial size: x_coord(h), y_coord(v)
        self._pin_space = (8, 8) # the increased length when adding one pin.
        self._pin_size = (6, 6)
        self.size = [0, 0]
        #self.pin_items = []
        self.pins_location = [[],[],[],[]] # [l, r, t, b]
        #self.item_block.append(self.pin_items)
        self.main_frame = []
        self.pin_symbols = []
    def init_pin_placement(self, port_list):
        """reset placement. defaltly place all pins on top."""
        self.pins_location = [[],[],[],[]] # [l, r, t, b]
        for port in port_list:
            self.pins_location[2].append(port)
        self._place_pin()
    def _place_pin(self):
        """generate pin shapes from port， """
        lpins = self.pins_location[0]
        rpins = self.pins_location[1]
        tpins = self.pins_location[2]
        bpins = self.pins_location[3]
        #重新计算实例大小。
        #初始化尺寸_size = 20 x 20;
        #左右两边最多的引脚数决定长度：20 + len * 8。
        #上下两边最多的引脚数决定宽度：20 + len * 8。
        #每边第一个引脚对齐主框；每个引脚相对上一个引脚偏移8。
        # 主框
        self.size = self._size
        len_v = max(len(lpins), len(rpins))
        len_h = max(len(tpins), len(dpins))
        new_x = self.size[0] + self._pin_space[0]*len_h
        new_y = self.size[1] + self._pin_space[1]*len_v
        self.size = (new_x, new_y)
        # 引脚
        x = -1 * self._pin_size[0]
        y = 0
        for port in lpins:
            self.pin_symbols.append(port.gen_pin_symbol((x,y), 'l'))
            y += self._pin_space[1]
        x = self.size[0]
        y = 0
        for port in rpins:
            self.pin_symbols.append(port.gen_pin_symbol((x,y), 'r'))
            y += self._pin_space[1]
        x = 0
        y = -1 * self._pin_size[1]
        for port in tpins:
            self.pin_symbols.append(port.gen_pin_symbol((x,y), 't'))
            x += self._pin_space[0]
        x = 0
        y = self.size[1]
        for port in bpins:
            self.pin_symbols.append(port.gen_pin_symbol((x,y), 'b'))
            x += self._pin_space[0]
        self.main_frame = [0, 0, self.size[0], self.size[1]]
        #placed_pin_count = sum(len(x) for x in pin_location)
        #if placed_pin_count != pin_count:
            #lg.error(f"引脚数目不全，还缺少{pin_count - placed_pin_count}个引脚没有定义位置")
    def set_inst_pins_location(self, port_location=[]):
        """ set a different pins_location shape different from module default one. """
        self.pins_location = port_location

class SPin():
    """实例端点.
    coord 是pin相对实例原点的坐标。
    标签中有名称，用于在查找线的连接关系时，指示pin的信息。"""
    def __init__(self, coord, side):
        super(SPin, self).__init__()
        self.coord = coord
        self.side = side
        self.tags = ['pin']
    def draw(self, tags, canvas):
        """在画布上绘图。"""
        item = canvas.create_polygon(self.pin_shape_all[self.side], fill='black', tags=self.tags+tags)
        canvas.move(item, self.coord[0], self.coord[1])
        return [item]

class SPinIn(SPin):
    """实例输入端点：三角形。"""
    pin_shape_all = {
            'l': [0,3, 0,0, 6,3, 0,6],
            'r': [6,3, 6,6, 0,3, 6,0],
            't': [3,0, 6,0, 3,6, 0,0],
            'b': [3,6, 0,6, 3,0, 6,6]
            }
    def __init__(self, coord, side):
        super(SPinIn, self).__init__(coord, side)
        self.tags = ['pin_in', 'cp']

class SPinOut(SPin):
    """实例输出端口：菱形。"""
    pin_shape_all = {
            'l': [0,3, 3,0, 6,3, 3,6],
            'r': [6,3, 3,6, 0,3, 3,0],
            't': [3,0, 6,3, 3,6, 0,3],
            'b': [3,6, 0,3, 3,0, 6,3]
            }
    def __init__(self, tag, coord, side):
        super(SPinOut, self).__init__(tag, coord, side)
        self.tags = ['pin_out', 'cp']

def find_cp(canvas, coord):
    """search for a cp near the cursor, return coord."""
    x = coord[0]
    y = coord[1]
    ids = canvas.find_overlapping(x-3, y-3, x+3, y+3)
    if ids:
        for one_id in ids:
            tags = canvas.gettags(one_id)
            for one_tag in tags:
                if one_tag.startswith("cp"):
                    dev_coord = canvas.coords(one_id)
                    cp_coord = dev_coord[0:2]
                    # cp_index = one_tag.split("=")[1]
                    # dev_coord = self.cur_canvas.coords(one_id)
                    # cp_coord = dev_coord[int(cp_index):int(cp_index)+2]
                    return cp_coord
    lg.debug("do not find cp in %s,%s", x,y)
    return None

if __name__ == "__main__":
    print("graph.py")

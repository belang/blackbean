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

class VConfig:
    """graph config options."""
    def __init__(self):
        self.show_name = False # show name in graph
    def config(self, **config):
        for key, value in config.items():
            setattr(self, key, value)

class SymbolC(object):
    """docstring for Symbol"""
    def __init__(self, color='black'):
        super(SymbolC, self).__init__()
        self.color = 'black'
        self.shape = None

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
        self.main_frame = SymbolC(color='black')
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
    #return self.pin_view(self.name, side, coord)
    def draw_main_frame(self):
        item = self.canvas.create_polygon(self.main_frame.shape, fill=self.main_frame.color, tags=self.tags, disabledoutline='blue')
        #self.canvas.move(item, self.coord[0], self.coord[1])
        self.canvas.tag_bind(item, sequence='<Enter>', func=self.mouse_in, add=None)
        self.canvas.tag_bind(item, sequence='<Leave>', func=self.mouse_ou, add=None)
        self.all_items.append(item)
    def draw_fp(self):
        """draw flag points."""
        length = len(self.main_frame.shape)
        i = 0
        while i < length:
            x = self.main_frame.shape[i]
            i += 1
            y = self.main_frame.shape[i]
            i += 1
            item = self.canvas.create_rectangle(self._fp_shape, fill='light blue', tags=tx.TagFlagPoint, state='disabled')
            self._fp_items.append(item)
            self.all_items.append(item)
            self.canvas.move(item, x, y)

class VPortIn(VPort):
    """端口。
    * shape 是图形主要外形。
    """
    def __init__(self, c, did, coord, canvas):
        super(VPortIn, self).__init__(c, did, coord, canvas)
        self.main_frame.shape = [15,5, 10,10, 0,10, 0,0, 10,0]
        self.tags.append('dev=input')

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
    def __init__(self):
        self.pin = {'l':[], 'r':[], 't':[], 'd':[]}
        self.main_frame = SymbolC(color='black')
        self._size = (40, 40) # initial size: x_coord(h), y_coord(v)
        self._pin_space = (8, 8) # the increased length when adding one pin.
        self._pin_size = (6, 6)
        self.size = [0, 0]
        self.pin_items = []
        self.pins = [[],[],[],[]] # [l, r, t, d]
        self.item_block.append(self.pin_items)
        self.config.config(show_name=True)
        self.init_pin_placement()
    def init_pin_placement(self):
        """generate pin shapes from port，
        元素是每个边的引脚列表，依次为左、右、上、下
        """
        self.view.append([])
        self.view.append([])
        self.view.append([])
        self.view.append([])
        lpins = self.view[0]
        rpins = self.view[1]
        tpins = self.view[2]
        dpins = self.view[3]
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
        for pin in lpins:
            self._add_pin(self.pins[0], pin, (x,y), 'l')
            y += self._pin_space[1]
        x = self.size[0]
        y = 0
        for pin in rpins:
            self._add_pin(self.pins[1], pin, (x,y), 'r')
            y += self._pin_space[1]
        x = 0
        y = -1 * self._pin_size[1]
        for pin in tpins:
            self._add_pin(self.pins[2], pin, (x,y), 't')
            x += self._pin_space[0]
        x = 0
        y = self.size[1]
        for pin in tpins:
            self._add_pin(self.pins[3], pin, (x,y), 'd')
            x += self._pin_space[0]
        #placed_pin_count = sum(len(x) for x in pin_location)
        #if placed_pin_count != pin_count:
            #lg.error(f"引脚数目不全，还缺少{pin_count - placed_pin_count}个引脚没有定义位置")
    def set_inst_view(self, port_location=[]):
        """ set a different view shape different from module default one. """
        self.view = port_location
    def _add_pin(self, plist, port, coord, side):
        """向单元中增加一个引脚摆放。"""
        plist.append(port.gen_pin(port.name, coord, self.canvas, side))

    @property
    def mbox(self):
        """main box"""
        x0 = 0
        x1 = 0
        y0 = self.size[0]
        y1 = self.size[1]
        return (x0, x1, y0, y1)

class VInst(VDevice):
    """instance:
        * first item in all items is main frame item"""
    def __init__(self, c, did, coord, canvas):
        super(VDevice, self).__init__(c, did, coord, canvas)
        self.tags.append('inst')
        self._config = {}
        self.place_pin()
    def place_pin(self, config_file=None):
        if config_file:
            #config_pin_from_file()
            pass
        else:
            for port in self.ref_module.port_list:
                if port.ptype == "I":
                    self.pin_config['l'].append(port.name)
                    self.pin.append(port.vpin('l', coord))
                else:
                    self.pin['r'].append(port.vpin('r'))
    def draw_items(self):
        self.draw_main_frame()
        self.draw_pin()
        self.draw_sub_shape()
        self.draw_text()
        self.move_all_item()
    def move_all_item(self):
        for item in self.all_items:
            self._move(item)
    def draw_main_frame(self):
        item = self.canvas.create_rectangle(self.ref_module.symbol.main_frame.shape, tags=self.tags, disabledoutline='blue')
        self.all_items.append(item)
    def draw_pin(self):
        coord = (0,0)
        self._draw_pin(self.pin['l'], coord)
        self._draw_pin(self.pin['r'], coord)
    def _draw_pin(self, pins, coord):
        for pin in pins:
            item = self.canvas.create_polygon(pin.main_frame.shape, tags=pin.tags)
            self.canvas.move(item, coord[0], coord[1])
            self.all_items.append(item)
    def draw_sub_shape(self):
        pass
    def draw_text(self):
        for label in self.text:
            self.all_items.append(self.canvas.create_text(label['coord'], text=label['text'], tags=self.tags, anchor='nw'))

class VUInst(VInst):
    """view of user module"""
    _name_coord = (5, 2)
    def __init__(self, logic, coord, canvas):
        super(VUInst, self).__init__(logic, coord, canvas)
        self.arg = arg
        self.main_frame.shape = [0,0, 50,50]
        self.sub_shape = []
        self.text = [{'text':self.name, 'coord':self._name_coord},
                ]

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

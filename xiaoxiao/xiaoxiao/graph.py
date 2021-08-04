#! $PATH/python
# -*- coding: utf-8 -*-

# file name: graph.py
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

class GConfig:
    """graph config options."""
    def __init__(self):
        self.show_name = False # show name in graph
    def config(self, **config):
        for key, value in config.items():
            setattr(self, key, value)

class Graph:
    """器件图形。
    * canvas: the canvas items are draw in
    * coord: 是器件相对图形原点的坐标，仅在初始化时有效。
    * fp_items: only created and showed when the Device is selected.
    * shape 是图形主要外形。
    """
    fp_shape = (-3,-3, 3,3)
    def __init__(self, coord, canvas, logic = None):
        self.coord = coord
        self.canvas = canvas
        self.logic = logic
        self.config = GConfig()
        self._name_coord = (5, 2)
        self.item_block = []
        self.name_items = []
        self.main_frame_items = []
        self.item_block.append(self.main_frame_items)
        self.item_block.append(self.name_items)
        self.fp_items = [] #[id1, id2...]
        self.fp_coords = [] #[(x1,y1), (x2,y2)...]
        self.shape = []
    @property
    def all_items(self):
        ta = []
        for item_l in self.item_block:
            ta.extend(item_l)
        return ta
    @property
    def border_coord(self):
        """main border coords"""
        for it in self.main_frame_items:
            return self.canvas.coords(it)
        return (0, 0)
    def _draw_flag_point(self): 
        """draw flag point to the seleted shape."""
        for coord in self.fp_coords:
            item = self.canvas.create_rectangle(self.fp_shape, fill='light blue', tags=tx.TagFlagPoint)
            self.fp_items.append(item)
            self.canvas.move(item, coord[0], coord[1])
    def active(self):
        """激活器件。画器件选中时的标记点。
        #历史方法：默认item第一个对象是外框。在外框坐标上画小方框。#"""
        #self.canvas.itemconfig(self.items[0], state='disabled')
        self._compute_flag_point()
        self._draw_flag_point()
        self._active()
    def deactive(self):
        """不激活器件。默认item第一个对象是外框。"""
        #self.canvas.itemconfig(self.items[0], state='normal')
        for item in self.fp_items:
            self.canvas.delete(item)
        self.fp_items.clear()
        self.fp_coords.clear()
    def _compute_flag_point(self):
        """计算标记点。"""
        for it in self.main_frame_items:
            coord = self.canvas.coords(it)
            point_count = len(coord)
            for x in range(0, point_count, 2):
                self.fp_coords.append(coord[x:x+2])
            # only use the first item as flag to show device.
            return
    def _active(self):
        """action append for active wire"""
        pass
    def redraw(self):
        """docstring for redraw"""
        self.delete_item(self.all_items)
        self.draw()
    def update_name(self):
        """redraw name in the text"""
        self.delete_item(self.name_items)
        self.name_items.clear()
        self.draw_name()
    def delete_item(self, items):
        for item in items:
            self.canvas.delete(item)
    def draw_name(self):
        if self.config.show_name:
            item = self.canvas.create_text(self._name_coord, text=self.logic.name, tags=self.tags, anchor='nw')
            self.name_items.append(item)
            self.move_items(self.name_items)
    def move_all_items(self):
        for item in self.all_items:
            self.canvas.move(item, self.coord[0], self.coord[1])
    def move_items(self, item_list):
        for item in item_list:
            self.canvas.move(item, self.coord[0], self.coord[1])
    def destroy(self):
        for item in self.all_items:
            self.canvas.delete(item)

class GPort(Graph):
    """端口。
    * shape 是图形主要外形。
    """
    def __init__(self, coord, canvas):
        super(GPort, self).__init__(coord, canvas)
        self.port_items = []
        self.item_block.append(self.port_items)
    def draw(self):
        """在画布上绘图。"""
        item = self.canvas.create_polygon(self.shape, fill='black', tags=self.tags, disabledoutline='blue')
        self.canvas.move(item, self.coord[0], self.coord[1])
        self.port_items.append(item)
        #lg.debug(f"draw port at {self.coord}")

class GPortIn(GPort):
    """输入端口。 """
    def __init__(self, coord, canvas):
        super(GPortIn, self).__init__(coord, canvas)
        self.shape = [15,5, 10,10, 0,10, 0,0, 10,0]
        self.tags = (f"type=input", 'cp')

class GPortOut(GPort):
    """输入端口。 """
    def __init__(self, coord, canvas):
        super(GPortOut, self).__init__(coord, canvas)
        self.shape = [5,5, 0,0, 10,0, 15,5, 10,10, 0,10]
        self.tags = (f"type=output", 'cp')


class GPin(Graph):
    """实例端点.
    coord 是pin相对实例原点的坐标。
    标签中有名称，用于在查找线的连接关系时，指示pin的信息。"""
    def __init__(self, coord, canvas, side):
        super(GPin, self).__init__(coord, canvas)
        self.side = side
    def locate(self, side):
        """生成摆放位置。"""
        self.side = side
        self.shape = self.pin_shape_all[side]
    def draw(self):
        """在画布上绘图。"""
        item = self.canvas.create_polygon(self.shape, fill='black', tags=self.tags, disabledoutline='blue')
        self.canvas.move(item, self.coord[0], self.coord[1])
        self.main_frame_items.append(item)
        lg.debug(f"draw pin at {self.coord[0]}, {self.coord[1]}")

class GPinIn(GPin):
    """实例输入端点：三角形。"""
    pin_shape_all = {
            'l': [0,3, 0,0, 6,3, 0,6],
            'r': [6,3, 6,6, 0,3, 6,0],
            't': [3,0, 6,0, 3,6, 0,0],
            'd': [3,6, 0,6, 3,0, 6,6]
            }
    def __init__(self, name, coord, canvas, side='l'):
        super(GPinIn, self).__init__(coord, canvas, side)
        self.shape = [0,3, 0,0, 6,3, 0,6]
        tag_shape_type = 'type=pin'
        tag_cp = f"cp"
        self.tags = (f'name={name}', tag_shape_type, tag_cp)
        self.locate(side)

class GPinOut(GPin):
    """实例输出端口：菱形。"""
    pin_shape_all = {
            'l': [0,3, 3,0, 6,3, 3,6],
            'r': [6,3, 3,6, 0,3, 3,0],
            't': [3,0, 6,3, 3,6, 0,3],
            'd': [3,6, 0,3, 3,0, 6,3]
            }
    def __init__(self, name, coord, canvas, side='r'):
        super(GPinOut, self).__init__(coord, canvas, side)
        self.shape = [0,3, 3,0, 6,3, 3,6] # left
        tag_shape_type = 'type=pout'
        tag_cp = "cp"
        self.tags = (f'name={name}', tag_shape_type, tag_cp)
        self.locate(side)

class GPortR(GPinIn):
    """docstring for GPortR"""
    def __init__(self, coord, canvas):
        super(GPortR, self).__init__('PortR', coord, canvas, 't')
        pass

class GPortW(GPinOut):
    """docstring for GPortR"""
    def __init__(self, coord, canvas):
        super(GPortW, self).__init__('PortW', coord, canvas, 't')
        pass

class GWire(Graph):
    """线。
    min: 线的最小长度。
    coord: save all the points of the wire, not the origin coord as default device. """
    min = 2 
    def __init__(self, coord, canvas, item):
        super(GWire, self).__init__(coord, canvas)
        #self.tags = ('type=wire')
        self.main_frame_items.append(item)
    def _compute_flag_point(self):
        """计算标记点, when wire is selected。"""
        self.coord = self.canvas.coords(self.main_frame_items[0])
        self.fp_coords.append(self.coord[0:2])
        point_count = len(self.coord[4:-2])
        one_fp = self.coord[2:4]
        for x in range(0, point_count, 2):
            self.fp_coords.append([(one_fp[0]+self.coord[4+x])//2,(one_fp[1]+self.coord[5+x])//2])
            one_fp = [self.coord[4+x], self.coord[5+x]]
        self.fp_coords.append(self.coord[-2:])
    def select_point(self, fp_id):
        """show the selected point."""
        try:
            p_index = self.fp_items.index(fp_id)
        except ValueError:
            return False
        fp_coord = self.fp_coords[p_index]
        for fp in self.fp_items:
            self.canvas.delete(fp)
        self.fp_items.clear()
        self.fp_coords.clear()
        item = self._draw_flag_point()
        self.fp_items.append(item)
        self.fp_coords.append(fp_coord)
    def _active(self):
        """action append for active wire"""
        self.canvas.addtag_withtag(self.fp_items[0], tx.TagFlagPointEndPoint)
        self.canvas.addtag_withtag(self.fp_items[-1], tx.TagFlagPointEndPoint)


class GInst(Graph):
    """实例单元。
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
        # 在画图时，需要知道主框图，引脚的位置与图形，引脚的类型标签。
        使用引脚图形对象(graph.pin*)来记录这些信息。
    """
    def __init__(self, coord, canvas, view, logic):
        super(GInst, self).__init__(coord, canvas, logic)
        self.view = view # 参考实例图形: [[LPort*],[],[],[]]
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
    def save_data(self):
        """save pin side and name list"""
        location = []
        for side in self.pin_location:
            location.extend([pin.name for pin in side])
        return location
    def draw(self):
        """在画布上绘图。"""
        self.tags = ('type=inst')
        self.draw_main_frame()
        self.draw_name()
        self.draw_pin()
    def draw_main_frame(self):
        # 主框
        item = self.canvas.create_rectangle(self.mbox, tags=self.tags)
        self.main_frame_items.append(item)
        self.move_items(self.main_frame_items)
    def draw_pin(self):
        # 引脚
        for side in self.pins:
            for pin in side:
                pin.draw()
                self.pin_items.extend(pin.items)
        self.move_items(self.pin_items)

class GBUS(Graph):
    """.
    """
    def __init__(self, coord, canvas):
        super(GBUS, self).__init__(coord, canvas)

class GIF(Graph):
    """.
    """
    def __init__(self, coord, canvas):
        super(GIF, self).__init__(coord, canvas)

class GBlock(Graph):
    """.
    """
    def __init__(self, coord, canvas):
        super(GBlock, self).__init__(coord, canvas)

class GConn(Graph):
    """.
    """
    def __init__(self, coord, canvas):
        super(GConn, self).__init__(coord, canvas)

class GRegfile(Graph):
    """The layout of Regfile is:

            R0      R1     W0 ....
            |       |      |
       +-----------------------------+
       |     name                    |
       +-----------------------------+ 
       |                             |
       |    size(e x r x c)          |
       |                             |
       +-----------------------------+

    """
    def __init__(self, coord, canvas, logic):
        super(GRegfile, self).__init__(coord, canvas, logic)
        self.config.config(show_name=True)
        self.name = logic.name
        self.size =  f"e{self.logic.element} x r{self.logic.row} x c{self.logic.column}"
        self._name_coord = [5, 2]
        #self._size = (0, 0, 40, 40)
        self.shape = [0, 0, 80, 80]
        self.tags = (f"type=regfile")
        self.sub_items = []
        self.size_items = []
        self.pin_items = []
        self.item_block.append(self.sub_items)
        self.item_block.append(self.size_items)
        self.item_block.append(self.pin_items)
        self.rport_list = []
        self.wport_list = []
        self.compute_shape()
    def compute_shape(self):
        self._seperate_line = [0, 20, self.shape[2], 20]
        self._size_coord = [5, 10+self._seperate_line[3]]
        self.name = self.logic.name
        self.size =  f"e{self.logic.element} x r{self.logic.row} x c{self.logic.column}"
        rch_count = int(self.logic.rch_count)
        wch_count = int(self.logic.wch_count)
        for i in range(rch_count):
            self.rport_list.append(GPortR((5+i*(11), -6), self.canvas))
        for j in range(wch_count):
            self.wport_list.append(GPortW((5+(rch_count+j)*(11), -6), self.canvas))
        self.shape[2] = self.shape[2] + 10*(rch_count+wch_count)
    def draw(self):
        """在画布上绘图。"""
        self.draw_main_frame()
        self.draw_sub_frame()
        self.draw_name()
        self.draw_size_text()
        self.draw_pin()
    def draw_main_frame(self):
        """docstring for draw_main_frame"""
        item = self.canvas.create_rectangle(self.shape, tags=self.tags, disabledoutline='blue')
        self.main_frame_items.append(item)
        self.move_items(self.main_frame_items)
    def draw_sub_frame(self):
        item = self.canvas.create_line(self._seperate_line, tags=self.tags)
        self.sub_items.append(item)
        self.move_items(self.sub_items)
    def draw_size_text(self):
        item = self.canvas.create_text(self._size_coord, text=self.size, tags=self.tags, anchor='nw')
        self.size_items.append(item)
        self.move_items(self.size_items)
    def draw_pin(self):
        """draw regfile connection pins according circuit logic, such as one port, 1w1r, or 1w2r."""
        for port in self.rport_list:
            port.draw()
        self.pin_items.extend(port.main_frame_items)
        for port in self.wport_list:
            port.draw()
        self.pin_items.extend(port.main_frame_items)
        self.move_items(self.pin_items)
    def update(self):
        """docstring for update"""
        self.compute_shape()
        self.redraw()

class GPipeReg(Graph):
    """The layout of Regfile is::

               +-----------------------------+
           I0--|     name                    |
               +-----------------------------+ 
               |                             |
           I1>-|    (Pipe)                   |->Out
               |    bunlde                   |
               +-----------------------------+

    I0 is the default input from upper pipeline stage;
    I1 is the input from logic module(usually the implementation of the pipe stage)
    """
    def __init__(self, coord, canvas, logic):
        super(GRegfile, self).__init__(coord, canvas, logic)
        self.config.config(show_name=True)
        self.name = logic.name
        self._shape = [0, 0, 80, 80]
        self._pipe_text = "(Pipe)"
        self.tags = (f"type=pipereg")
        self.sub_items = []
        self.bundle_items = []
        self.pin_items = []
        self.item_block.append(self.sub_items)
        self.item_block.append(self.bundle_items)
        self.item_block.append(self.pin_items)
        self.pin_list = []
    def compute_shape(self):
        self.shape = self._shape
        self._name_coord = [5, 2]
        self._seperate_line = [0, 20, self.shape[2], 20]
        self._pipe_text_coord = [5, self._seperate_line[1]+10]
        self._bundle_coord = [10, self._seperate_line[1]+10]] # future compute by the size of text
    def draw(self):
        """在画布上绘图。"""
        self.draw_main_frame()
        self.draw_sub_frame()
        self.draw_name()
        self.draw_bundle_text()
        self.draw_pin()
    def draw_main_frame(self):
        """docstring for draw_main_frame"""
        item = self.canvas.create_rectangle(self.shape, tags=self.tags, disabledoutline='blue')
        self.main_frame_items.append(item)
        self.move_items(self.main_frame_items)
    def draw_sub_frame(self):
        item = self.canvas.create_line(self._seperate_line, tags=self.tags)
        self.sub_items.append(item)
        self.move_items(self.sub_items)
    def draw_bundle_text(self):
        item = self.canvas.create_text(self._pipe_text_coord, text=self._pipe_text, tags=self.tags, anchor='nw')
        self.bundle_items.append(item)
        item = self.canvas.create_text(self._bundle_coord, text=self.logic.bundle, tags=self.tags, anchor='nw')
        self.move_items(self.bundle_items)
    def draw_pin(self):
        """draw regfile connection pins according circuit logic, such as one port, 1w1r, or 1w2r."""
        for port in self.rport_list:
            port.draw()
        self.pin_items.extend(port.main_frame_items)
        for port in self.wport_list:
            port.draw()
        self.pin_items.extend(port.main_frame_items)
        self.move_items(self.pin_items)
    def update(self):
        """docstring for update"""
        self.compute_shape()
        self.redraw()

class GDevice(object):
    """docstring for GDevice
        * first item in all items is main frame item"""
    def __init__(self, coord, canvas, logic):
        super(GDevice, self).__init__()
        self.coord = coord
        self.canvas = canvas
        self.lc = logic
        self.main_frame = []
        self.all_items = []
        self.config = GConfig()
        self._fp_items = [] #[id1, id2...]
        self._fp_coords = [] #[(x1,y1), (x2,y2)...]
    def draw(self):
        self.draw_main_frame()
        pass
    def draw_main_frame(self):
        pass

class GPort(GDevice):
    """端口。
    * shape 是图形主要外形。
    """
    def __init__(self, coord, canvas):
        super(GPort, self).__init__(coord, canvas)
    @property
    def cp(self):
        return self.main_frame
    def draw_main_frame(self):
        """在画布上绘图。"""
        item = self.canvas.create_polygon(self.main_frame, fill='black', tags=self.tags, disabledoutline='blue')
        self.canvas.move(item, self.coord[0], self.coord[1])
        self.all_items.append(item)

class GInst(GDevice):
    """instance:
        * first item in all items is main frame item"""
    def __init__(self, coord, canvas, logic):
        super(GDevice, self).__init__(coord, canvas, logic)
        self.pin = []
        self.main_frame = [0,0, 50,50]
        self.sub_shape = []
        self.text = logic.name
        self._name_coord = (5, 2)
    def draw(self):
        self.draw_main_frame()
        self.draw_pin()
        self.draw_sub_shape()
        self.draw_text()
    def draw_main_frame(self):
        pass
    def draw_pin(self):
        pass
    def draw_sub_shape(self):
        pass
    def draw_text(self):
        pass

if __name__ == "__main__":
    print("graph.py")

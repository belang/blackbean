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

class Graph:
    """器件图形。
    * coord: 是器件相对图形原点的坐标，仅在初始化时有效。
    * fp_items: record the canvas item which is shown and selected.
    """
    fp_shape = (-3,-3, 3,3)
    def __init__(self, coord, canvas):
        self.coord = coord
        self.items = []
        self.canvas = canvas
        self.fp_items = [] #[id1, id2...]
        self.fp_coords = [] #[(x1,y1), (x2,y2)...]
        self.shape = []
    @property
    def border_coord(self):
        """main border coords"""
        for it in self.items:
            return self.canvas.coords(it)
        return (0, 0)
    def _draw_flag_point(self): 
        """draw flag point to the seleted shape."""
        for coord in self.fp_coords:
            item = self.canvas.create_rectangle(self.fp_shape, fill='light blue', tags=xt.TagFlagPoint)
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
        for it in self.items:
            coord = self.canvas.coords(it)
            point_count = len(coord)
            for x in range(0, point_count, 2):
                self.fp_coords.append(coord[x:x+2])
            # only use the first item as flag to show device.
            return
    def _active(self):
        """action append for active wire"""
        pass

class GPort(Graph):
    """端口。
    * shape 是图形主要外形。
    """
    def __init__(self, coord, canvas):
        super(GPort, self).__init__(coord, canvas)
    def draw(self):
        """在画布上绘图。"""
        item = self.canvas.create_polygon(self.shape, fill='black', tags=self.tags, disabledoutline='blue')
        self.canvas.move(item, self.coord[0], self.coord[1])
        self.items.append(item)
        lg.debug(f"draw device at {self.coord}")

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
        self.items.append(item)

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

class GWire(Graph):
    """线。
    min: 线的最小长度。
    coord: save all the points of the wire, not the origin coord as default device. """
    min = 2 
    def __init__(self, coord, canvas, item):
        super(GWire, self).__init__(coord, canvas)
        #self.tags = ('type=wire')
        self.items.append(item)
    def _compute_flag_point(self):
        """计算标记点, when wire is selected。"""
        self.coord = self.canvas.coords(self.items[0])
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
        self.canvas.addtag_withtag(self.fp_items[0], xt.TagFlagPointEndPoint)
        self.canvas.addtag_withtag(self.fp_items[-1], xt.TagFlagPointEndPoint)


class GInst(Graph):
    """实例单元。
    """
    def __init__(self, coord, canvas, view):
        super(GInst, self).__init__(coord, canvas)
        self.view = view # 参考实例图形
    def draw(self):
        """在画布上绘图。"""
        self.tags = ('type=inst')
        # 主框
        item = self.canvas.create_rectangle(self.view.mbox, tags=self.tags)
        self.canvas.move(item, self.coord[0], self.coord[1])
        self.items.append(item)
        # 引脚
        for side in self.view.pins:
            for pin in side:
                pin.draw()
                self.items.extend(pin.items)
                for item in pin.items:
                    self.canvas.move(item, self.coord[0], self.coord[1])

class GModuleView(Graph):
    """模块实例参考图形。\n
        模块图形坐标：
        X = (-x, 0),   Y = (0, 0)\n
                   +----------+\n
                   | top pin  |\n
        X----------Y----------+------------+\n
        | left pin | main box |  right pin |\n
        +----------+          +------------+\n
                   |          |\n
        +----------+          +------------+\n
        | left pin | main box |  right pin |\n
        +----------+----------+------------+\n
                   | down pin |\n
                   +----------+\n
        \n
        # 在画图时，需要知道主框图，引脚的位置与图形，引脚的类型标签。
        使用引脚图形对象(graph.pin*)来记录这些信息。
    """
    _size = (20, 20) # initial size: x_coord(h), y_coord(v)
    _pin_space = (8, 8) # the increased length when adding one pin.
    _pin_size = (6, 6)
    def __init__(self, coord, canvas):
        super(GModuleView, self).__init__(coord, canvas)
        self.size = [0, 0]
        self.pins = [[],[],[],[]] # [l, r, t, d]
        self.pin_location = []
    def config_pin_placement(self, pin_location=[]):
        """配置pin的排列：pin_location是pin器件列表，
        元素是每个边的引脚列表，依次为左、右、上、下"""
        # pin_location = [[LPort*],[],[],[]]
        pin_location.extend([[],[],[],[]])
        self.pin_location = pin_location
        lpins = pin_location[0]
        rpins = pin_location[1]
        tpins = pin_location[2]
        dpins = pin_location[3]
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
        placed_pin_count = sum(len(x) for x in pin_location)
        #if placed_pin_count != pin_count:
            #lg.error(f"引脚数目不全，还缺少{pin_count - placed_pin_count}个引脚没有定义位置")
    def _add_pin(self, plist, pin, coord, side):
        """向单元中增加一个引脚摆放。"""
        plist.append(pin.gen_pin()(pin.name, coord, self.canvas, side))

    @property
    def mbox(self):
        """main box"""
        return (0, 0, self.size[0], self.size[1])
    def save_data(self):
        """save pin side and name list"""
        location = []
        for side in self.pin_location:
            location.extend([pin.name for pin in side])
        return location

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


if __name__ == "__main__":
    print("graph.py")

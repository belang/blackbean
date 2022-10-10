#! $PATH/python
# -*- coding: utf-8 -*-

# file name: nfsv.py
# author: lianghy
# time: 9/8/2022 3:36:14 PM

"""Generate SystemVerilog from NuanFeng Model."""

import math
import logging

RESET = '!rst_n'
RESET_EDGE = 'negedge rst_n'
CLK = 'clk'
CLOCK_EDGE = 'posedge clk'
END = '\n'
COLON = ': '
# system verilog data and procedures class

class NFSV(object):
    """docstring for Processes"""
    def __init__(self, level=0):
        super(NFSV, self).__init__()
        self.level = level
        self._rtl = ''
    @property
    def indent(self):
        """caculate the space indent of the code"""
        return f"{'    '*self.level}"
    @property
    def rtl(self):
        if self._rtl == '':
            self.gen_rtl()
        return self._rtl
    def gen_rtl(self):
        raise NotImplementedError("gen_rtl")

class Port(NFSV):
    """Port"""
    def __init__(self, direction, ptype, iden):
        super(Port, self).__init__(1)
        self.direction = direction
        self.ptype = ptype
        self.iden = iden

class ANSIPort(Port):
    """ANSI type Port"""
    def __init__(self, direction, ptype, iden):
        super(ANSIPort, self).__init__(direction, ptype, iden)
    def gen_rtl(self):
        self._rtl = self.indent
        self._rtl += self.direction
        self._rtl += '    '
        self._rtl += self.ptype
        self._rtl += ' '
        self._rtl += self.iden

## type declaration
class TypeDec(NFSV):
    """Declaration type"""
    def __init__(self, name, level=0):
        super(TypeDec, self).__init__(level)
        self.name = name

class TDEnum(TypeDec):
    """Declaration type: enum"""
    def __init__(self, name, item, level=0):
        super(TDEnum, self).__init__(name, level)
        self.item = item
    def gen_rtl(self):
        length = len(self.item)
        bit = math.ceil(math.log2(length))-1
        self._rtl = self.indent
        self._rtl += f'typedef enum logic [{bit}:0]'
        self._rtl += ' {'
        self._rtl += ', '.join(self.item)
        self._rtl += '} '+self.name+';\n'

## data declaration

class DataDec(NFSV):
    """Declare data."""
    def __init__(self, dtype, signals, level=0):
        super(DataDec, self).__init__()
        self.dtype = dtype
        self.signals = signals
        self.align_width = len(dtype) + 4
    def gen_rtl(self):
        self._rtl = self.indent
        self._rtl += f"{self.dtype: <{self.align_width}}"
        self._rtl += ' '.join(self.signals)
        self._rtl += f';\n'

## Processes

class Processes(NFSV):
    """Processes"""
    def __init__(self, level=0):
        super(Processes, self).__init__(level)

class Procedures(Processes):
    """Procedures"""
    def __init__(self, level=0):
        super(Procedures, self).__init__(level)
        self.block = None
    def add_statement(self, stm):
        self.block.add_stm(stm)
    def gen_rtl(self):
        self._rtl = self.indent
        self._rtl += self.head
        self._rtl += ' '
        self.block.level = self.level
        self._rtl += self.block.rtl

class Always(Procedures):
    """ProceduresAlways"""
    def __init__(self, iden):
        super(Always, self).__init__()
        self.block = BlockSeq(iden)

class AlwaysFF(Always):
    """always_ff"""
    def __init__(self, iden=''):
        super(AlwaysFF, self).__init__(iden)
        self.head = f"always_ff @({CLOCK_EDGE} or {RESET_EDGE})"

class AlwaysComb(Always):
    """always_comb"""
    def __init__(self, iden=''):
        super(AlwaysComb, self).__init__(iden)
        self.head = f"always_comb"
    def set_signal_default_value(self, signal, value='0'):
        self.block.add_def_stm(AssignBlocking(signal, value))

## Processes -> block

class Block(Processes):
    """block: a group of statements.
    type: seq - sequential"""
    def __init__(self, iden):
        super(Block, self).__init__()
        self.iden = iden
        self._iden_rtl = ''
        if self.iden != '':
            self._iden_rtl = COLON+self.iden
        self.keyword = ['begin', 'end']
        self.statements = []
        self.stm_default = []       # all statements for signal default value
    def set_level(self, up):
        self.level = up.level
    def add_def_stm(self, stm):
        # TODO: check whether the signal is set.
        self.stm_default.append(stm)
    def add_stm(self, stm):
        self.statements.append(stm)
    def gen_rtl(self):
        self._rtl = '' # no indent at begin
        self._rtl += self.keyword[0]
        self._rtl += self._iden_rtl
        self._rtl += END
        for s in self.stm_default:
            s.level = self.level + 1
            self._rtl += s.rtl
        for s in self.statements:
            s.level = self.level + 1
            self._rtl += s.rtl
        self._rtl += self.indent+self.keyword[1]
        self._rtl += self._iden_rtl
        self._rtl += END

class BlockSeq(Block):
    """sequential block"""
    def __init__(self, iden=''):
        super(BlockSeq, self).__init__(iden)
        #self.keyword = ['begin', 'end'] # default is Seq


### Procedures: procedural programming

class ProcProm(Procedures):
    """Procedural program"""
    def __init__(self, level=0):
        super(ProcProm, self).__init__(level)
        self.block = BlockSeq()

class CaseItem(ProcProm):
    """CaseItem"""
    def __init__(self, exp):
        super(CaseItem, self).__init__()
        self.exp = exp
    def set_level(self, up):
        self.level = up.level + 1
    def gen_rtl(self):
        self.block.set_level(self)
        self._rtl = self.indent
        self._rtl += self.exp+': '
        self._rtl += self.block.rtl

class CaseItemDefault(CaseItem):
    """Default Case Item"""
    def __init__(self, variable, exp):
        super(CaseItemDefault, self).__init__('default')
        self.block.add_stm(AssignBlocking(variable, exp))

class Case(ProcProm):
    """case statement:"""
    def __init__(self, case_exp, up_block):
        super(Case, self).__init__()
        self.quality = ''
        self.keyword = 'case'
        self.case_exp = case_exp
        self.up_block = up_block
        self.up_block.add_statement(self)
        self.items = []
    def get_item(self, exp):
        for item in self.items:
            if item.exp == exp:
                return item
        return False
    def new_item(self, item_exp):
        item = CaseItem(item_exp)
        self.items.append(item)
        return item
    def gen_rtl(self):
        self._rtl = self.indent
        if self.quality != '':
            self._rtl += self.quality + ' '
        self._rtl += self.keyword
        self._rtl += f' ({self.case_exp})\n'
        for item in self.items:
            item.level = self.level + 1
            self._rtl += item.rtl
        self.default_item.set_level(self)
        self._rtl += self.default_item.rtl

class UniqueCase(Case):
    """block statement"""
    def __init__(self, exp, up_block):
        super(UniqueCase, self).__init__(exp, up_block)
        self.quality = 'unique'
        pass

class IF(ProcProm):
    """if else"""
    def __init__(self, cond, level=0):
        super(IF, self).__init__(level)
        self.cond = cond
        self.head = "if (" + self.cond + ')'

class IFNRst(IF):
    """if (!rst_n)"""
    def __init__(self):
        super(IFNRst, self).__init__(RESET)
        pass

class Else(ProcProm):
    """Else"""
    def __init__(self):
        super(Else, self).__init__()
        self.head = "else"

class ElseIF(ProcProm):
    """Else"""
    def __init__(self, cond):
        super(ElseIF, self).__init__()
        self.head = "else if (" + self.cond + ')'

## Assign Statement

class AssignProc(NFSV):
    """block statement"""
    def __init__(self, target, assign, expression):
        super(AssignProc, self).__init__()
        self.target = target
        self.assign = assign
        self.expression = expression
        pass
    def gen_rtl(self):
        self._rtl = self.indent
        self._rtl += f'{self.target} {self.assign} {self.expression}'
        self._rtl += ';'
        self._rtl += END

class AssignBlocking(AssignProc):
    """block statement"""
    def __init__(self, variable, expression):
        super(AssignBlocking, self).__init__(variable, '=', expression)
        pass

class AssignNonBlocking(AssignProc):
    """block statement"""
    def __init__(self, target, expression):
        super(AssignNonBlocking, self).__init__(target, '<=', expression)
        pass


# SV Hierarchy Constructs

# circuit function component

class NFSVComponent(NFSV):
    """A component is a logic function. It is initialed by a component defined in HAML"""
    def __init__(self, comp):
        super(NFSVComponent, self).__init__()
        self.io = []
        self.type_dec = []
        self.data_dec = []
        self.process = []
        self.comb = []
        self.instance = []
        self.data_model = comp
    def gen_circuit(self):
        """generate circuit in system verilog view."""
        self.gen_io()
        self.gen_type_dec()
        self.gen_data_dec()
        self.gen_process()
        self.gen_comb()
        self.gen_instance()
    def gen_io(self):
        pass
    def gen_type_dec(self):
        pass
    def gen_data_dec(self):
        pass
    def gen_process(self):
        pass
    def gen_comb(self):
        pass
    def gen_instance(self):
        pass

class Module(NFSVComponent):
    """docstring for Module"""
    def __init__(self, comp):
        super(Module, self).__init__(comp)
        self.definition = f'module {self.data_model.name} (\n'
        self.end = 'endmdule'
        self.comp = []      # components list
    def gen_circuit(self):
        for c in self.data_model.components:
            # mc: model of component
            if c.type == "FSM":
                mc = NFSVFSM(c)
            elif c.type == "IO":
                mc = NFSVIO(c)
            elif c.type == "Comb":
                mc = NFSVComb(c)
            else:
                raise NotImplementedError(c.type)
            self.comp.append(mc)
            mc.gen_circuit()
            self.io.extend(mc.io)
            self.type_dec.extend(mc.type_dec)
            self.data_dec.extend(mc.data_dec)
            self.process.extend(mc.process)
            self.comb.extend(mc.comb)
    def gen_rtl(self):
        self._rtl = ''
        self._rtl += self.definition
        self._rtl += ',\n'.join([t.rtl for t in self.io])
        self._rtl += '\n);\n\n'
        self._rtl += '\n'.join([t.rtl for t in self.type_dec])
        self._rtl += '\n'
        self._rtl += ';\n'.join([t.rtl for t in self.data_dec])
        self._rtl += '\n'
        self._rtl += '\n'.join([t.rtl for t in self.process])
        self._rtl += '\n'
        self._rtl += '\n'.join([t.rtl for t in self.comb])
        self._rtl += '\n'
        self._rtl += '\n'.join([t.rtl for t in self.instance])
        self._rtl += '\n'
        self._rtl += self.end

class NFSVFSM(NFSVComponent):
    """rtl for FSM."""
    def __init__(self, data_model):
        super(NFSVFSM, self).__init__(data_model)
        self.cs = data_model.name+"_cs"
        self.ns = data_model.name+"_ns"
    def gen_type_dec(self):
        self.data_type = f"t_{self.data_model.name}"
        self.type_dec.append(TDEnum(self.data_type, [s for s in self.data_model.states]))
    def gen_data_dec(self):
        self.data_dec.append(DataDec(self.data_type, [self.cs, self.ns]))
    def gen_process(self):
        self.gen_transfer()
        self.gen_condition()
    def gen_transfer(self):
        always = AlwaysFF(f'transfer_{self.data_model.name}')
        self.process.append(always)
        s_if = IFNRst()
        always.add_statement(s_if)
        s_if.add_statement(AssignNonBlocking(self.cs, self.data_model.rst_state))
        s_else = Else()
        always.add_statement(s_else)
        s_else.add_statement(AssignNonBlocking(self.cs, self.ns))
    def gen_condition(self):
        always = AlwaysComb(f'condition_{self.data_model.name}')
        self.process.append(always)
        always.set_signal_default_value(self.ns, self.cs)
        case = UniqueCase(self.cs, always)
        for s in self.data_model.cond_states:
            item = case.get_item(s['state'])
            c_level = item
            if item:
                stm = Else()
                item.add_statement(stm)
                c_level = stm
            else:
                item = case.new_item(s['state'])
                c_level = item
            if s['condition'] != '':
                stm = IF(s['condition'])
                c_level.add_statement(stm)
                c_level = stm
            c_level.add_statement(AssignBlocking(self.ns, s['next_state']))
        s = self.data_model.default_cond
        case.default_item = CaseItemDefault(self.ns, s['next_state'])

class NFSVIO(NFSVComponent):
    """rtl for IO."""
    def __init__(self, comp):
        super(NFSVIO, self).__init__(comp)
        pass
    def gen_io(self):
        for pin in self.data_model.io:
            ptype = f'[{int(pin["width"])-1}:0]'
            if pin['direc'] == 'i':
                self.io.append(ANSIPort('input', ptype, pin['name']))

            else:
                self.io.append(ANSIPort('output', ptype, pin['name']))

class NFSVComb(NFSVComponent):
    """Combination logic.
    always_comb begin : name
        signal = default value;
        if () begin
        else if () beign
        end
    end : name"""
    def __init__(self, comp):
        super(NFSVComb, self).__init__(comp)
        pass
    def gen_comb(self):
        always = AlwaysComb(f'gen_{self.data_model.name}')
        self.comb.append(always)
        signal = ''
        f_new_signal = True # flag indicates next row is a new signal
        for item in self.data_model.item:
            always.add_statement(AssignBlocking(item.name, item.default_value))
            t_next_branch = False
            for c in item.branch:
                if c['condition'] != '':
                    if t_next_branch is True:
                        branch = ELSEIF(c['condition'])
                    else:
                        branch = IF(c['condition'])
                    always.add_statement(branch)
                    branch.add_statement(AssignBlocking(item.name, c['expression']))
                    t_next_branch = True
            self.comb.append(AssignBlocking(item['name'], item['data']))
        #Future: optimize if-else logic to case

if __name__ == "__main__":
    print("nfsv.py")

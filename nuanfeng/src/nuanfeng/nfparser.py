#! $PATH/python
# -*- coding: utf-8 -*-

# file name: nfparser.py
# author: lianghy
# time: 8/25/2022 4:07:26 PM

"""Nuanfeng(warm wind)"""

import argparse
import sys
import urllib.error
import urllib.request

import logging

import docutils.frontend
import docutils.nodes
import docutils.parsers.rst
import docutils.utils

from nuanfeng import nfmodel

# parse a table:
#   title -> tbody -> row -> entry -> paragraph -> [attribute] -> Text
#   |                                                             |
#   v                                                             v
#   type and name of component                                    data of component

class NFVTable(docutils.nodes.GenericNodeVisitor):
    def __init__(self, document, module):
        super(NFVTable, self).__init__(document)
        self.module = module
    def visit_table(self, node):
        title = node.children[0].children[0] #table.title.Text
        c_patten, c_name = parse_component_title(title)
        logging.debug(f"get table title {c_patten}, name {c_name}")
        for comp in NFTable_Dont_Parse:
            if comp == c_patten:
                m_comp = True
                logging.debug(f"skip table {c_name}")
                return
        NFTable_Comp_Parser_Sel[c_patten](c_name, self.module, node)
    def default_visit(self, node):
        pass

class NFVTableBody(docutils.nodes.GenericNodeVisitor):
    def __init__(self, document, m_comp):
        super(NFVTableBody, self).__init__(document)
        self.m_comp = m_comp
        self.rows = []
    def visit_tbody(self, node):
        #logging.debug(f"get table body {node}")
        v = NFVTableBodyRow(self.document, self.rows)
        node.walk(v)
    def default_visit(self, node):
        pass

class NFVTableBodyRow(docutils.nodes.GenericNodeVisitor):
    def __init__(self, document, rows):
        super(NFVTableBodyRow, self).__init__(document)
        self.rows = rows
        self.row = None
    def visit_row(self, node):
        #logging.debug(f"get row {node}")
        self.rows.append(node)
    def default_visit(self, node):
        pass

class NFVText(docutils.nodes.GenericNodeVisitor):
    def __init__(self, document):
        super(NFVText, self).__init__(document)
        self.text = None
    def visit_text(self, node):
        logging.debug(f"get text {node}")
        self.text = node.astext()
    def default_visit(self, node):
        pass

def parse_component_title(title):
    """docstring for parse_component_title"""
    index = title.index(' - ')
    cp = title[0:index]     # component patten
    cn = title[index+3:]    # component name
    return cp, cn

def parse_table_FSM_define(name, module, node):
    # get rows from body
    logging.debug(f"parse FSM define")
    comp = module.new_component("FSM", name)
    v = NFVTableBody(node.document, comp)
    node.walk(v)
    # get valid entry
    for row in v.rows:
        *_, state_name = row.children[0].traverse()
        #*_, pre_state =  row.children[1].traverse()
        #*_, condition =  row.children[2].traverse()
        comp.new_state(state_name.astext())

def parse_table_FSM_trans(name, module, node):
    # get rows from body
    logging.debug(f"parse FSM transfer")
    comp = module.get_component("FSM", name)
    v = NFVTableBody(node.document, comp)
    node.walk(v)
    # get valid entry
    for row in v.rows:
        *_, state = row.children[0].traverse()
        *_, next_state  = row.children[1].traverse()
        *_, condition  = row.children[2].traverse()
        comp.new_condition(state.astext(), next_state.astext(), condition.astext())

def parse_table_IO(name, module, node):
    # get rows from body
    comp = module.new_component("IO", name)
    logging.debug(f"parse IO")
    v = NFVTableBody(node.document, comp)
    node.walk(v)
    # get valid entry
    for row in v.rows:
        a = []
        for c in row.children[0:-1]:
            *_, n = c.traverse()
            a.append(n.astext())
        comp.new_io(a)

def parse_table_Comb(name, module, node):
    # get rows from body
    comp = module.new_component("Comb", name)
    logging.debug(f"parse IO")
    v = NFVTableBody(node.document, comp)
    node.walk(v)
    # get valid entry
    for row in v.rows:
        a = []
        for c in row.children[0:-1]:
            *_, n = c.traverse()
            a.append(n.astext())
        comp.new_item(a)


def parse_module(node):
    # new module
    #       doc  section     title       text       
    mtext = node.children[0].children[0].children[0]
    if mtext.startswith('Module -'):
        module_name = mtext[9:]
    else:
        raise ValueError(f"no module define is found in {mtext}")
    module = nfmodel.NFModule(module_name)
    v = NFVTable(node.document, module)
    node.children[0].walk(v) # only one module in a document
    return module

def parse_rst_file(fileobj):
    # Parse the file into a document with the rst parser.
    default_settings = docutils.frontend.OptionParser(
        components=(docutils.parsers.rst.Parser,)).get_default_values()
    document = docutils.utils.new_document(fileobj.name, default_settings)
    parser = docutils.parsers.rst.Parser()
    parser.parse(fileobj.read(), document)

    # Visit the parsed document with our link-checking visitor.
    #visitor = LinkCheckerVisitor(document)
    #document.walk(visitor)
    return document


NFTable_Dont_Parse = []

NFTable_Comp_Parser_Sel = {
        'FSM': parse_table_FSM_define,
        'FSM_TRAN': parse_table_FSM_trans,
        'IO': parse_table_IO,
        'Comb': parse_table_Comb,
        }

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('infile', type=argparse.FileType('r'),
                           default=sys.stdin)
    argparser.add_argument('-p', dest='PrintDoc', nargs='?', default=True)
    args = argparser.parse_args()
    print('Reading', args.infile.name)
    document = parse_rst_file(args.infile)
    if args.PrintDoc:
        document.export()

if __name__ == "__main__":
    print("parse HAML")

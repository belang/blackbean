name = "nuanfeng"

import os
from . import nfparser
from . import nfsv

def parse_spec(flist, dout='rtl'):
    if not os.path.isdir(dout):
        os.mkdir(dout)
    #modules = []
    for onef in flist:
        with open(onef, 'r') as fin:
            document = nfparser.parse_rst_file(fin)
        module = nfparser.parse_module(document)
        rtl_module = nfsv.Module(module)
        #modules.append(rtl_module)
        fname = os.path.basename(onef)
        with open(os.path.join(dout, fname), 'w') as fout:
            fout.write(rtl_module.gen_circuit())


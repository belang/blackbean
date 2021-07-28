#! $PATH/python
# -*- coding: utf-8 -*-

# file name: xxtext.py
# author: lianghy
# time: 9/9/2020 3:50:14 PM

"""This is the text file of all labels in xiaoxiao views."""


def init_text(lan=None):
    if lan == 'ch':
        class Text:
            class WindowTools:
                self.new         = "新建"
                self.open        = "打开"
                self.save        = "保存"
                self.close       = "关闭"
                self.backward    = "后退"
                self.forward     = "前进"
                self.export      = "导出"
                self.inport      = "导入"
                self.module      = "模块"
                self.inst        = "输入"
                self.input       = "输出"
                self.output      = "实例"
                self.wire        = "单线"
                self.delete      = "删除"
                self.move        = "移动"
            class AttrWin:
                apply       = "应用"
                reset       = "重置"
                exportPin   = "输出引脚"
                importPin   = "导入引脚"
                initView    = "初始化视图"
    else:
        class Text:
            TagFlagPoint = 'TagFP'
            TagFlagPointEndPoint = 'TagFPEP'

            ACTCreateModule = 1
            ACTCreateDevice = 2

            InfoCreateModule = 'create module' # 创建模块
            InfoCreateDevice = 'create device' # 创建模块
            InfoCreateInput = 'create input' # 创建输入
            InfoCreateReg = 'create register'
            InfoCreateRegfile = 'create regfile'
            InfoCancelCreateModule = 'cancel create module' # 撤消创建模块
            InfoCancelCreateDevice = 'cancel create device' # 撤消创建器件
            InfoAskOverwriteProject = 'Overwrite'
            InfoAskOverwriteProjectM = 'The project exists, overwrite?'
            InfoAskSaveProject = 'Save Project'
            InfoAskSaveProjectM = 'The project is changed. Save it?'
            InfoCloseCircuit = 'Close circuit' # 关闭电路
            InfoSaveCircuit = 'Save circuit' # 保存电路
            InfoInstType = 'Instance Type'
            InfoDevUpdateName = "modify device name {} to {}"
            InfoDevUpdateWidth = "modify device width {} to {}"

            # common text
            NameNone = "none"
            LName = 'name'
            LModuleName = "Module Name" # "模块名"
            LProjectName = "project name" # "工程名"
            LProjectDir = "directory" # "目录"
            LOpen = "open" # "打开"

            MessageCheckCircuitName = 'Please check circuit name!' # 请检查电路名称
            FileErrorDirNotExit = 'Director does not exist'

            # project
            MNewProject = "new project" # "新建工程"
            MSaveProject = "save project" # "保存工程"

            ErrorModuleName = 'Error: Module Name' # 错误：模块名称
            ErrorDeviceName = 'Device Name:' # "器件名称"
            ErrorDeviceWidth = 'Device Width:' # "器件位宽"

            # attritute
            AttrInstEmpty   = "Empty Module"
            AttrInstCircuit = "Circuit Module"

            # dia
            DiaSelFileTitle = "Select Define File"
            DiaAskOpenFile = "Browse"
            DiaDesignFile = "input file name"

            class WindowTools:
                project     = "Pro"
                new         = "newC"
                open        = "open"
                save        = "save"
                close       = "clos"
                backward    = "back"
                forward     = "forw"
                export      = "expo"
                inport      = "impo"
                module      = "NewM"
                inst        = "inst"
                regb        = "BReg"
                regfile     = "RF"
                input       = "inpu"
                output      = "outp"
                wire        = "wire"
                delete      = "dele"
                move        = "move"
            class AttrWin:
                apply       = "Apply"
                reset       = "Reset"
                exportPin   = "ExPin"
                importPin   = "ImPin"
                initView    = "InitView"
                newPro      = "New"
                savePro     = "Save"
                closePro    = "Close"
                openPro     = "Open"
                name        = "Name" # "引脚名"
                pinName     = "Pin Name" # "引脚名"
                signalName  = "Signal Name" # "引脚名"
                width       = "Width" # "位宽"
                refType     = 'Ref Type'
                refName     = 'Ref Name'
                element     = 'element  '
                row         = 'row      '
                column      = 'column   '
                rch_count   = 'read port  count'
                wch_count   = 'write port count'
            class Action:
                newCircuit  = "new circuit"
                newProject  = "new project" # "新建工程"
            wt = WindowTools()
            aw = AttrWin()
            ac = Action()
    return Text()
if __name__ == "__main__":
    print("xxtext.py")

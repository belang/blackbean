#! $PATH/python
# -*- coding: utf-8 -*-

# file name: error.py
# author: lianghy
# time: 11/11/2020 5:20:36 PM

"""定义错误类型和错误描述。"""

wrong_driver_type = '驱动信号的类型只能是Signal或Output。'
forbid_set_load   = '禁止直接向负载赋值，强制赋值请使用force。'

if __name__ == "__main__":
    print("error.py")

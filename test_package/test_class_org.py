import sys
sys.path.append('../Share_py')
import os
import numpy as np

from debug_assistant import VarRegister
var_register = VarRegister(os.path.abspath(__file__))

class test_class():
    def __init__(self):
        pass
    def function_call(self):
        time_all = 0
        a = 10
        b = np.array([10])
        c = [100]
        d = {0: 10}

        var_register.goto_switch(state=True, index=[], ignore_var=['time_all'])

        # preprocess
        var_register.goto_start(1)
        time_all += 10
        a += 10
        b[0] += 10
        c[0] += 10
        d[0] += 10
        var_register.goto_end(1)

        # inference
        var_register.goto_start(2)
        time_all += 10
        a += 5
        b[0] += 5
        c[0] += 5
        d[0] += 5
        var_register.goto_end(2)

        # postprocess
        time_all += 10
        print(a)
        print(b[0])
        print(c[0])
        print(d[0])

        print(str(time_all) + ' mins')
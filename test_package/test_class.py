import sys
sys.path.append('../../packages_custom/Share_py')
import os
from debug_assistant import VarRegister
var_register = VarRegister(os.path.abspath(__file__))

class test_class():
    def __init__(self):
        pass
    def f_call(self):
        time_all = 0

        var_register.goto_on()

        print('preprocess')
        time_all += 10

        var_register.goto_start(1)
        print('inference')
        time_all += 10
        a = 11
        c = [100, 2013]
        d = {0:0, '1':'2'}

        var_register.goto_end(1)

        print('postprocess')
        time_all += 10
        print(a + 1)
        print(c[0] + 1)
        print(d[0] + 1)

        print(str(time_all) + 'mins')
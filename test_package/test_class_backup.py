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

        var_register.goto_turn_on()

        var_register.goto_start()
        print('state1')
        time_all += 10
        var_register.goto_end()

        print('state2')
        time_all += 10

        print('state3')
        time_all += 10

        print('state4')
        time_all += 10

        print('state5')
        time_all += 10

        print(str(time_all) + 'mins')
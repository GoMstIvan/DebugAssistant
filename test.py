from test_package.test_class import test_class

import sys
sys.path.append('../../packages_custom/Share_py')

def sub_function(x):
    y1 = x+1
    y2 = x+2
    return (y1,y2)

if __name__ == '__main__':
    my_class = test_class()
    my_class.f_call()

    x = 1
    y = sub_function(x)
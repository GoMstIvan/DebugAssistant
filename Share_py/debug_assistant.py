import pickle
import inspect
import os

class VarRegister():
    def __init__(self, current_file_path=''):
        if current_file_path == '':
            raise BaseException('you must input current_file_path, recommand: "os.path.abspath(__file__)" ')
        # print('Notice: goto_start, goto_end can just be comment out by #')
        self.current_file_path = current_file_path

        self.index_used = []
        self.index2row_dict = {}  # 記錄著每個index是哪個row開始哪個row結束

        self.goto_switch_state = True
        self.contents = []
        self.contents_insert = []
        self.revise_row_start = []
        self.revise_row_end = []
        self.revise_if = False
        self.var_register_name = ''
        self.ignore_var_list = []
        with open(self.current_file_path, 'r', encoding='utf-8') as f:
            contents = f.readlines()
        for content in contents:
            if 'VarRegister(' in content:
                var_register_name = content.split('VarRegister(')[0]
                var_register_name = var_register_name.replace('=', '')
                self.var_register_name = ''.join(var_register_name.split())

    def goto_switch(self, state=True, index=[], ignore_var=[]):  # 可用list指定index，沒指定就是all
        # 列出所有index
        self.__state_check()
        # 刪掉沒有指定的index
        self.__unspecify_index_del(index)

        self.ignore_var_list = ignore_var  # 忽略的變數不會儲存和載入

        self.goto_switch_state = state

        if state:  # turn on
            # 針對指定的index
            # 如果有非註解的goto_end、goto_start
            # 沒有  # debug---要跑完且儲存每個goto_end的local() 並加入debug註解請、goto_end下面加入載入local變數，使用者重跑一次
            # 有  # debug---，則要載入local()跑
            # 如果沒有則正常執行就好
            self.__operate()
        else:  # turn off
            # 針對指定的index
            # 如果有  # debug--- 要去掉# debug---，goto_end下面加入載入local變數，請使用者重跑一次
            # 如果沒有  # debug--- ，就正常執行就好
            self.__recover()

    def __unspecify_index_del(self, index=[]):
        if index != []:
            for i in range(len(self.index_used) - 1, -1, -1):
                if not self.index_used[i] in index:
                    del self.index2row_dict[self.index_used[i]]
                    del self.index_used[i]

    def __state_check(self):
        self.index_used.clear()
        self.index2row_dict.clear()
        with open(self.current_file_path, 'r', encoding='utf-8') as f:
            contents = f.readlines()
        # 原則: 無論是非註解還是註解的goto_start、goto_end必須要成雙成對、index不能重複
        index_start = []
        index_end = []
        row_start = []
        row_end = []
        for i in range(len(contents)):
            if '.goto_start(' in contents[i]:
                tmp = contents[i].split('.goto_start(')[-1]
                tmp = tmp.split(')')[0]
                index_start.append(int(tmp))
                row_start.append(i)
            if '.goto_end(' in contents[i]:
                tmp = contents[i].split('.goto_end(')[-1]
                tmp = tmp.split(')')[0]
                index_end.append(int(tmp))
                row_end.append(i)
        index_len = min(len(index_start), len(index_end))
        for i in range(index_len):
            if index_start[i] != index_end[i]:
                raise BaseException('index should be a pair: ' + str(index_start[i]))
            else:
                if index_start[i] in self.index_used:
                    raise BaseException('index is repeated ' + str(index_start[i]))
                self.index_used.append(index_start[i])
                self.index2row_dict[index_start[i]] = [row_start[i], row_end[i]]

    def goto_start(self, index):  # 僅設立標註點用 goto_start、goto_end必須要同時存在，且目前不可形成巢狀
        pass

    def goto_end(self, index):  # 僅設立標註點用 goto_start、goto_end必須要同時存在，且目前不可形成巢狀
        pass

        if self.goto_switch_state:
            # 儲存goto_start(index)~goto_end(index)區間所用到的locals()
            if index in self.index_used:
                var = locals()
                self.dump_all(index)
                self.local_load_code_generate(index)

            if self.revised_if and index == self.index_used[-1]:
                self.revised_if = False
                for i in range(len(self.index_used)-1, -1, -1):
                    insert_row = self.index2row_dict[self.index_used[i]][1] + 1
                    contents_insert = self.contents_insert.pop()

                    if len(self.contents) > insert_row:
                        self.contents = self.contents[:insert_row] + contents_insert + self.contents[
                                                                                               insert_row:]
                    else:
                        self.contents = self.contents[:insert_row] + contents_insert

                with open(self.current_file_path, 'w', encoding='utf-8') as f:
                    f.writelines(self.contents)
                print("code was revised by VarRegister, please run it again.")
                self.contents = []
                exit()

    def __operate(self):  # 將goto_start到goto_end中間的程式碼都註解掉
        # 讀取該py檔所有內容
        with open(self.current_file_path, 'r', encoding='utf-8') as f:
            contents = f.readlines()
        revise_row = []
        self.revised_if = False
        self.revise_row_start.clear()
        self.revise_row_end.clear()
        for i in range(len(contents)):
            if '.goto_start(' in contents[i] and not '# debug---' in contents[i]:
                tmp = contents[i].split('.goto_start(')[-1]
                tmp = int(tmp.split(')')[0])
                if tmp in self.index_used:
                    revise_row.append(i)
            if '.goto_end(' in contents[i] and not '# debug---' in contents[i]:
                tmp = contents[i].split('.goto_end(')[-1]
                tmp = int(tmp.split(')')[0])
                if tmp in self.index_used:
                    revise_row.append(i)
            if len(revise_row) == 2:
                blank_cnt = self.blank_cnt(contents[revise_row[0]])
                blank_pad = ' ' * blank_cnt
                for j in range(revise_row[0], revise_row[1] + 1):
                    contents[j] = blank_pad + '# debug--- ' + contents[j]
                revise_row = []
                self.revised_if = True
                self.contents = contents

    def __recover(self):  # 將goto_start到goto_end中間註解掉的程式碼恢復原狀
        with open(self.current_file_path, 'r', encoding='utf-8') as f:
            contents = f.readlines()

        revise_row_start = []
        revise_row_end = []
        revise_way = []  # p means part delete, a means all delete

        for i in range(len(contents)):
            if '# debug---' in contents[i]:
                if '.goto_start(' in contents[i]:
                    tmp = contents[i].split('.goto_start(')[-1]
                    tmp = int(tmp.split(')')[0])
                    if tmp in self.index_used:
                        revise_row_start.append(i)
                elif '.goto_end(' in contents[i]:
                    tmp = contents[i].split('.goto_end(')[-1]
                    tmp = int(tmp.split(')')[0])
                    if tmp in self.index_used:
                        revise_row_end.append(i)
                        revise_way.append('p')
                else:
                    pass
            elif '# debug locals start' in contents[i]:
                tmp = contents[i].split('locals start index')[-1]
                tmp = int(tmp.split(', please')[0])
                if tmp in self.index_used:
                    revise_row_start.append(i)
            elif '# debug locals end' in contents[i]:
                tmp = contents[i].split('locals end index')[-1]
                tmp = int(tmp.split(', please')[0])
                if tmp in self.index_used:
                    revise_row_end.append(i)
                    revise_way.append('a')

        if len(revise_way) > 0:
            for i in range(len(revise_way)-1, -1, -1):
                if revise_way[i] == 'p':
                    blank_pad = self.blank_cnt(contents[revise_row_start[i]]) + len('# debug---')
                    for j in range(revise_row_start[i], revise_row_end[i]+1):
                        contents[j] = contents[j][blank_pad+1:]
                elif revise_way[i] == 'a':
                    del contents[revise_row_start[i]:revise_row_end[i]+1]

            with open(self.current_file_path, 'w', encoding='utf-8') as f:
                f.writelines(contents)
            print("code was revised by VarRegister, please run it again.")
            exit()
    '''
    def dump(self, variable, var_name):  # 存下當下要存的變數
        raise BaseException('this function has been deprecated')
        # 輸入是可以是多變數的tuple格式 (var1, var2, var3...)
        # 也可以是dict:   ex{'a':1, 'b':[2,3], 'c':{0:0}}
        with open(var_name + '_pickle_file', 'wb') as f:
            pickle.dump(variable, f)

    def load(self, var_name):  # 載入當下要存的變數
        raise BaseException('this function has been deprecated')
        with open(var_name + '_pickle_file', 'rb') as f:
            var = pickle.load(f)
        return var
    '''

    def dump_all(self, index):  # dump all locals
        #variable = locals()
        variable = inspect.stack()[2][0].f_locals
        var_keys = list(variable.keys())
        for key in var_keys:
            if key in self.ignore_var_list:
                del variable[key]
        with open('debug_assistant_' + str(index) + '_pickle_file', 'wb') as f:
            pickle.dump(variable, f)

    def load_all(self, index):  # load all locals
        raise BaseException('this function has been deprecated')
        with open('debug_assistant_' + str(index) + '_pickle_file', 'rb') as f:
            var = pickle.load(f)
        return var

    def load_pickle(self, pickle_filepath):
        if isinstance(pickle_filepath, int):
            pickle_filepath = 'debug_assistant_' + str(pickle_filepath) + '_pickle_file'

        var = pickle.load(open(pickle_filepath, 'rb'), encoding='iso-8859-1')

        # with open(pickle_filepath) as f:
        #     var = pickle.load(f)
        return var

    def blank_cnt(self, str_input):
        cnt = 0
        for i in range(len(str_input)):
            if str_input[i] == ' ':
                cnt += 1
            else:
                break
        return cnt

    def local_load_code_generate(self, index):
        # goto_end下面加入載入local變數
        contents = self.contents
        row_now = self.index2row_dict[index][1]
        blank_pad = ' ' * self.blank_cnt(contents[row_now])

        contents_add = []
        contents_add.append(blank_pad + '# debug locals start index' + str(index) + ', please do not edit directly\n')
        contents_add.append(blank_pad + str.format('debug_assistant_locals = {}.load_pickle({})\n',
                                                   self.var_register_name, index))
        pickle_filepath = 'debug_assistant_' + str(index) + '_pickle_file'
        variable = self.load_pickle(pickle_filepath)
        for key in variable.keys():
            if key[0:2] != '__':
                contents_add.append(blank_pad + key + ' = ' + 'debug_assistant_locals[\"' + key + '\"]\n')
        contents_add.append(blank_pad + '# debug locals end index' + str(index) + ', please do not edit directly\n')

        self.contents_insert.append(contents_add)

locals()   # 可以印出當下所有區域變數
globals()   # 可以印出當下所有全域變數

# 不要執行的多行程式碼用  ''' 註解
# debug跳過的程式碼用 ctrl + / 註解

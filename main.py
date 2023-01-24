from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from spider import Spider
import os, time, threading

import plyer.platforms.android.notification as notification
from android.storage import app_storage_path
temp_path = os.path.join(app_storage_path(),'temp.txt') 
# temp_path = os.path.join('.','temp.txt') 

from kivy.core.text import LabelBase
LabelBase.register(name='Font_Hanzi',fn_regular='./fonts/SourceHanSerifSC-VF.ttf')

exit_flag = False

def load_data(temp_path):
    ret = []
    with open(temp_path, 'r') as f:
        for _ in range(7):
            ret.append(f.readline()[:-1])
    return ret

def save_data(temp_path, *args):
    with open(temp_path, 'w') as f:
        for argument in args:
            f.write(str(argument))
            f.write('\n')

def auto_update(mainApp, time_delta=8*60*60):
    global exit_flag
    try:
        if os.path.exists(temp_path):
            temp_data = load_data(temp_path)
            id_light, id_aircond = temp_data[0], temp_data[1]
            # kwh_light, kwh_aircond = temp_data[2], temp_data[3]
            thres_light, thres_aircond = int(temp_data[4]), int(temp_data[5])
            time_last = int(temp_data[6])
        else:
            raise RuntimeError('请至少手动查询成功一次后使用后台监测')
        note_auto = notification.instance()
        while not exit_flag:
            time_now = time.localtime()
            if time.time()-time_last>time_delta:
                info = Spider(id_light, id_aircond)
                mainApp.ids.info_label.text = "照明剩余电量：{}度\n空调剩余电量：{}度\n更新时间：{}年{}月{}日{}点{}分{}秒".format(
                    info[0],info[1],
                    time_now.tm_year,time_now.tm_mon,time_now.tm_mday,time_now.tm_hour,time_now.tm_min,time_now.tm_sec)
                time_last = int(time.time())
                save_data(temp_path, id_light, id_aircond, info[0], info[1], thres_light, thres_aircond, time_last)
                if (info[0]<thres_light)and(info[1]<thres_aircond):
                    note_auto.notify(title='低电费警告', message="照明和空调电费均低于阈值！")
                elif info[0]<thres_light:
                    note_auto.notify(title='低电费警告', message="照明电费低于阈值！")
                elif info[1]<thres_aircond:
                    note_auto.notify(title='低电费警告', message="空调电费低于阈值！")
            time.sleep(0.2)
    except Exception as error:
        self.ids.info_label.text = str(error)


class MainWidget(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.checkbox_bg.bind(active=self.checkbox_reaction)
        if os.path.exists(temp_path):
            temp_data = load_data(temp_path)
            self.ids.light.text = temp_data[0]
            self.ids.aircond.text = temp_data[1]
            self.ids.thres_light.text = temp_data[4]
            self.ids.thres_aircond.text = temp_data[5]
            time_last = time.localtime(int(temp_data[6]))
            self.ids.info_label.text = "照明剩余电量：{}度\n空调剩余电量：{}度\n更新时间：{}年{}月{}日{}点{}分{}秒".format(
                temp_data[2],temp_data[3],
                time_last.tm_year,time_last.tm_mon,time_last.tm_mday,time_last.tm_hour,time_last.tm_min,time_last.tm_sec)

    def checkbox_reaction(mainWindow, checkbox, value):
        global exit_flag
        if os.path.exists(temp_path):
            if value:
                exit_flag = False
                thread_bypass = threading.Thread(name='t_bp',target=auto_update,args=(mainWindow,))
                thread_bypass.start()
            else:
                exit_flag = True
        else:
            checkbox.active = False
            mainWindow.ids.info_label.text = '请至少手动查询成功一次后使用后台监测'

    def manual_check(self):
        try:
            if self.ids.light.text.isdigit() and self.ids.aircond.text.isdigit():
                info = Spider(self.ids.light.text, self.ids.aircond.text)
                if info==(): raise RuntimeError('爬取失败')
                else:
                    time_now = time.localtime()
                    self.ids.info_label.text = "照明剩余电量：{}度\n空调剩余电量：{}度\n更新时间：{}年{}月{}日{}点{}分{}秒".format(
                        info[0],info[1],
                        time_now.tm_year,time_now.tm_mon,time_now.tm_mday,time_now.tm_hour,time_now.tm_min,time_now.tm_sec)
                    save_data(temp_path,
                        self.ids.light.text, self.ids.aircond.text,
                        info[0], info[1],
                        self.ids.thres_light.text, self.ids.thres_aircond.text,
                        int(time.time()))
            else: raise RuntimeError('请输入正确电表号')
        except Exception as error:
            self.ids.info_label.text = str(error)

    def show_infoPopup(*args):
        target = infoPopup()
        target.open()


class infoPopup(Popup):
    pass


class MyTask(App):

    def build(self):
        self.mainWindow = MainWidget()
        return self.mainWindow

    def stop(self, *args):
        global exit_flag
        exit_flag = True
        return super().stop(*args)


if __name__ == '__main__':
    MyTask().run()

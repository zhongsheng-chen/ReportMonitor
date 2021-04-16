import sys
import os
from selenium import webdriver
import json
from PIL import Image
import pytesseract
import time
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from ReportMonitor_UI import Ui_MainWindow
import threading
from win10toast import ToastNotifier

goalurl = "yjsy.buct.edu.cn:8080"


class login(QThread):
    show_yzm_signal = pyqtSignal(int)
    monitor_signal = pyqtSignal(str)
    ocr_signal = pyqtSignal(str)
    toast_signal = pyqtSignal(str, int)
    user = 0
    password = 0
    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    myList = list()

    def __init__(self, *args, **kwargs):
        self.driver = webdriver.Chrome(options=self.option)
        self.driver.get("http://" + goalurl + "/pyxx/login.aspx")
        self.aElement = self.driver.find_element_by_xpath('./*//title')
        print(self.aElement.get_attribute("innerText"))
        self.driver.set_window_size(1024, 768)
        self.yzm = ""
        self.flagFirst = True
        return super().__init__(*args, **kwargs)

    def __del__(self):
        self.flagFirst = True

    def run(self, i=1, user=0, password=0):

        if (user != 0) and (password != 0):
            self.user = user
            self.password = password
        try:

            self.driver.find_element_by_xpath("./*//input[@name='_ctl0:txtusername']").clear()
            self.driver.find_element_by_xpath("./*//input[@name='_ctl0:txtusername']").send_keys(self.user)
            self.driver.find_element_by_xpath("./*//input[@name='_ctl0:txtpassword']").clear()
            self.driver.find_element_by_xpath("./*//input[@name='_ctl0:txtpassword']").send_keys(self.password)
            self.driver.get_screenshot_as_file('screenshot.png')
            yzmElement = self.driver.find_element_by_xpath("./*//input[@name='_ctl0:txtyzm']/../img")
            left = int(yzmElement.location['x'])
            top = int(yzmElement.location['y'])
            right = int(yzmElement.location['x'] + yzmElement.size['width'])
            bottom = int(yzmElement.location['y'] + yzmElement.size['height'])
            img = Image.open('screenshot.png')
            img = img.crop((left, top, right, bottom))
            # img=img.crop((left, top, right, bottom))
            img.save('code.png')
            self.show_yzm_signal.emit(i)
        except:
            self.show_yzm_signal.emit(9)

    def yzmCrop(self):
        # ## Zhongsheng modified on 15th April, 2021
        self.driver.set_window_size(1280, 1024)

        self.driver.get_screenshot_as_file('screenshot_no_save.png')
        yzmElement = self.driver.find_element_by_xpath("./*//input[@name='txtyzm']/../img")
        bottomTable = self.driver.find_element_by_xpath("./*//table[@id='Table2']/tbody/tr[3]")
        img = Image.open('screenshot.png')
        left = int(yzmElement.location['x'])

        # top = int(yzmElement.location['y'])
        # top = img.height - 32 - yzmElement.size['height'] #- bottomTable.size['height']
        if int(yzmElement.location['y'] + yzmElement.size['height']) > img.height:
            bottom = img.height
        else:
            bottom = int(yzmElement.location['y'] + yzmElement.size['height'])
        top = bottom - yzmElement.size['height']
        right = int(yzmElement.location['x'] + yzmElement.size['width'])
        # bottom = int(yzmElement.location['y'] + yzmElement.size['height'])
        print((left, top, right, bottom))
        img = img.crop((left, top, right, bottom))
        img.save('code.png')
        self.show_yzm_signal.emit(4)
        self.toast_signal.emit("有可抢报告，请输入验证码！", -1)

    def monitor(self):
        url = "http://" + goalurl + "/pyxx/txhdgl/hdlist.aspx?xh=" + self.user
        self.driver.get(url)
        target = self.driver.find_element_by_xpath("./*//input[@name='txtyzm']/../img")
        self.driver.execute_script("arguments[0].scrollIntoView(false);", target)  # 拖动到可见的元素去
        try:
            tempList = self.driver.find_elements_by_xpath("./*//img[@alt='提交心得']")
        except:
            tempList = []
        if ((len(tempList) - len(self.myList)) == 1 and self.flagFirst == False):
            self.show_yzm_signal.emit(5)
        self.myList = tempList
        self.flagFirst = False
        i = 1
        while (1):
            reportList = self.driver.find_elements_by_xpath("./*//img[@alt='我要报名']")
            string = str(i) + ' '
            for each in reportList:
                leapflag = False
                maxNum = each.find_element_by_xpath("../../../td[7]").get_attribute("innerText")
                nowNum = each.find_element_by_xpath("../../../td[8]").get_attribute("innerText")
                if nowNum < maxNum:
                    reportName = each.find_element_by_xpath("../../../td[2]").get_attribute("innerText")
                    with open('overlook.txt', 'r') as f:
                        for x in f.readlines():
                            if reportName == x[:-1]:
                                leapflag = True
                                string = string + reportName + " 在屏蔽列表中，不选择。"
                    if leapflag == False:
                        self.monitor_signal.emit(
                            string + "！有可抢报告！" + "\r\n" + each.find_element_by_xpath("../../../td[2]").get_attribute(
                                "innerText") + "\r\n" + each.find_element_by_xpath("../../../td[4]").get_attribute(
                                "innerText") + "\r\n地点：" + each.find_element_by_xpath("../../../td[6]").get_attribute(
                                "innerText") + "\r\n剩余人数：" + str(int(maxNum) - int(nowNum)))
                        self.yzmCrop()
                        self.aElement = each
                        return
            self.monitor_signal.emit(string)
            time.sleep(5)
            i = i + 1
            self.driver.refresh()

    def choseLesson(self):
        url = "http://" + goalurl + "/PYXX/pygl/pyjhxk.aspx?xh=" + self.user
        self.driver.get(url)
        i = 1
        while (1):
            n = 0
            lessonList = self.driver.find_elements_by_xpath("./*//img[@alt='选择当前课程']")
            if lessonList == []:
                self.monitor_signal.emit("没有可选课程,已结束检测。")
                return
            string = str(i) + ' '
            for each in lessonList:
                lessonName = each.find_element_by_xpath("../../../td[5]").get_attribute("innerText")
                lessonRoom = each.find_element_by_xpath("../../../td[2]").get_attribute("innerText")
                lessonTime = each.find_element_by_xpath("../../../td[7]").get_attribute("innerText")
                lessonStatus = each.find_element_by_xpath("../../../td[12]").get_attribute("innerText")
                if "未满" in lessonStatus:
                    with open('choseLesson.txt', 'r') as f:
                        for x in f.readlines():
                            if lessonName == x[:-1]:
                                self.monitor_signal.emit(string + lessonName + "检测到未满，尝试选择。")
                                each.click()
                                time.sleep(1)
                                self.judge()
                                break
                                # if self.examine(x,url):
                                #    self.monitor_signal.emit(string + lessonName +"选课成功。")
                                #    self.toast_signal.emit(lessonName+"  选课成功！",-1)
                                # else:
                                #    self.toast_signal.emit(lessonName+"  检测到未满。",5)
                else:
                    n = n + 1
                    pass
            self.monitor_signal.emit(string + ' ' + str(n) + "课(班)已满")
            time.sleep(3)
            i = i + 1
            self.driver.get(url)

    def examine(self, cLessonName, url):
        try:
            self.driver.get(url)
            lessonList = self.driver.find_elements_by_xpath("./*//img[@alt='退选当前课程']")
            for each in lessonList:
                lessonName = each.find_element_by_xpath("../../../td[5]").get_attribute("innerText")
                print(lessonName)
                if cLessonName == lessonName:
                    return True
            return False
        except Exception as e:
            self.monitor_signal.emit("[examine]:" + str(e))
            return False

    def judge(self):
        return self._judgeWait()

    def _judgeWait(self):
        while (1):
            try:
                # cookie_items = self.driver.get_cookies()
                # post={}
                # for cookie_item in cookie_items:
                #    post[cookie_item['name']] = cookie_item['value']
                # cookie_str = json.dumps(post)
                # with open('cookie.txt', 'w+', encoding='utf-8') as f:
                #    f.write(cookie_str)
                # time.sleep(2)
                temp = self.driver.get_cookies()
                print("come here and temp: ", temp)
                return True
            except:
                try:
                    # al=self.driver.switch_to_alert()
                    al = self.driver.switch_to.alert()
                    print("come here and alert")
                    al.accept()
                    return False
                except:
                    time.sleep(1)

    def ocr(self):
        self.yzm = pytesseract.image_to_string(Image.open('code.png'))
        self.yzm = self.yzm[0:4]
        if '\n' in self.yzm or '\r\n' in self.yzm:
            self.yzm = ''
        self.monitor_signal.emit("识别验证码：" + self.yzm)
        self.ocr_signal.emit(str(self.yzm))
        time.sleep(1)

    def doinput(self, yzmInput, mode=False):
        try:
            self.driver.find_element_by_xpath("./*//input[@name='_ctl0:txtyzm']").clear()
            self.driver.find_element_by_xpath("./*//input[@name='_ctl0:txtyzm']").send_keys(yzmInput)
            self.driver.find_element_by_xpath("./*//input[@name='_ctl0:ImageButton1']").click()
            time.sleep(1)
            if (not self.judge()):
                self.run(2)
            else:
                self.show_yzm_signal.emit(0)
                self.driver.refresh()
                time.sleep(1)
                self.monitor_signal.emit(self.driver.find_element_by_xpath('./*//title').get_attribute("innerText"))
                if mode:
                    self.choseLesson()
                else:
                    self.monitor()
        except Exception as e:
            self.monitor_signal.emit("[doinput]:" + str(e))

    def doreport(self, yzmInput):
        try:
            self.driver.find_element_by_xpath("./*//input[@name='txtyzm']").clear()
            self.driver.find_element_by_xpath("./*//input[@name='txtyzm']").send_keys(yzmInput)
            self.aElement.click()
            time.sleep(0.5)
            # al=self.driver.switch_to_alert()
            al = self.driver.switch_to.alert()
            al.accept()
            time.sleep(1)
            self.judge()
            self.monitor()
        except Exception as e:
            self.monitor_signal.emit("[doreport]:" + str(e))

    def quit(self):
        self.driver.quit()


class creatLink(QThread):
    creat_link_signal = pyqtSignal(login)

    def __init__(self, parent=None):
        return super().__init__(parent)

    def run(self):
        self.Thread = login()
        self.creat_link_signal.emit(self.Thread)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.start.clicked.connect(self.run)
        self.button_linkWeb.clicked.connect(self.link)
        self.button_txt.clicked.connect(self.overlook)
        self.stop.clicked.connect(self.stopAll)
        self.button_saveID.clicked.connect(self.saveID)
        self.check_toast.stateChanged.connect(self.__toastFlag)
        # self.menu_doTest.triggered.connect(self.__choseLesson)
        self.openWeb.setOpenExternalLinks(True)
        self.flag = 0
        self.toaster = ToastNotifier()
        self.toastFlag = self.check_toast.isChecked()
        try:
            with open('cookie.txt', 'r') as f:
                cookie = f.readlines()
                self.Line_stID.setText(cookie[0][:-1])
                self.Line_password.setText(cookie[1])
        except Exception as e:
            self.showMonitor("[cookie]: " + str(e))

    def __choseLesson(self):
        threading.Thread(target=self.thread.choseLesson, args=()).start()

    def _toast(self, string, sec=5):
        if self.toastFlag:
            try:
                if self.ocr.isChecked() == True:
                    sec = 5
                self.toaster.show_toast("ReportMonitor", string, icon_path='icon.ico', duration=sec, threaded=True)
            except:
                self.textBrowser.append(
                    str(time.asctime(time.localtime(time.time())))[-13:-5] + " ：" + "弹出系统提示失败，内容：" + string)

    def __toastFlag(self):
        self.toastFlag = self.check_toast.isChecked()
        self._toast("通知已打开")

    def saveID(self):
        string = self.Line_stID.text() + "\n" + self.Line_password.text()
        try:
            with open('cookie.txt', 'w+') as f:
                f.write(string)
            self._toast("帐号保存成功")
        except:
            self._toast("帐号保存失败")

    def _link(self, x):
        self.thread = x
        self.thread.show_yzm_signal.connect(self.yzmLoad)
        self.thread.monitor_signal.connect(self.showMonitor)
        self.thread.ocr_signal.connect(self.ocrWork)
        self.thread.toast_signal.connect(self._toast)
        self.Label_linkStatus.setText("已连接")

    def stopAll(self):
        try:
            self.thread.quit()
            self.retranslateUi(self)
            self.Label_linkStatus.setText("连接断开")
            del self.thread
            del self.creat
        except Exception as e:
            self.showMonitor("[Stop]: " + str(e))

    def ocrWork(self, string):
        self.Line_yzm.setText(string)
        self.yzmShow()

    def showMonitor(self, string):
        self.textBrowser.append(str(time.asctime(time.localtime(time.time())))[-13:-5] + " ：" + string)

    def link(self):
        try:
            self.Label_linkStatus.setText("正在连接")
            self.creat = creatLink()
            self.creat.start()
            self.creat.creat_link_signal.connect(self._link)
        except:
            self.Label_linkStatus.setText("连接失败，请重试")

    def overlook(self):
        threading.Thread(target=os.system, args=('overlook.txt',)).start()

    def run(self):
        try:
            self.thread.user = self.Line_stID.text()
            self.thread.password = self.Line_password.text()
            self.thread.start()
        except:
            self.textBrowser.append(str(time.asctime(time.localtime(time.time())))[-13:-5] + " ：" + "还没有连接到网站")

    def yzmLoad(self, flag):
        self.pic_yzm.setPixmap(QPixmap('code.png'))
        {'0': lambda: self.Label_news.setText("登录成功\r\n开始监测"), '1': lambda: self.Label_news.setText("请输入验证码\r\n然后按下回车"),
         '2': lambda: self.Label_news.setText("登录失败\r\n请检查帐号密码并重试"),
         '4': lambda: self.Label_news.setText("检测到可抢报告\r\n请输入验证码"),
         '5': lambda: self.Label_news.setText("有抢到的报告\r\n请登录网站查看"), '9': lambda: self.Label_news.setText("error")}[
            str(flag)]()
        self.flag = flag
        if self.ocr.isChecked() == True and flag != 0 and flag != 5:
            threading.Thread(target=self.thread.ocr).start()
        # if flag==0:
        #    self.openWeb.setText("<A href='http://202.4.152.190:8080/pyxx/Default.aspx'>教务网</a>")
        if flag == 5:
            self._toast("有成功抢到的报告，请自行登录研究生管理系统查看详情。", -1)

    def yzmShow(self):
        try:
            self.Label_news.setText("请稍候")
            if self.flag == 4:
                threading.Thread(target=self.thread.doreport, args=(self.Line_yzm.text(),)).start()
            else:
                threading.Thread(target=self.thread.doinput,
                                 args=(self.Line_yzm.text(), self.menu_L.isChecked(),)).start()
            self.Line_yzm.clear()
        except Exception as e:
            self.showMonitor("[验证码]: " + str(e))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import string
import sys
import threading
import time
from datetime import datetime

import cv2
import pytesseract
import winsound
from PIL import Image
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import UnexpectedAlertPresentException
from win10toast import ToastNotifier

from Logger import Logger
from Notification import send_notification
from ReportMonitor_UI import Ui_MainWindow

login_addr = "http://yjsy.buct.edu.cn:8080/pyxx/login.aspx"
report_addr = "http://yjsy.buct.edu.cn:8080/pyxx/txhdgl/hdlist.aspx?xh="
lesson_addr = "http://yjsy.buct.edu.cn:8080//PYXX/pygl/pyjhxk.aspx?xh="

log = Logger('log.log', level='info')


class UserNotExistError(Exception):
    def __init__(self, err="用户名不存在"):
        Exception.__init__(self, err)


class ValidCaptchaError(Exception):
    def __init__(self, err="验证码非法"):
        Exception.__init__(self, err)


class CaptchaWrongError(Exception):
    def __init__(self, err="验证码错误"):
        Exception.__init__(self, err)


class Login(QThread):
    ask_feedback_signal = pyqtSignal(int)
    monitor_signal = pyqtSignal(str)
    prepare_captcha_signal = pyqtSignal(str)
    toast_signal = pyqtSignal(str, int)

    refresh_login_captcha_signal = pyqtSignal()
    refresh_captcha_signal = pyqtSignal()

    user = 0
    password = 0
    option = webdriver.ChromeOptions()
    option.add_argument("--start-maximized")
    option.add_argument('window-size=1536, 824')
    option.add_argument('headless')
    report_list = list()

    def __init__(self, *args, **kwargs):
        self.driver = webdriver.Chrome(options=self.option)
        self.driver.get(login_addr)

        self.page_element = self.driver.find_element_by_xpath('./*//title')
        print(self.page_element.get_attribute("innerText"))

        self.captcha = "captcha"
        self.flag_first = True
        self.has_login_captcha_cropped = False
        self.has_captcha_cropped = False

        return super().__init__(*args, **kwargs)

    def __del__(self):
        self.flag_first = True

    def run(self, i=1, user=0, password=0):
        if (user != 0) and (password != 0):
            self.user = user
            self.password = password
        try:

            self.login_captcha_cropping()
            self.ask_feedback_signal.emit(i)

        except Exception as e:
            self.ask_feedback_signal.emit(9)
            log.logger.error(e)

    def monitor(self):
        url = report_addr + self.user
        self.driver.get(url)
        target = self.driver.find_element_by_xpath("./*//input[@name='txtyzm']/../img")
        self.driver.execute_script("arguments[0].scrollIntoView(false);", target)  # 拖动到可见的元素去

        try:
            previous_report_list = self.driver.find_elements_by_xpath("./*//img[@alt='提交心得']")
        except:
            previous_report_list = []
        if (len(previous_report_list) - len(self.report_list)) == 1 and self.flag_first is False:
            new_report = list(filter(lambda rep: rep not in previous_report_list, self.report_list))[0]
            new_report_name = new_report.find_element_by_xpath("../../../td[2]").get_attribute("innerText")
            new_report_date = new_report.find_element_by_xpath("../../../td[4]").get_attribute("innerText")
            new_report_location = new_report.find_element_by_xpath("../../../td[6]").get_attribute("innerText")
            new_report_info = f"报告名称：{new_report_name}\r\n" \
                              f"报告时间：{new_report_date}\r\n" \
                              f"报告地点：{new_report_location}"

            self.ask_feedback_signal.emit(5, f"已经抢到报告...\r\n" + new_report_info)
            log.logger.info(f"已经抢到报告...\r\n" + new_report_info)
        self.report_list = previous_report_list
        self.flag_first = False

        i = 1
        while True:
            reports = self.driver.find_elements_by_xpath("./*//img[@alt='我要报名']")
            string = f"第{i}次监听..."

            for report in reports:
                leapflag = False
                max_num = report.find_element_by_xpath("../../../td[7]").get_attribute("innerText")
                now_num = report.find_element_by_xpath("../../../td[8]").get_attribute("innerText")
                if now_num < max_num:
                    report_name = report.find_element_by_xpath("../../../td[2]").get_attribute("innerText")
                    with open('overlook.txt', 'r') as f:
                        for x in f.readlines():
                            if report_name == x[:-1]:
                                leapflag = True
                                string = string + report_name + " 在屏蔽列表中，不选择。"
                    if leapflag == False:
                        report_name = report.find_element_by_xpath("../../../td[2]").get_attribute("innerText")
                        report_date = report.find_element_by_xpath("../../../td[4]").get_attribute("innerText")
                        report_location = report.find_element_by_xpath("../../../td[6]").get_attribute("innerText")
                        report_availability = str(int(max_num) - int(now_num))
                        report_info = f"报告名称：{report_name}\r\n报告时间：{report_date}\r\n" \
                                      f"报告地点：{report_location}\r\n可报名人数：{report_availability}"

                        self.monitor_signal.emit(string + f"！发现报告...\r\n" + report_info)
                        self.captcha_cropping()
                        self.page_element = report
                        self.ask_feedback_signal.emit(4)
                        self.toast_signal.emit("发现报告，请输入验证码", -1)

                        winsound.PlaySound("RemindMe.wav", winsound.SND_FILENAME)
                        send_notification(f"发现报告...\r\n" + report_info)
                        log.logger.info(f"发现报告...\r\n" + report_info)
                        return

            self.monitor_signal.emit(string)
            log.logger.info(string)

            time.sleep(3)
            i = i + 1
            self.driver.refresh()

    def chose_lesson(self):
        url = lesson_addr + self.user
        self.driver.get(url)
        i = 1
        while 1:
            n = 0
            lesson_list = self.driver.find_elements_by_xpath("./*//img[@alt='选择当前课程']")
            if lesson_list == []:
                self.monitor_signal.emit("没有可选课程,已结束检测。")
                return
            string = str(i) + ' '
            for lesson in lesson_list:
                lesson_name = lesson.find_element_by_xpath("../../../td[5]").get_attribute("innerText")
                lesson_room = lesson.find_element_by_xpath("../../../td[2]").get_attribute("innerText")
                lesson_data = lesson.find_element_by_xpath("../../../td[7]").get_attribute("innerText")
                lesson_status = lesson.find_element_by_xpath("../../../td[12]").get_attribute("innerText")
                if "未满" in lesson_status:
                    with open('choseLesson.txt', 'r') as f:
                        for x in f.readlines():
                            if lesson_name == x[:-1]:
                                self.monitor_signal.emit(string + lesson_name + "检测到未满，尝试选择。")
                                lesson.click()
                                time.sleep(1)
                                self.judge()
                                break
                else:
                    n = n + 1
                    pass
            self.monitor_signal.emit(string + ' ' + str(n) + "课(班)已满")
            time.sleep(3)
            i = i + 1
            self.driver.get(url)

    def judge(self):
        return self._judge()

    def _judge(self):
        while 1:
            try:
                all_cookies = self.driver.get_cookies()
                print("All cookies are ", all_cookies)
                return True
            except:
                try:

                    al = self.driver.switch_to.alert()
                    print("Driver alert")
                    al.accept()
                    return False

                except:
                    time.sleep(0.1)

    def ocr(self):
        img = cv2.imread("code.png")
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        img = cv2.inRange(img, lowerb=180, upperb=255)
        cv2.imwrite('code_denoise.png', img)
        img = Image.fromarray(img)
        captcha = pytesseract.image_to_string(img)
        exclude_char_list = ' .·:`‘、“\\|\'\"?![],()~@#$%^&*_+-={};<>/¥'
        captcha = ''.join([ch for ch in captcha if ch not in exclude_char_list])

        whitespace = ['\f', '\n', '\r', '\t', '\v', '\u00A0', '\u2028', '\u2029']
        captcha = ''.join(
            filter(lambda x: x not in whitespace, filter(lambda x: x in string.printable, captcha))).strip(
            ' \r\n\f\t\b\v\0')

        if not len(captcha):
            captcha = "captcha"

        self.captcha = captcha
        self.monitor_signal.emit("识别验证码：" + self.captcha)
        self.prepare_captcha_signal.emit(str(self.captcha))
        time.sleep(0.1)

    def do_input(self, captcha="captcha", mode=True):
        try:
            self.driver.find_element_by_xpath("./*//input[@name='_ctl0:txtyzm']").clear()
            self.driver.find_element_by_xpath("./*//input[@name='_ctl0:txtyzm']").send_keys(captcha)
            self.driver.find_element_by_xpath("./*//input[@name='_ctl0:ImageButton1']").click()
            self.monitor_signal.emit(f"正在尝试打开...")
            time.sleep(0.1)

            if self.judge():

                self.driver.refresh()
                time.sleep(0.1)

                head = self.driver.find_element_by_xpath('./*//title').get_attribute("innerText")
                self.monitor_signal.emit(head.strip() + f"研究生信息管理系统" + f"打开成功")

                if mode:
                    self.ask_feedback_signal.emit(0)
                    self.monitor()
                else:
                    self.chose_lesson()

            else:
                self.run(2)

        except UnexpectedAlertPresentException as e:

            if "你输入的验证码错误" in str(e):
                self.monitor_signal.emit("验证码错误，请重新输入")
                self.login_captcha_cropping()
                self.has_login_captcha_cropped = True
                self.refresh_login_captcha_signal.emit()
                self.ask_feedback_signal.emit(1)
                log.logger.error(f"验证码错误")

            elif "请输入验证码" in str(e):
                self.monitor_signal.emit("请输入验证码")
                self.login_captcha_cropping()
                self.has_login_captcha_cropped = True
                self.refresh_login_captcha_signal.emit()
                log.logger.error(f"验证码非法")

            elif "用户名不存在" in str(e):
                self.monitor_signal.emit("用户名不存在")
                self.login_captcha_cropping()
                self.has_login_captcha_cropped = True
                self.refresh_login_captcha_signal.emit()
                log.logger.error(f"用户名不存在")

            elif "密码错误" in str(e):
                self.monitor_signal.emit("密码错误")
                self.login_captcha_cropping()
                self.has_login_captcha_cropped = True
                self.refresh_login_captcha_signal.emit()
                log.logger.error(f"密码错误")

            elif "该学号不存在" in str(e):
                self.monitor_signal.emit("该学号不存在")
                self.login_captcha_cropping()
                self.has_login_captcha_cropped = True
                self.refresh_login_captcha_signal.emit()
                log.logger.error(f"学号不存在")

            else:
                self.monitor_signal.emit(str(e))
                log.logger.error(e)

        except Exception as e:
            self.monitor_signal.emit(str(e))
            log.logger.error(e)

    def do_report(self, captcha="captcha"):
        try:
            self.driver.find_element_by_xpath("./*//input[@name='txtyzm']").clear()
            self.driver.find_element_by_xpath("./*//input[@name='txtyzm']").send_keys(captcha)
            self.page_element.click()
            time.sleep(0.5)
            alert = self.driver.switch_to.alert
            alert.accept()
            time.sleep(0.5)

            if self.judge():  # if register a report successfully, do it again
                self.monitor_signal.emit("报名验证成功")
                log.logger.info("报名验证成功")
                self.monitor()
            else:  # if not, refresh captcha to prepare for next attempts
                self.monitor_signal.emit("报名验证失败")
                self.driver.refresh()
                self.captcha_cropping()
                self.has_captcha_cropped = True
                self.refresh_captcha_signal.emit()
                self.ask_feedback_signal.emit(4)
                log.logger.error("报名验证失败")

        except Exception as e:

            try:
                if "报名已满" in str(e):
                    self.monitor()
                elif "验证码错误" in str(e):
                    self.monitor_signal.emit("报名验证码错误")
                    self.driver.refresh()
                    self.captcha_cropping()
                    self.has_captcha_cropped = True
                    self.refresh_captcha_signal.emit()
                    self.ask_feedback_signal.emit(4)
                    log.logger.error("报名验证码错误")

                else:
                    self.monitor_signal.emit("报名验证异常。" + str(e))
                    self.driver.refresh()
                    self.captcha_cropping()
                    self.has_captcha_cropped = True
                    self.refresh_captcha_signal.emit()
                    self.ask_feedback_signal.emit(4)
                    log.logger.error("报名验证异常。" + str(e))

                    # self.monitor()

            except Exception as e:
                self.monitor()
                self.monitor_signal.emit(str(e))
                log.logger.error(e)

    def quit(self):
        self.driver.quit()

    def check_connection(self):
        try:
            self.driver.get(self.driver.current_url)
            return True
        except WebDriverException:
            try:
                retries = 5
                while retries > 0:
                    try:
                        self.driver.get(self.driver.current_url)
                        break
                    except Exception as e:

                        Logger.warning("未知错误。" + e)
                        return False
            except TimeoutException:

                Logger.warning("访问网页超时")
                return False

    def load_username_password(self):
        self.driver.find_element_by_xpath("./*//input[@name='_ctl0:txtusername']").clear()
        self.driver.find_element_by_xpath("./*//input[@name='_ctl0:txtusername']").send_keys(self.user)
        self.driver.find_element_by_xpath("./*//input[@name='_ctl0:txtpassword']").clear()
        self.driver.find_element_by_xpath("./*//input[@name='_ctl0:txtpassword']").send_keys(self.password)

    def _login_captcha_cropping(self, element):
        captcha_element = self.driver.find_element_by_xpath(element)
        left = int(captcha_element.location['x'])
        top = int(captcha_element.location['y'])
        right = int(captcha_element.location['x'] + captcha_element.size['width'])
        bottom = int(captcha_element.location['y'] + captcha_element.size['height'])
        img = Image.open('screenshot.png')
        img = img.crop((left + 1, top + 1, right - 1, bottom - 1))
        img.save('code.png')

    def login_captcha_cropping(self):
        self._reset_max_window()
        self.load_username_password()
        self.driver.get_screenshot_as_file('screenshot.png')
        self._login_captcha_cropping("./*//input[@name='_ctl0:txtyzm']/../img")

    def _captcha_cropping(self, element):
        img = Image.open('screenshot.png')
        captcha_element = self.driver.find_element_by_xpath(element)
        left = int(captcha_element.location['x'])
        right = int(captcha_element.location['x'] + captcha_element.size['width'])
        if int(captcha_element.location['y'] + captcha_element.size['height']) > img.height:
            bottom = img.height
        else:
            bottom = int(captcha_element.location['y'] + captcha_element.size['height'])
        top = bottom - int(captcha_element.size['height'])
        bottom = int(captcha_element.location['y'] + captcha_element.size['height'])
        img = img.crop((left + 0.5, top + 1.5, right - 0.5, bottom - 16))
        img.save('code.png')

    def captcha_cropping(self):
        self._reset_max_window()
        self.driver.get_screenshot_as_file('screenshot.png')
        self._captcha_cropping("./*//input[@name='txtyzm']/../img")

    def _reset_max_window(self):
        self.driver.maximize_window()
        current_window_size = self.driver.get_window_size()
        width = current_window_size["width"]
        height = current_window_size["height"]
        self.driver.set_window_size(width, height)


class Connection(QThread):
    creat_connection_signal = pyqtSignal(Login)

    def __init__(self, parent=None):
        self.thread = Login()
        return super().__init__(parent)

    def run(self):
        self.creat_connection_signal.emit(self.thread)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.button_start.clicked.connect(self.validate_captcha)
        self.button_connect.clicked.connect(self.make_connection)

        self.button_block_list.clicked.connect(self.block_report)
        self.button_stop.clicked.connect(self.stop_all)
        self.button_save_account.clicked.connect(self.save_account)
        self.check_toast.stateChanged.connect(self.__toast_flag)
        self.line_captcha.returnPressed.connect(self.refresh_login_captcha)

        self.label_to_website.setOpenExternalLinks(True)

        self.flag = -1
        self.toaster = ToastNotifier()
        self.toast_flag = self.check_toast.isChecked()

        self.button_start.setEnabled(False)
        self.button_stop.setEnabled(False)
        self.button_block_list.setEnabled(False)
        self.line_captcha.setEnabled(False)

        try:
            with open('cookie.txt', 'r') as f:
                cookie = f.readlines()
                self.line_student_id.setText(cookie[0][:-1])
                self.line_password.setText(cookie[1])
        except Exception as e:
            self.show_monitor("打开cookie文件失败。" + e)

    def __chose_lesson(self):
        threading.Thread(target=self.thread.chose_lesson, args=()).start()

    def _toast(self, toast_str, sec=5):
        if self.toast_flag:
            try:
                if self.check_auto.isChecked() is True:
                    sec = 5
                self.toaster.show_toast("ReportMonitor", toast_str, icon_path='icon.ico', duration=sec, threaded=True)
            except Exception as e:
                self.text_info_board.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + e)

    def __toast_flag(self):
        self.toast_flag = self.check_toast.isChecked()
        self._toast("通知已打开")

    def save_account(self):
        id_and_pwd = self.line_student_id.text() + "\n" + self.line_password.text()
        try:
            with open('cookie.txt', 'w+') as f:
                f.write(id_and_pwd)
            self._toast("帐号保存成功")
        except:
            self._toast("帐号保存失败")

    def _make_connection(self, x):
        self.thread = x
        self.thread.ask_feedback_signal.connect(self.ask_feedback)
        self.thread.monitor_signal.connect(self.show_monitor)
        self.thread.prepare_captcha_signal.connect(self.prepare_captcha)
        self.thread.toast_signal.connect(self._toast)
        self.thread.refresh_login_captcha_signal.connect(self.refresh_login_captcha)
        self.thread.refresh_captcha_signal.connect(self.refresh_captcha)
        self.label_connection_status.setText("已连接")
        self.run()

    def make_connection(self):
        try:
            self.label_connection_status.setText("正在连接")
            self.creat = Connection()
            self.creat.start()
            self.creat.creat_connection_signal.connect(self._make_connection)

            self.button_start.setEnabled(True)
            self.button_stop.setEnabled(True)
            self.button_block_list.setEnabled(True)
            self.line_captcha.setEnabled(True)

        except Exception as e:
            self.label_connection_status.setText("连接失败，请重试")
            self.show_monitor(str(e))
            log.logger.error("连接失败。" + e)

    def stop_all(self):
        try:
            self.thread.quit()
            self.retranslateUi(self)
            self.label_connection_status.setText("连接断开")
            self.button_connect.setEnabled(True)
            self.button_start.setEnabled(False)
            self.button_stop.setEnabled(False)
            self.button_block_list.setEnabled(False)
            self.line_captcha.setEnabled(False)

            del self.thread
            del self.creat
            log.logger.info("连接断开")
        except Exception as e:
            self.show_monitor(str(e))
            log.logger.error(e)

    def prepare_captcha(self, captcha):
        self.line_captcha.setText(captcha)
        self.validate_captcha()

    def refresh_login_captcha(self):
        try:
            if self.thread.has_login_captcha_cropped:
                self.label_captcha_pic.setPixmap(QPixmap('code.png'))
                self.thread.has_login_captcha_cropped = False

                self.show_monitor("登录验证码已重新加载")
                log.logger.info(f"登录验证码已重新加载")

            else:
                self.thread.driver.get(self.thread.driver.current_url)
                self.thread.login_captcha_cropping()
                self.label_captcha_pic.setPixmap(QPixmap('code.png'))

                self.show_monitor("登录验证码已更新")
                log.logger.info(f"登录验证码已更新")

        except Exception as e:
            self.show_monitor(str(e))
            log.logger.error(e)

    def refresh_captcha(self):
        try:

            if self.thread.has_captcha_cropped:
                self.label_captcha_pic.setPixmap(QPixmap('code.png'))
                self.thread.has_captcha_cropped = False

                self.show_monitor("报告验证码已更新")
                log.logger.info(f"报告验证码已更新")

            else:
                self.thread.driver.get(self.thread.driver.current_url)
                self.thread.captcha_cropping()
                self.label_captcha_pic.setPixmap(QPixmap('code.png'))

                self.show_monitor("报告验证码已更新")
                log.logger.info(f"报告验证码已更新")

        except Exception as e:
            self.show_monitor(str(e))
            log.logger.error(e)

    def show_monitor(self, string):
        self.text_info_board.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' ' + string)

    def block_report(self):
        threading.Thread(target=os.system, args=('overlook.txt',)).start()

    def run(self):
        try:
            self.thread.user = self.line_student_id.text()
            self.thread.password = self.line_password.text()
            self.thread.start()
        except Exception as e:
            self.text_info_board.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' ' + "还没有连接到网站")
            log.logger.error("还没有连接到网站。" + e)

    def ask_feedback(self, flag, report_info=""):
        self.label_captcha_pic.setPixmap(QPixmap('code.png'))
        {'-1': lambda: self.label_feedback.setText("请稍候..."),
         '0': lambda: self.label_feedback.setText("登录成功\r\n开始监测"),
         '1': lambda: self.label_feedback.setText("请输入验证码\r\n"),
         '2': lambda: self.label_feedback.setText("登录失败\r\n请检查帐号密码并重试"),
         '4': lambda: self.label_feedback.setText("检测到可抢报告\r\n请输入验证码"),
         '5': lambda: self.label_feedback.setText("有抢到的报告\r\n请登录网站查看"),
         '9': lambda: self.label_feedback.setText("登录异常")}[
            str(flag)]()
        self.flag = flag

        if flag == -1:
            self.button_connect.setEnabled(False)

        if flag == 0:
            self.button_connect.setEnabled(False)
            self.line_captcha.returnPressed.disconnect()
            self.show_monitor("登录成功")
            log.logger.info(f"登录成功")

        if flag == 1:
            self.button_start.setEnabled(True)
            self.button_connect.setEnabled(False)

        if flag == 2:
            self.button_connect.setEnabled(True)
            self.show_monitor("登录失败，请检查帐号密码并重试")
            log.logger.error(f"登录失败，请检查帐号密码并重试")

        if flag == 4:
            self.button_start.setEnabled(True)
            self.button_connect.setEnabled(False)

        if flag == 5:
            self.button_connect.setEnabled(False)
            self._toast("有成功抢到的报告，请自行登录研究生管理系统查看详情。", -1)
            send_notification(report_info)
            log.logger.info("有成功抢到的报告：" + report_info)

        if flag == 9:
            self.button_connect.setEnabled(True)

        if self.check_auto.isChecked():
            self.button_start.setEnabled(False)

        if self.check_auto.isChecked() is True:
            if flag == 1 or flag == 4:
                threading.Thread(target=self.thread.ocr).start()
        else:
            if flag == 4:
                self.line_captcha.returnPressed.connect(self.refresh_captcha)

    def validate_captcha(self):
        try:

            if self.flag == 4:
                threading.Thread(target=self.thread.do_report, args=(self.line_captcha.text(),)).start()
            else:
                threading.Thread(target=self.thread.do_input,
                                 args=(self.line_captcha.text(),
                                       self.menu_report.isChecked(),)).start()
            self.line_captcha.clear()

        except CaptchaWrongError:
            self.show_monitor("验证码错误")
            log.logger.error("验证码错误")
        except UserNotExistError:
            self.show_monitor("用户名不存在")
            log.logger.error("用户名不存在")
        except ValidCaptchaError:
            self.show_monitor("验证码非法")
            log.logger.error("验证码非法")
        except Exception as e:
            self.show_monitor(str(e))
            log.logger.error(e)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

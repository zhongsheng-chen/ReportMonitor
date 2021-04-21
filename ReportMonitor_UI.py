# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportMonitor_UI.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(564, 292)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("LELIEL.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.Label_news = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.Label_news.setFont(font)
        self.Label_news.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.Label_news.setTextFormat(QtCore.Qt.AutoText)
        self.Label_news.setAlignment(QtCore.Qt.AlignCenter)
        self.Label_news.setObjectName("Label_news")
        self.gridLayout.addWidget(self.Label_news, 7, 0, 1, 4)
        self.Label_yzm = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.Label_yzm.setFont(font)
        self.Label_yzm.setTextFormat(QtCore.Qt.AutoText)
        self.Label_yzm.setObjectName("Label_yzm")
        self.gridLayout.addWidget(self.Label_yzm, 2, 3, 1, 1)
        self.Label_stID = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.Label_stID.setFont(font)
        self.Label_stID.setTextFormat(QtCore.Qt.AutoText)
        self.Label_stID.setObjectName("Label_stID")
        self.gridLayout.addWidget(self.Label_stID, 2, 0, 1, 1)
        self.button_saveID = QtWidgets.QPushButton(self.centralwidget)
        self.button_saveID.setObjectName("button_saveID")
        self.gridLayout.addWidget(self.button_saveID, 3, 3, 1, 1)
        self.Line_password = QtWidgets.QLineEdit(self.centralwidget)
        self.Line_password.setEchoMode(QtWidgets.QLineEdit.PasswordEchoOnEdit)
        self.Line_password.setObjectName("Line_password")
        self.gridLayout.addWidget(self.Line_password, 3, 1, 1, 1)
        self.Line_stID = QtWidgets.QLineEdit(self.centralwidget)
        self.Line_stID.setObjectName("Line_stID")
        self.gridLayout.addWidget(self.Line_stID, 2, 1, 1, 1)
        self.Label_password = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.Label_password.setFont(font)
        self.Label_password.setTextFormat(QtCore.Qt.AutoText)
        self.Label_password.setObjectName("Label_password")
        self.gridLayout.addWidget(self.Label_password, 3, 0, 1, 1)
        self.pic_yzm = QtWidgets.QLabel(self.centralwidget)
        self.pic_yzm.setMinimumSize(QtCore.QSize(64, 28))
        self.pic_yzm.setMaximumSize(QtCore.QSize(64, 28))
        self.pic_yzm.setText("")
        self.pic_yzm.setObjectName("pic_yzm")
        self.gridLayout.addWidget(self.pic_yzm, 2, 7, 1, 1)
        self.button_linkWeb = QtWidgets.QPushButton(self.centralwidget)
        self.button_linkWeb.setObjectName("button_linkWeb")
        self.gridLayout.addWidget(self.button_linkWeb, 6, 0, 1, 1)
        self.ocr = QtWidgets.QCheckBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.ocr.setFont(font)
        self.ocr.setObjectName("ocr")
        self.gridLayout.addWidget(self.ocr, 3, 7, 1, 1)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 8, 0, 2, 8)
        self.Line_yzm = QtWidgets.QLineEdit(self.centralwidget)
        self.Line_yzm.setObjectName("Line_yzm")
        self.gridLayout.addWidget(self.Line_yzm, 2, 5, 1, 2)
        self.start = QtWidgets.QPushButton(self.centralwidget)
        self.start.setObjectName("start")
        self.gridLayout.addWidget(self.start, 3, 5, 1, 2)
        self.button_txt = QtWidgets.QPushButton(self.centralwidget)
        self.button_txt.setObjectName("button_txt")
        self.gridLayout.addWidget(self.button_txt, 6, 6, 1, 1)
        self.stop = QtWidgets.QPushButton(self.centralwidget)
        self.stop.setObjectName("stop")
        self.gridLayout.addWidget(self.stop, 6, 5, 1, 1)
        self.check_toast = QtWidgets.QCheckBox(self.centralwidget)
        self.check_toast.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.check_toast.setFont(font)
        self.check_toast.setChecked(True)
        self.check_toast.setObjectName("check_toast")
        self.gridLayout.addWidget(self.check_toast, 6, 7, 1, 1)
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setObjectName("textBrowser")
        self.gridLayout.addWidget(self.textBrowser, 7, 5, 1, 2)
        self.Label_linkStatus = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.Label_linkStatus.setFont(font)
        self.Label_linkStatus.setObjectName("Label_linkStatus")
        self.gridLayout.addWidget(self.Label_linkStatus, 6, 1, 1, 2)
        self.openWeb = QtWidgets.QLabel(self.centralwidget)
        self.openWeb.setAlignment(QtCore.Qt.AlignCenter)
        self.openWeb.setObjectName("openWeb")
        self.gridLayout.addWidget(self.openWeb, 6, 3, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 564, 23))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menu_RM = QtWidgets.QAction(MainWindow)
        self.menu_RM.setCheckable(True)
        self.menu_RM.setChecked(True)
        self.menu_RM.setObjectName("menu_RM")
        self.menu_L = QtWidgets.QAction(MainWindow)
        self.menu_L.setCheckable(True)
        self.menu_L.setObjectName("menu_L")
        self.menu.addAction(self.menu_RM)
        self.menu.addAction(self.menu_L)
        self.menubar.addAction(self.menu.menuAction())

        self.retranslateUi(MainWindow)
        self.Line_yzm.returnPressed.connect(MainWindow.yzmShow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.Line_stID, self.Line_password)
        MainWindow.setTabOrder(self.Line_password, self.Line_yzm)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "ReportMonitor"))
        self.Label_news.setText(_translate("MainWindow", "提示信息"))
        self.Label_yzm.setText(_translate("MainWindow", "验证码："))
        self.Label_stID.setText(_translate("MainWindow", "学号："))
        self.button_saveID.setText(_translate("MainWindow", "设为默认帐号"))
        self.Label_password.setText(_translate("MainWindow", "密码："))
        self.button_linkWeb.setText(_translate("MainWindow", "连接网站"))
        self.ocr.setText(_translate("MainWindow", "托管"))
        self.label.setText(_translate("MainWindow", "<html><head/><body><p>内部使用 </p></body></html>"))
        self.start.setText(_translate("MainWindow", "开始"))
        self.button_txt.setText(_translate("MainWindow", "屏蔽列表"))
        self.stop.setText(_translate("MainWindow", "停止"))
        self.check_toast.setText(_translate("MainWindow", "通知"))
        self.Label_linkStatus.setText(_translate("MainWindow", "未连接"))
        self.openWeb.setText(_translate("MainWindow", "<A href=\'http://yjsy.buct.edu.cn:8080/pyxx/login.aspx\'>教务网</a>"))
        self.menu.setTitle(_translate("MainWindow", "监测任务"))
        self.menu_RM.setText(_translate("MainWindow", "ReportMonitor"))
        self.menu_L.setText(_translate("MainWindow", "Lesson"))


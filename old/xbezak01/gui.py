# -*- coding: utf-8 -*-


from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(600, 400)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(600, 400))
        MainWindow.setMaximumSize(QtCore.QSize(600, 400))
        MainWindow.setStyleSheet("background-color: rgb(145,145,145);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setStyleSheet("")
        self.centralwidget.setObjectName("centralwidget")
        self.prehraj = QtWidgets.QPushButton(self.centralwidget)
        self.prehraj.setEnabled(True)
        self.prehraj.setGeometry(QtCore.QRect(550, 330, 32, 32))
        self.prehraj.setAutoFillBackground(False)
        self.prehraj.setStyleSheet("background-color: rgb(255,255,255);\n"
"font: 13pt \".SF NS Text\";")
        self.prehraj.setObjectName("prehraj")
        self.pridaj_slide = QtWidgets.QPushButton(self.centralwidget)
        self.pridaj_slide.setGeometry(QtCore.QRect(20, 10, 32, 32))
        self.pridaj_slide.setStyleSheet("background-color: rgb( 255,255,255);")
        self.pridaj_slide.setObjectName("pridaj_slide")
        self.myTextBox = QtWidgets.QLabel(self.centralwidget)
        self.myTextBox.setGeometry(QtCore.QRect(240, 20, 271, 16))
        self.myTextBox.setText("")
        self.myTextBox.setObjectName("myTextBox")
        self.nazov_suboru = QtWidgets.QLabel(self.centralwidget)
        self.nazov_suboru.setGeometry(QtCore.QRect(140, 20, 91, 16))
        self.nazov_suboru.setObjectName("nazov_suboru")
        self.zatvorit = QtWidgets.QPushButton(self.centralwidget)
        self.zatvorit.setGeometry(QtCore.QRect(20, 330, 32, 32))
        self.zatvorit.setStyleSheet("background-color: rgb(255,255,255);\n"
"font: 13pt \".SF NS Text\";")
        self.zatvorit.setObjectName("zatvorit")

        self.hudba = QtWidgets.QPushButton(self.centralwidget)
        self.hudba.setGeometry(QtCore.QRect(55, 10, 32, 32))
        self.hudba.setStyleSheet("background-color: rgb(255,255,255);\n"
"font: 13pt \".SF NS Text\";")
        self.hudba.setObjectName("hudba")

        self.zdielat = QtWidgets.QPushButton(self.centralwidget)
        self.zdielat.setGeometry(QtCore.QRect(515, 330, 32, 32))
        self.zdielat.setStyleSheet("background-color: rgb(255,255,255);\n"
"font: 13pt \".SF NS Text\";")
        self.zdielat.setObjectName("zdielat")

        self.napoveda = QtWidgets.QPushButton(self.centralwidget)
        self.napoveda.setGeometry(QtCore.QRect(550, 10, 32, 32))
        self.napoveda.setStyleSheet("background-color: rgb(255,255,255);\n"
"font: 13pt \".SF NS Text\";")
        self.napoveda.setObjectName("napoveda")  

        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(20, 60, 571, 251))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 600, 22))
        self.menubar.setObjectName("menubar")
        self.menuMenu = QtWidgets.QMenu(self.menubar)
        self.menuMenu.setObjectName("menuMenu")
        MainWindow.setMenuBar(self.menubar)
        self.actionNovy = QtWidgets.QAction(MainWindow)
        self.actionNovy.setObjectName("actionNovy")
        self.actionOtvorit = QtWidgets.QAction(MainWindow)
        self.actionOtvorit.setObjectName("actionOtvorit")
        self.actionUlozit = QtWidgets.QAction(MainWindow)
        self.actionUlozit.setObjectName("actionUlozit")
        self.actionUlozit_ako = QtWidgets.QAction(MainWindow)
        self.actionUlozit_ako.setObjectName("actionUlozit_ako")
        self.actionZavriet = QtWidgets.QAction(MainWindow)
        self.actionZavriet.setCheckable(True)
        self.actionZavriet.setObjectName("actionZavriet")
        self.menuMenu.addAction(self.actionNovy)
        self.menuMenu.addAction(self.actionOtvorit)
        self.menuMenu.addAction(self.actionUlozit)
        self.menuMenu.addAction(self.actionUlozit_ako)
        self.menuMenu.addAction(self.actionZavriet)
        self.menubar.addAction(self.menuMenu.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        #self.prehraj.setText(_translate("MainWindow", "Prehraj"))
        self.prehraj.setIcon(QtGui.QIcon("play.ico"))
        self.prehraj.setIconSize(QtCore.QSize(30,30))

        self.pridaj_slide.setIcon(QtGui.QIcon("plus.ico"))
        self.pridaj_slide.setIconSize(QtCore.QSize(30,30))

        #self.pridaj_slide.setText(_translate("MainWindow", "Pridaj nový slide"))
        self.nazov_suboru.setText(_translate("MainWindow", "Nazov suboru:"))
        
        self.zatvorit.setIcon(QtGui.QIcon("power.ico"))
        self.zatvorit.setIconSize(QtCore.QSize(30,30))

        self.hudba.setIcon(QtGui.QIcon("music.ico"))
        self.hudba.setIconSize(QtCore.QSize(30,30))

        self.zdielat.setIcon(QtGui.QIcon("share.ico"))
        self.zdielat.setIconSize(QtCore.QSize(30,30))

        self.napoveda.setIcon(QtGui.QIcon("help.png"))
        self.napoveda.setIconSize(QtCore.QSize(30,30))
        #self.zatvorit.setText(_translate("MainWindow", "Zatvoriť"))
        self.menuMenu.setTitle(_translate("MainWindow", "&Menu"))
        self.actionNovy.setText(_translate("MainWindow", "Nový..."))
        self.actionOtvorit.setText(_translate("MainWindow", "Otvorit..."))
        self.actionUlozit.setText(_translate("MainWindow", "Uložit..."))
        self.actionUlozit_ako.setText(_translate("MainWindow", "Uložit ako..."))
        self.actionZavriet.setText(_translate("MainWindow", "Zavriet"))


# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets

class Uprav_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 400)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.zatvorit = QtWidgets.QPushButton(self.centralwidget)
        self.zatvorit.setGeometry(QtCore.QRect(10, 330, 32, 32))
        self.zatvorit.setStyleSheet("background-color: rgb(255,255,255);\n"
"font: 13pt \".SF NS Text\";")
        self.zatvorit.setObjectName("zatvorit")
        self.ulozit = QtWidgets.QPushButton(self.centralwidget)
        self.ulozit.setGeometry(QtCore.QRect(550, 330, 32, 32))
        self.ulozit.setStyleSheet("background-color: rgb(255,255,255);\n"
"font: 13pt \".SF NS Text\";")
        self.ulozit.setObjectName("ulozit")
        self.vymazat = QtWidgets.QPushButton(self.centralwidget)
        self.vymazat.setGeometry(QtCore.QRect(50, 330, 32, 32))
        self.vymazat.setStyleSheet("background-color: rgb(255,255,255);\n"
"font: 13pt \".SF NS Text\";")
        self.vymazat.setObjectName("vymazat")
        self.vyber_obrazok = QtWidgets.QPushButton(self.centralwidget)
        self.vyber_obrazok.setGeometry(QtCore.QRect(10, 30, 131, 28))
        self.vyber_obrazok.setObjectName("vyber_obrazok")
        self.stiahnut_obrazok = QtWidgets.QPushButton(self.centralwidget)
        self.stiahnut_obrazok.setGeometry(QtCore.QRect(10, 120, 131, 28))
        self.stiahnut_obrazok.setObjectName("stiahnut_obrazok")
        self.url_zdroj = QtWidgets.QLineEdit(self.centralwidget)
        self.url_zdroj.setGeometry(QtCore.QRect(10, 80, 271, 32))
        self.url_zdroj.setObjectName("url_zdroj")
        self.label2 = QtWidgets.QLabel(self.centralwidget)
        self.label2.setGeometry(QtCore.QRect(100, 10, 500, 20))
        self.label2.setObjectName("label2")
        self.label3 = QtWidgets.QLabel(self.centralwidget)
        self.label3.setGeometry(QtCore.QRect(270, 330, 141, 32))
        self.label3.setObjectName("label")        
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(150, 30, 141, 32))
        self.label.setObjectName("label")
        self.upravit = QtWidgets.QPushButton(self.centralwidget)
        self.upravit.setGeometry(QtCore.QRect(85, 330, 32, 32))
        self.upravit.setStyleSheet("background-color: rgb(255,255,255);\n"
"font: 13pt \".SF NS Text\";")
        self.upravit.setObjectName("upravit")
        self.obrazok = QtWidgets.QLabel(self.centralwidget)
        self.obrazok.setGeometry(QtCore.QRect(310, 40, 271, 261))
        self.obrazok.setText("")
        self.obrazok.setObjectName("obrazok")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 600, 28))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        #self.zatvorit.setText(_translate("MainWindow", "Zatvoriť"))
        #self.ulozit.setText(_translate("MainWindow", " Uložiť"))
        #self.vymazat.setText(_translate("MainWindow", "Vymazať"))
        self.vyber_obrazok.setText(_translate("MainWindow", "Vybrať obrázok"))
        self.stiahnut_obrazok.setText(_translate("MainWindow", "Stiahnuť obrázok"))
        self.url_zdroj.setText(_translate("MainWindow", "zadajte url"))
        self.label.setText(_translate("MainWindow", "názov súboru"))
        self.label2.setText(_translate("MainWindow", "Pridajte obrázok (z pc/adresára) alebo zadajte url adresu"))

        #self.upravit.setText(_translate("MainWindow", "Upraviť"))

        self.zatvorit.setIcon(QtGui.QIcon("back.ico"))
        self.zatvorit.setIconSize(QtCore.QSize(30,30))
        self.vymazat.setIcon(QtGui.QIcon("delete.ico"))
        self.vymazat.setIconSize(QtCore.QSize(30,30))
        self.upravit.setIcon(QtGui.QIcon("edit.ico"))
        self.upravit.setIconSize(QtCore.QSize(30,30))
        self.ulozit.setIcon(QtGui.QIcon("save.ico"))
        self.ulozit.setIconSize(QtCore.QSize(30,30))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


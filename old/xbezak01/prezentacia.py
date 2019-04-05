#!/usr/bin/python3
# -*- coding: utf-8 -*-
# autori: xbezak01, xnovak1j, xblask02

import sys
import imghdr
import urllib.request
sys.path.insert(1,'/usr/local/lib/python3.5/site-packages/')
from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QSizePolicy, QWidgetItem, QFileDialog
from PyQt5.QtGui import QPainter, QColor, QBrush, QPixmap, QIcon
from uprav_slide import Uprav_MainWindow
from gui import Ui_MainWindow

# class represented custom exception
class ErrorWithCode(Exception):

	## Constructor
	# @param self pointer na objekt
	# @param code error code
	def __init__(self, code):
		self.code = code

	def __str__(self):
		return repr(self.code)

class customButton(QPushButton):
	def __init__(self, parent=None):
		super(QPushButton, self).__init__(parent)

	def setNumber(self, number):
		self.number = number

	def set_Icon(self, pixmap):
		self.pixmap = pixmap
		pixmap_icon = QIcon(pixmap)
		size = QtCore.QSize(self.size())
		self.setIcon(pixmap_icon)
		self.setIconSize(size)

class UpravWindow(QtWidgets.QMainWindow):

	pixmap = None

	def __init__(self, MyApp):
		super(UpravWindow, self).__init__(MyApp)
		self.parent = MyApp
		self.ui = Uprav_MainWindow()
		#self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
		self.ui.setupUi(self)
		self.setWindowTitle('Úprava položky')
		self.setStyleSheet("QMainWindow {background: rgb(160, 160, 160);}");
		self.ui.zatvorit.clicked.connect(self.zatvorit)
		self.ui.ulozit.clicked.connect(self.zatvorit)
		self.ui.vymazat.clicked.connect(self.vymazat)
		self.ui.vyber_obrazok.clicked.connect(self.vyber_obrazok)
		self.ui.stiahnut_obrazok.clicked.connect(self.stiahni_obrazok)

	def stiahni_obrazok(self):
		url = self.ui.url_zdroj.text()
		try :
			filename = url[url.rfind('/') + 1:]
			f = open(filename,'wb')
			f.write(urllib.request.urlopen(url).read())
			f.close()
			self.ui.label.setText(filename)		
		except ValueError:
			self.ui.url_zdroj.setText("Musis zadať platnú URL!!!")
			
		self.pixmap = QPixmap(filename)
		self.ui.obrazok.setScaledContents(True)
		self.ui.obrazok.setPixmap(self.pixmap)
		self.ui.obrazok.setAlignment(QtCore.Qt.AlignCenter)
		self.tlacitko.set_Icon(self.pixmap)

	def vyber_obrazok(self):   
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)

		if fileName:
			if imghdr.what(fileName):
				nazov_suboru = fileName[fileName.rfind('/') + 1:]
				self.ui.label.setText(nazov_suboru)		
				self.pixmap = QPixmap(fileName)
				self.ui.obrazok.setScaledContents(True)
				self.ui.obrazok.setPixmap(self.pixmap)
				self.ui.obrazok.setAlignment(QtCore.Qt.AlignCenter)
				self.tlacitko.set_Icon(self.pixmap)
			else :
				self.ui.label.setText("Nespravny format!")

	def zatvorit(self):
		self.parent.setVisible(True)
		self.close()

	def vymazat(self):
		self.parent.setVisible(True)
		self.parent.count -= 1
		self.tlacitko.hide()
		self.close()

	def pridatTlacitko(self, tlacitko):
		self.tlacitko = tlacitko
		try:
			self.pixmap = self.tlacitko.pixmap
			self.ui.obrazok.setScaledContents(True)
			self.ui.obrazok.setPixmap(self.pixmap)
			self.ui.obrazok.setAlignment(QtCore.Qt.AlignCenter)			
		except AttributeError:
			pass

	def pridajTextSlide(self):

		self.ui.label3.setText("Slide č. " + str(self.tlacitko.number))
class MyApp(QtWidgets.QMainWindow):

	pridat_slide = False

	def __init__(self):
		super(MyApp, self).__init__()
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.setWindowTitle('Nástroj na tvorbu prezentácie')
		self.setStyleSheet("QMainWindow {background: rgb(0, 225, 255);}");
		self.ui.actionZavriet.triggered.connect(self.close)
		self.ui.actionOtvorit.triggered.connect(self.otvorPrezentaciu)
		self.ui.zatvorit.clicked.connect(self.close)
		self.ui.pridaj_slide.clicked.connect(self.pridaj_slide)
		self.count = 0

	def otvorPrezentaciu(self):
	    nazov_cesty = QtWidgets.QFileDialog.getOpenFileName(self, 'OpenFile')
	    nazov_cesty = nazov_cesty[0]
	    nazov_suboru = nazov_cesty[nazov_cesty.rfind('/') + 1:]
	    self.ui.myTextBox.setText(nazov_suboru)

	def pridaj_slide(self):

		self.pridat_slide = True
		self.repaint()
		if not self.count :
			positions = [(i,j) for i in range(3) for j in range(3)]
			for count, position in enumerate(positions, 1):
				self.count = 1
				button = customButton()
				button.setNumber(count)
				policy_typ = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
				button.setSizePolicy(policy_typ)
				if count != 1:
					button.hide()
				self.ui.gridLayout.addWidget(button, *position)
				button.clicked.connect(lambda: self.pridaj_slide2(button))
		else:
			if self.count != 9:	
				button_item = self.ui.gridLayout.itemAt(self.count)
				button_item_previous = self.ui.gridLayout.itemAt(self.count - 1)
				self.count += 1
				button_widget = QWidgetItem.widget(button_item)
				button_widget.show()

	def pridaj_slide2(self, button):
		stlacene_tlacitko = self.sender()
		window = UpravWindow(self)
		window.pridatTlacitko(stlacene_tlacitko)
		window.pridajTextSlide()
		window.show()
		self.setVisible(False)

if __name__ == "__main__":
	try:
		app = QtWidgets.QApplication(sys.argv)
		window = MyApp()
		window.show()
		sys.exit(app.exec_())

	except ErrorWithCode as e:
		sys.stderr.write("Chyba!!!")
		sys.exit(99)
	except KeyboardInterrupt:
		window.close()
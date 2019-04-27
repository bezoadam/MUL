from PyQt5 import QtWidgets, QtGui


class JumpSlider(QtWidgets.QSlider):
	'''Custom Slider class for click->jump behaviour

	Arguments:

		QtWidgets {QSlider} -- Base class
	'''

	def __init__(self, *args):
		QtWidgets.QSlider.__init__(self, *args)

	def mousePressEvent(self, e):
		'''Handle mouse press event

		Arguments:

			e {QtGui.QMouseEvent} -- event
		'''
		self.handleEvent(e)

	def mouseMoveEvent(self, e):
		'''Handle mouse move event

		Arguments:

			e {QtGui.QMouseEvent} -- event
		'''
		self.handleEvent(e)

	def mouseReleaseEvent(self, e):
		'''Handle mouse release event

		Arguments:

			e {QtGui.QMouseEvent} -- event
		'''
		self.handleEvent(e)

	def handleEvent(self, e):
		'''Base function for handling occured mouse events

		Arguments:

			e {QtGui.QMouseEvent} -- event
		'''
		self.setSliderPosition(int(self.minimum() + ((self.maximum() - self.minimum()) * e.x()) / float(self.width())))

	def handleValueChanged(self, x):
		'''Handler for slider value changed

		Arguments:

			x {int} -- New value of slider
		'''
		raise NotImplementedError()

	def setup(self, mainWindow):
		'''Setup function for connecting parent widgets with child widgets

		Arguments:

			mainWindow {QtWidgets.QMainWindow} -- Main window of whole application
		'''
		self.mainWindow = mainWindow
		self.valueChanged.connect(self.handleValueChanged)


class VolumeSlider(JumpSlider):
	'''VolumeSlider class for customized slider handling volume of player

	Arguments:

		JumpSlider {JumpSlider} -- Base class of slider
	'''
	def __init__(self, *args):
		super(JumpSlider, self).__init__(*args)

	def handleValueChanged(self, x):
		'''Handler for slider value changed

		Arguments:

			x {int} -- New value of slider
		'''
		self.mainWindow.updateVolumeFromSlider()


class TimeSlider(JumpSlider):
	'''TimeSlider class for customized slider handling current time of played song

	Arguments:

		JumpSlider {JumpSlider} -- Base class of slider
	'''
	def __init__(self, *args):
		super(JumpSlider, self).__init__(*args)

	def handleValueChanged(self, x):
		'''Handler for slider value changed

		Arguments:

			x {int} -- New value of slider
		'''
		self.mainWindow.updateTimeFromSlider()

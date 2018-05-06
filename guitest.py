import sys

from PyQt5 import QtWidgets

class GUI(QtWidgets.QWidget):
	def __init__(self, parent=None):
		QtWidgets.QWidget.__init__(self, parent)
		self.setWindowTitle("3D Reconstruction")
		self.resize(1000, 600)

if __name__ == '__main__':
	# For the widget we need to create an application object
	application = QtWidgets.QApplication(sys.argv)

	myGUI = GUI()
	myGUI.show()


	# When user closes the Widget
	sys.exit(application.exec_())
from PyQt5 import QtWidgets

from mp3player.widgets import MP3Player


def main():
	app = QtWidgets.QApplication([])
	player = MP3Player()
	player.show()
	return app.exec()


if __name__ == "__main__":
	main()
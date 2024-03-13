import sys

from UI import MapInterface
from PyQt6.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet("QPushButton{font-size: 26pt;}")
    window = MapInterface()
    window.show()

    app.exec()


if __name__ == "__main__":
    main()

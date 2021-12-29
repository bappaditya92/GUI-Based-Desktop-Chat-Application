import sys
from PyQt5.QtWidgets import QApplication, QWidget
import Communicator as comm

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = comm.Communicator()
    sys.exit(app.exec_())

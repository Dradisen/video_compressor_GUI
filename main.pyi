from PyQt5 import QtWidgets
import sys

from src.components.Compressor import Compressor
 
app = QtWidgets.QApplication([])
application = Compressor()
application.show()

sys.exit(app.exec())
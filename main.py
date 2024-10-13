# main.py

import sys
from PyQt5.QtWidgets import QApplication
from gui import EvolutionSimulatorGUI

def main():
    app = QApplication(sys.argv)
    gui = EvolutionSimulatorGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()








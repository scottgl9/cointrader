#!/usr/bin/python
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import random

class mainWindow(QtGui.QTabWidget):
    def __init__(self, parent = None):
        super(mainWindow, self).__init__(parent)
        self.tab_names = []
        self.tabs = {}
        self.figures = {}
        self.canvases = {}

        self.create_tab("tab1")
        self.plot_tab("tab1")
        self.create_tab("tab2")
        self.plot_tab("tab2")

    def create_tab(self, name):
        self.tab_names.append(name)
        self.tabs[name] = QtGui.QWidget()
        self.addTab(self.tabs[name], name)
        self.figures[name] = plt.figure(figsize=(10,5))
        self.canvases[name] = FigureCanvas(self.figures[name])
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.canvases[name])
        self.tabs[name].setLayout(layout)

    def plot_tab(self, name, data):
        ax = self.figures[name].add_subplot(111)
        ax.plot(data, '*-')
        self.canvases[name].draw()

def main():
    app = QtGui.QApplication(sys.argv)
    main = mainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

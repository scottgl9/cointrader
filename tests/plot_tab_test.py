#!/usr/bin/python
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import random

class TabType:
    def __init__(self, name):
        self.name = name
        self.tab = None
        self.figure = None
        self.canvas = None

class mainWindow(QtGui.QTabWidget):
    def __init__(self, parent = None):
        super(mainWindow, self).__init__(parent)
        self.tabs = {}

        self.create_tab("tab1")
        self.plot_tab("tab1")
        self.create_tab("tab2")
        self.plot_tab("tab2")

    def create_tab(self, name):
        tabtype = TabType(name)
        tabtype.tab = QtGui.QWidget()
        self.addTab(tabtype.tab, name)
        tabtype.figure = plt.figure(figsize=(10,5))
        tabtype.canvas = FigureCanvas(tabtype.figure)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(tabtype.canvas)
        tabtype.tab.setLayout(layout)
        self.tabs[name] = tabtype

    def plot_tab(self, name, data=None):
        data = [random.random() for i in range(10)]
        ax = self.tabs[name].figure.add_subplot(111)
        ax.plot(data, '*-')
        self.tabs[name].canvas.draw()

def main():
    app = QtGui.QApplication(sys.argv)
    main = mainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

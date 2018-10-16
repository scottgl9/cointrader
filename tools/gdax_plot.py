import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QSizePolicy, QWidget, QComboBox
from PyQt5.QtCore import QRect

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from trader.gdax.public_client import PublicClient
from trader.myhelpers import *
from trader.indicator.EMA import EMA
from trader.indicator.VWAP import VWAP
from trader.indicator.test.QUAD import QUAD

class App(QMainWindow):

    def __init__(self):
        super(App, self).__init__()
        self.left = 0
        self.top = 0
        self.title = 'PyQt5 matplotlib example - pythonspot.com'
        self.width = 1900
        self.height = 1000
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.m = PlotCanvas(self, width=20, height=8)
        self.m.move(0, 0)

        #button = QPushButton('PyQt5 button', self)
        #button.setToolTip('This s an example button')
        #button.move(500, 0)
        #button.resize(140, 100)

        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)

        # Create combobox and add items.
        self.comboBox = QComboBox(centralWidget)
        self.comboBox.setGeometry(QRect(40, 40, 491, 31))
        self.comboBox.setObjectName(("comboBox"))

        pc = PublicClient()
        products = pc.get_products()
        for product in products:
            if 'id' in product and 'EUR' not in product['id'] and 'GBP' not in product['id']:
                self.comboBox.addItem(product['id'])

        self.comboBox.activated.connect(self.changeTicker)

        self.show()

    def changeTicker(self, index):
        print(self.comboBox.itemText(index))
        self.m.ticker = self.comboBox.itemText(index)
        self.m.plot()
        #print(self.comboBox.itemData(index))


class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.ticker = 'BTC-USD'
        self.plot()

    def plot_emas_product(self, plt, klines, product):
        # klines = retrieve_klines_last_hour(product, hours=4)
        # klines = retrieve_klines_24hrs(product)
        vwap = VWAP(60)
        # macd = MACD()
        # macd_signal = []
        # for kline in klines:
        #    macd.update(float(kline[3]))
        #    #macd.update()
        #    macd_signal.append(float(macd.signal.result))
        price_min = []
        price_max = []
        timestamps = []
        prices = []
        for kline in klines:
            prices.append(float(kline[3]))
            prices.append(float(kline[4]))
        quad_maxes = []
        quad_x = []
        quad_y = []
        price_min.append(float(klines[0][1]))
        price_max.append(float(klines[0][2]))
        quad = QUAD()
        ema_quad = EMA(9)

        initial_time = float(klines[0][0])

        for i in range(1, len(klines) - 1):
            ts = (float(klines[i][0]) - initial_time) / (60.0)
            price_min.append(float(klines[i][1]))
            price_max.append(float(klines[i][2]))
            quad.update(ts, ema_quad.update(klines[i][3]))
            if 1:  # try:
                A, B, C = quad.compute()

                if C != 0:  # and C > min(prices) and C < max(prices):
                    if 1:  # C > min(prices) and C < max(prices):
                        timestamp_max = initial_time + 60.0 * (-B / (2 * A))
                        timestamp_current = initial_time + i * 60.0
                        print(A, B, C, timestamp_current, prices[i], timestamp_max)
                        # ts = ts + 2.0
                        y = A * (ts * ts) + (B * ts) + C
                        # if y > min(prices) and y < max(prices):
                        quad_x.append(ts)
                        quad_y.append(ema_quad.update(y))
                        quad_maxes.append(C)
            # except:
            #    pass
        print(quad_x)

        price_max_value = max(price_max)
        diff = price_max_value - min(price_min)
        level1 = price_max_value - 0.236 * diff
        level2 = price_max_value - 0.382 * diff
        level3 = price_max_value - 0.618 * diff

        plt.axhspan(level1, min(price_min), alpha=0.4, color='lightsalmon')
        plt.axhspan(level2, level1, alpha=0.5, color='palegoldenrod')
        plt.axhspan(level3, level2, alpha=0.5, color='palegreen')
        plt.axhspan(price_max_value, level3, alpha=0.5, color='powderblue')

        vwap0 = []
        for kline in klines:
            vwap.kline_update(low=kline[1], high=kline[2], close=kline[4], volume=kline[5])
            vwap0.append(vwap.result)
        ema0 = compute_ema_dict_from_klines(klines, 4)
        ema1 = compute_ema_dict_from_klines(klines, 12)
        ema2 = compute_ema_dict_from_klines(klines, 26)
        # compute_ema_crossover_from_klines(ema1, ema2)
        prices = prices_from_kline_data(klines)
        symprice, = plt.plot(prices, label=product)  # , color='black')
        sma12, = plt.plot(compute_smma_from_kline_prices(prices, 12), label='SMMA12')
        ema4, = plt.plot(ema0["y"], label='EMA4')
        #quad0, = plt.plot(quad_x, quad_y, label='QUAD')
        plt.legend(handles=[symprice, ema4, sma12])

    def plot(self):
        self.figure.clear()
        klines = retrieve_klines_24hrs(self.ticker)#retrieve_klines_last_hour(self.ticker, hours=5)
        ax = self.figure.add_subplot(111)
        self.plot_emas_product(ax, klines, self.ticker)
        # ax = self.figure.add_subplot(111)
        #prices1 = np.array(prices_from_kline_data(klines))
        #ax.plot(prices1, 'r-')
        #ax.set_title('GDAX plot')
        self.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
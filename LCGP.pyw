# pip install PyQt5
# pip install pyqt5-tools (optional. for the Designer)
# pip install matplotlib
# -*- encoding: utf-8 -*-


import sys

# PyQt5 imports
import PyQt5
from PyQt5 import QtGui, uic

import sip  # must be after PyQt5.QtGui import

import PyQt5.QtWidgets
from PyQt5.QtWidgets import QPushButton, QTextEdit, QApplication, \
    QGridLayout, QHBoxLayout, QLabel, QMainWindow, QMessageBox, QVBoxLayout, QWidget

import PyQt5.QtGui
from PyQt5.QtGui import QColor

# Matplotlib imports
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

''' UNUSED IMPORT STATEMENTS. MAY BE USEFUL IN THE FUTURE

import PyQt5
from PyQt5.QtCore import pyqtSlot, QSize
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QMainWindow, QAction, QVBoxLayout, QHBoxLayout, QLabel, \
    QLineEdit, QSpacerItem, QSizePolicy, QPushButton

from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
                             QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                             QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
                             QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
                             QVBoxLayout, QWidget)
from PyQt5.QtCore import QFileInfo, QRegExp, QSize, Qt
from PyQt5.QtGui import QIcon, QImage, QPalette, QPixmap, QLinearGradient, QColor, QBrush
import PyQt5.QtGui
from PyQt5.QtWidgets import (QAbstractItemView, QAction, QActionGroup,
                             QApplication, QComboBox, QFileDialog, QFrame, QGridLayout, QGroupBox,
                             QHBoxLayout, QHeaderView, QItemDelegate, QLabel, QMainWindow,
                             QMessageBox, QRadioButton, QSizePolicy, QSpinBox, QStyle,
                             QStyleFactory, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from matplotlib.figure import Figure
# print(QStyleFactory.keys()) # get installed styles
'''

"""
Put the MainWindow.ui file in the same directory as the script.
"""


class MainWindow(QMainWindow):
    """
    THis is the main window of the program.
    Warning: do not change class name. it will break things. Sorry I couldn't do it otherwise...
    """
    points = []  # points the user has entered
    line = ()  # tuple a,b of the line
    ##
    ## TEXT VARIABLES
    ##
    x_label = "x axis"
    y_label = "y axis"

    def __init__(self):
        super(MainWindow, self).__init__()
        # POINT SIZE IS 9 FOR ALL WIDGETS IN THIS CLASS
        self.window = uic.loadUi("{}.ui".format(__class__.__name__))  # load the Designer UI

        self.window.setMinimumSize(900, 650)  # set min size to still show axis labels

        # compile the ui file with this
        # with open("ccc.py","w") as f:
        #    uic.compileUi("MainWindow.ui",f)

        self.figure = plt.figure()  #
        self.canvas = FigureCanvas(self.figure)  # init graph widget
        self.toolbar = NavigationToolbar(self.canvas, self.window.graph_view)  # init toolbar

        self.init_graph()  # *** SET DEFAULTS FOR GRAPH ***
        self.init_colors()  # comment that out if you don't care about the colors being the same

        self.window.point_editor.clicked.connect(lambda: self.open_point_dialog())

        self.window.help.clicked.connect(self.view_help)
        self.window.calculate.clicked.connect(lambda: self.plot(self.points, plot_line=True))  # bind calculate button to function
        self.window.reset.clicked.connect(lambda: self.reset_points())  # bind calculate button to function
        self.window.add_point.clicked.connect(self.add_point)  # bind add point button to function
        self.window.delete_point.clicked.connect(self.delete_point)
        # QLineEdit will emit signal returnPressed() when user presses enter key while in it
        self.window.add_point_field.returnPressed.connect(self.add_point)  # assign signal to the add_point button

        self.layout = QVBoxLayout(self.window.graph_view)  # create a layout INSIDE the QWidget
        self.layout.addWidget(self.toolbar)  # place the toolbar in the layout
        self.layout.addWidget(self.canvas)  # place the graph in the layout

    def init_graph(self):
        """
        This method recreates the graph/plot. call it to clear out the graph
        """
        self.figure.clear()
        ax = self.figure.add_subplot(111)  # create axis
        ax.ticklabel_format(useOffset=False, style="plain")  # disable scientific notation on axis
        ax.set_facecolor("#ffffff")  # set background color on plot

        # adjust borders of graph
        top = 0.966
        bottom = 0.106
        left = 0.121
        right = 0.974
        hspace = 0.2
        wspace = 0.2
        plt.subplots_adjust(left=left, bottom=bottom, right=right, top=top, wspace=wspace, hspace=hspace)

        # axis
        plt.xlabel(self.x_label)
        plt.ylabel(self.y_label)
        # plt.axis("equal") this keep both axis the same. sucks if u only wanna zoom in one axis

        # other stuff
        plt.grid(True, color="lightgray")
        self.set_function_label()

        # finally draw that piece of shit
        self.canvas.draw()  # optional? definitely not.

    def init_colors(self):
        """
        This method is totally optional. It initializes the color of all widgets.
        """
        # [0] = bg color / [1] = text color
        accent_0 = ["#f0f0f0", "#000000"]  # light gray, black
        accent_1 = ["#ffffff", "#000000"]  # white, black

        self.figure.patch.set_facecolor(accent_0[0])  # set color outside plot in HEX / value 0-1 (r,g,b)
        # here comes the graph color that u must change in the init_graph() method

        # Main window background
        palette = QtGui.QPalette()
        palette.setColor(self.backgroundRole(), QColor(accent_0[0]))
        self.window.setPalette(palette)

        # All buttons gotta be the same !!!
        button_str = "QPushButton {{ background-color : {}; color : {}; }}".format(accent_1[0], accent_1[1])
        '''self.window.calculate.setStyleSheet(button_str)
        self.window.reset.setStyleSheet(button_str)
        self.window.add_point.setStyleSheet(button_str)
        self.window.delete_point.setStyleSheet(button_str)
        self.window.point_editor.setStyleSheet(button_str)'''  # this sucks because it removes the os style

        # lists / line widgets
        list_str = "QLineEdit {{ background-color : {}; color : {}; }}".format(accent_0[0], accent_0[1])
        self.window.function.setStyleSheet(list_str)
        self.window.add_point_field.setStyleSheet(button_str)  # this one gotta be different
        self.window.points_list_view.setStyleSheet(list_str)  # this little fucker doesnt seem to work

        # labels
        label_str = "QLabel {{ background-color : {}; color : {}; }}".format(accent_0[0], accent_0[1])
        self.window.points_coords_label.setStyleSheet(label_str)
        self.window.graph_label.setStyleSheet(label_str)
        self.window.fx_label.setStyleSheet(label_str)

        # the one and only checkbox :(
        self.window.autocalculate.setStyleSheet("QCheckBox {{ background-color : {}; color : {}; }}".format(accent_0[0], accent_0[1]))

    def add_point(self):
        """
        Add point function. bound to button add point
        """
        add_point_value = self.window.add_point_field.text()  # read text in the box (type:str)
        add_point_value = add_point_value.split(",")  # split in list (type:list)

        if len(add_point_value) is 2:  # check if value is correct format

            x = convert_str_to_int_float(add_point_value[0])  # get x coord and transform it
            y = convert_str_to_int_float(add_point_value[1])  # get y coord and transform it
            if y is None:
                self.show_status_bar_message("Invalid Format. '{}' is not a valid number".format(y))
            if x is None:
                self.show_status_bar_message("Invalid Format. '{}' is not a valid number".format(x))

            """
            MOST IMPORTANT PART OF PROGRAM
            """
            if (x, y) not in self.points:  # if point is not already added
                if type(x) is int or type(x) is float:  # check if x in int or float
                    if type(y) is int or type(y) is float:  # check if y is int/float
                        self.points.append((x, y))
                        self.update_list()  # update list
                        self.plot(self.points)  # put point on graph
                        self.show_status_bar_message("Point ({},{}) added!".format(x, y))
                        if self.window.autocalculate.isChecked():  # if auto-calculate is checked...
                            self.plot(self.points, plot_line=True)  # calculate the line
                        self.window.add_point_field.setText("")  # reset text field
            else:
                self.show_status_bar_message("Point already exists!")
                self.window.add_point_field.setText("")  # reset text field
        else:
            self.show_status_bar_message("Invalid Format. Example input: 4.5,-6")

    def plot(self, points: list, plot_line=False):
        """
        :param points: if line=False, then the list of points to plot
        :param plot_line: True/False depends if u wanna plot line or points
        """
        if plot_line:
            if len(self.points) >= 2:  # setting mode to calculate n draw line
                try:  # handle this quick and dirty
                    self.line.pop(0).remove()  # remove the line if it exists
                except ValueError as e:
                    print_exception(e)
                except AttributeError as e:
                    print_exception(e)

                # *** CALCULATE LINE ***
                def f(x):  # set up function for line
                    return a * x + b

                numPoints = len(points)  # get the amount of points

                # get x coords
                xcoords = []
                for x in range(numPoints):
                    xcoords.append(points[x][0])

                minXpoint = min(xcoords)
                maxXpoint = max(xcoords)

                self.line = self.calculate_line(self.points)  # get a, b

                if self.line is not None:  # if line can be drawn...
                    a, b = self.line[0], self.line[1]

                    axes = plt.axis()  # save axes without line
                    # x1 x2   y1 y2
                    offset = 0
                    self.line = plt.plot([minXpoint - offset, maxXpoint + offset],
                                         [f(minXpoint - offset), f(maxXpoint + offset)], color="red",
                                         linestyle='-', linewidth=1)

                    # plt.xlim([axes[0], axes[1]])  # apply previous axis
                    # plt.ylim([axes[2], axes[3]])

                    if not self.window.autocalculate.isChecked():
                        self.show_status_bar_message("Line successfully drawn !")
                    self.set_function_label(a, b)
            else:
                if not self.window.autocalculate.isChecked():
                    self.show_status_bar_message("Not enough points to draw line. Minimum 2 required")
        else:  # setting mode to plot points
            for i in self.points:
                # todo: fix: this re-plots points that are already plotted
                plt.scatter(i[0], i[1], color="black")  # scatter > plot cuz u can change color n shit
        self.canvas.draw()

    def update_list(self):
        """
        this method updates the widget that lists points on the left
        """
        self.window.points_list_view.clear()  # clear list first
        self.window.points_list_view.addItems([str(x) for x in self.points])  # add items back

    def delete_point(self):
        """
        method bound to delete point button
        """
        itemPos = self.window.points_list_view.currentRow()  # get current row of selected item
        if itemPos is not -1:  # -1 if nothing is selected in the widget
            itemValue = self.points[itemPos]
            del self.points[itemPos]  # delete point from list
            # todo fix: find better method instead of redrawing everything
            self.init_graph()  # clear graph
            self.plot(self.points)  # plot the points without the removed one
            if self.window.autocalculate.isChecked():  # if auto-calculate is checked...
                self.plot(self.points, plot_line=True)  # draw line
            self.update_list()
            self.show_status_bar_message("Deleted point {}".format(itemValue))
        else:
            self.show_status_bar_message("Please select a point to delete.")

    def reset_points(self):
        """
        Button reset function / resets everything back to default
        """
        msg = "Are you sure you want to remove all points?"
        reply = QMessageBox.question(self, 'Warning', msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.No:
            pass
        else:
            self.points = []  # reset placed points
            self.init_graph()  # put defaults for graph
            self.update_list()  # update list with nothing
            self.show_status_bar_message("Reset successful !")

    def set_function_label(self, a="a", b="b"):
        """
        Displays the a,b of the function on the function label
        :param a:  a part of ax+b
        :param b:  b part of ax+b
        """
        self.window.function.setText("{} x + {}".format(a, b))

    def show_status_bar_message(self, message):
        """
        Shows a message to the status bar
        """
        time = 5000  # time in ms -> how long will the text be shown in status bar
        self.window.statusbar.showMessage(message, time)

    def calculate_line(self, points):
        """
        this method calculates the line that passes closer to all points
        I am aware that using numpy it would be easier to do matrix multiplications, etc... but
        I had already done it before I knew that so why redo it?
        :param points: list of points
        :return: a,b part of line. None if not possible
        """
        numPoints = len(points)

        # Looking for a,b in ax+b
        # [a1, b1] * [a] = [g]
        # [c1, d1]   [b]   [h]
        #
        # [g] = horizontal * solvector
        # [h]

        # [x1, 1]
        # [x2, 1]
        # [x3, 1]
        matrix_A = []
        for x in range(numPoints):
            matrix_A.append([points[x][0], 1])
        # print("Verticale matrix: ", matrix_A)

        # [x1,x2,x3]
        # [ 1, 1, 1]
        matrix_AexpT = [[], []]
        for x in range(numPoints):
            matrix_AexpT[0].append(points[x][0])  # append x coords
            matrix_AexpT[1].append(1)  # append the 1s
        # print("Horizonal matrix: ", matrix_AexpT)

        # a1 = x1*x1+x2*x2+x3*x3...
        a1 = 0
        for x in matrix_AexpT[0]:
            a1 = a1 + x ** 2

        # b1 = x1*1+x2*1+x3*1...
        b1 = 0
        for x in matrix_AexpT[0]:
            b1 = b1 + x

        # c1 = 1*x1+1*x2+1*x3...
        c1 = 0
        for x in matrix_AexpT[0]:
            c1 = c1 + x

        # d1 = 1*1+1*1+1*1...
        d1 = 0
        for x in matrix_AexpT[1]:
            d1 = d1 + x

        # [a1, b1]
        # [c1, d1]
        resultM = [[a1, b1], [c1, d1]]

        solvector = []  # y coordinates of points
        for x in points:
            solvector.append(x[1])

        # g = y1*x1+y2*x2+y3*x3...
        g = 0
        for x in range(numPoints):
            g = g + solvector[x] * matrix_AexpT[0][x]

        # h = y1*1+y2*1+y3*1...
        h = 0
        for x in range(numPoints):
            h = h + solvector[x] * matrix_AexpT[1][x]

        try:
            a = (g * d1 - b1 * h) / (d1 * a1 - b1 * c1)
            b = h / d1 - (c1 / d1 * a)
            return a, b
        except ZeroDivisionError as e:
            print_exception(e)
            self.show_status_bar_message("Cannot draw a vertical line.")
            return None  # if cannot draw line return none

    def view_help(self):
        """
        bound to Help button. opens the help window
        """
        self.help = HelpWindow()  # init help window
        self.help.show()

    def open_point_dialog(self):
        """
        bound to the point editor button
        still quite glitchy but useful if you wanna mess around and add 5k points very fast lol
        """
        self.save = PointWindow(self.points)  # pass in the current list of points
        self.save.show()


class HelpWindow(QWidget):  # QWidget necessary to use grid layout
    """
    This is the Help window.
    """

    def __init__(self):
        super(HelpWindow, self).__init__()
        self.setMinimumSize(800, 500)
        self.setMaximumSize(800, 500)
        self.setWindowTitle("Help")
        # self.setWindowIcon(QtGui.QIcon("python.png"))

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setFontPointSize(10)
        self.text.setText("Jon Defilla\nVersion 1.0 (03 aug 2018)\nGNU General Public License\n\n"
                          "Help:\nThis program draws and returns the function of a line that passes closest to all given points.\n"
                          "To add points, input them in the 'Format: x,y' box and press the 'Enter' key or the 'Add point' button. "
                          "They will appear in the plot and in the box on the left, which lists all existing points.\n"
                          "To calculate the line and get its function click the 'Calculate line' button or check "
                          "the 'auto-calculate' checkbox to calculate it automatically each time you add or remove a point.\n"
                          "Once the line is calculated, its function will appear in a text box. The text in this box is "
                          "selectable and copyable.\nTo delete a point, select it in the box on the left and press delete point.\n"
                          "To reset everything back to default press the reset button.\n"
                          "The point editor is a way to add/remove lots of points quickly. Click the 'Point editor' button to open it. "
                          "In the point editor window will be listed all currently placed points or none if there aren't any. To add "
                          "points simply input them like you would otherwise (x,y). Make sure to only keep one point per line. The "
                          "parenthesis are optional.")
        self.grid = QGridLayout(self)
        self.setLayout(self.grid)

        self.okButton = QPushButton("OK")
        self.okButton.clicked.connect(self.close)

        self.grid.addWidget(self.text, 1, 0)

        self.horizontal_box = QHBoxLayout()
        self.horizontal_box.addStretch(1)

        self.horizontal_box.addWidget(self.okButton)

        self.grid.addLayout(self.horizontal_box, 2, 0)


class PointWindow(HelpWindow):
    """
    This is the point editor window. It inherits from HelpWindow because they're similar
    """

    def __init__(self, points):
        super(PointWindow, self).__init__()
        self.setWindowTitle("Point Editor")
        self.setMinimumSize(800, 500)
        self.setMaximumSize(800, 500)

        sip.delete(self.okButton)  # delete ok button so we can recreate it later

        self.label = QLabel("Press OK to save the points or cancel to cancel. One point per line. The parenthesis are optional. "
                            "Example input: \n(5,6\n-9.3,10.3")
        self.label.setStyleSheet('QLabel { font-size: 9pt }')
        self.grid.addWidget(self.label, 0, 0)

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.setStyleSheet('QPushButton { font-size: 9pt }')
        self.cancelButton.clicked.connect(self.close)
        self.horizontal_box.addWidget(self.cancelButton)

        self.okButton = QPushButton("OK")
        self.okButton.setStyleSheet('QPushButton { font-size: 9pt }')
        self.okButton.clicked.connect(self.save)
        self.horizontal_box.addWidget(self.okButton)

        self.text.setReadOnly(False)

        self.first_line = ""
        self.points_str = "".join(str(point) + "\n" for point in points)

        self.final_string = self.first_line + self.points_str
        self.text.setText(self.final_string)

    def save(self):
        """
        bound to the OK button on the point editor
        I know its very messy but it somewhat works
        """
        MainWindow.points = []  # reset points
        text_in_box = self.text.toPlainText().split("\n")
        for point in text_in_box:
            if point == "":
                continue  # skip empty lines

            point = point.replace("(", "").replace(")", "")
            point = point.split(",")

            try:
                x = convert_str_to_int_float(point[0])
                y = convert_str_to_int_float(point[1])
                if x is None or y is None:
                    continue  # maybe put pop up message or something...

                MainWindow.points.append((x, y))

            except IndexError as e:
                print_exception(e)

        # very messy but it works alright
        MainWindow.update_list(main)  # self is main. we just pass the instance instead
        MainWindow.init_graph(main)  # reset the graph then plot points
        MainWindow.plot(main, MainWindow.points)  # same here. main = Mainwindow.self
        MainWindow.show_status_bar_message(main, "Points added !")
        if main.window.autocalculate.isChecked():
            MainWindow.plot(main, MainWindow.points, plot_line=True)

        self.close()


def print_exception(exception):
    if debug:
        print(exception)


def convert_str_to_int_float(string):
    """
    :param string: string you wanna convert to int/float
    :return: type int/float of input. None if not possible
    """
    try:  # to convert x to int, then to float
        string = int(string)
    except ValueError as e:
        print_exception(e)
        try:
            string = float(string)
        except ValueError as e:
            print_exception(e)
            return None
    return string


def exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


debug = True

if __name__ == '__main__':
    if debug:
        sys._excepthook = sys.excepthook
        sys.excepthook = exception_hook

    app = QApplication(sys.argv)  # can put [] instead of sys.argv

    # DO NOT change the instance name. It will fuck up the point editor.
    main = MainWindow()
    main.window.show()

    sys.exit(app.exec_())

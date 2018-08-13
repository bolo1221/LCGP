# Copyright (C) 2018 Jon Defilla
#
# LCGP is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# LCGP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LCGP.  If not, see <http://www.gnu.org/licenses/>.
#
# ONLY TESTED ON PYTHON 3.6.5
#
# pip install PyQt5
# pip install pyqt5-tools (optional, for the PyQt Designer)
# pip install matplotlib
# -*- encoding: utf-8 -*-


import sys
import os

# PyQt5 imports
from PyQt5 import QtGui, uic

import sip  # must be after PyQt5.QtGui import

from PyQt5.QtWidgets import QPushButton, QTextEdit, QApplication, \
    QGridLayout, QHBoxLayout, QLabel, QMainWindow, QMessageBox, QVBoxLayout, QWidget

from PyQt5.QtGui import QColor

# Matplotlib imports // todo: switch to GPU accelerated plotting library
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

''' # UNUSED IMPORT STATEMENTS. MAY BE USEFUL IN THE FUTURE

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


# compile the ui file with this.
# with open("compiledUI.py", "w") as f:
#    uic.compileUi("MainWindow.ui", f)


class MainWindow(QMainWindow):
    """
    This is the main window of the program.
    """
    points = []  # points the user has entered
    line = object  # line object

    # plot variables
    x_label = ""
    y_label = ""
    plt_title = ""

    # [0] = bg color / [1] = text color
    accent_0 = ["#f0f0f0", "#000000"]  # light gray, black
    accent_1 = ["#ffffff", "#000000"]  # white, black

    def __init__(self):
        super(__class__, self).__init__()
        # POINT SIZE IS 9 FOR ALL WIDGETS IN THIS CLASS
        try:
            # to remove .ui -> uic.loadUi(..., self)
            self.ui = uic.loadUi("{}.ui".format(os.path.join(os.getcwd(), os.path.basename(__file__))))  # load the Designer UI
        except FileNotFoundError:
            raise FileNotFoundError("{}.ui not found. Please make sure it is in the same directory as the script.".format(os.path.basename(__file__)))

        self.ui.setMinimumSize(900, 675)  # keep same aspect ratio as max size
        self.ui.setMaximumSize(1024, 768)

        self.help = HelpWindow()  # init help window
        self.point_editor = PointWindow(self)  # pass in the main window object

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)  # init graph widget
        self.toolbar = NavigationToolbar(self.canvas, self.ui.graph_view)  # init toolbar

        self.init_graph(self.accent_1[0])  # *** SET DEFAULTS FOR GRAPH ***
        self.init_colors(self.accent_0, self.accent_1)  # comment that out if you don't care about the whites not being the same

        self.ui.point_editor.clicked.connect(lambda: self.open_point_dialog())

        self.ui.help.clicked.connect(self.view_help)
        self.ui.calculate.clicked.connect(lambda: self.plot(self.points, plot_line=True))  # bind calculate button to function
        self.ui.reset.clicked.connect(lambda: self.reset_points())  # bind reset button to function
        self.ui.delete_point.clicked.connect(self.delete_point)  # bind delete point button to function
        self.ui.add_point.clicked.connect(self.add_point)  # bind add point button to function
        # QLineEdit will emit signal returnPressed() when user presses enter key while in it
        self.ui.add_point_field.returnPressed.connect(self.add_point)  # assign signal to the add_point button

        self.layout = QVBoxLayout(self.ui.graph_view)  # create a layout INSIDE the QWidget
        self.layout.addWidget(self.toolbar)  # place the toolbar in the layout
        self.layout.addWidget(self.canvas)  # place the graph in the layout

        # Plotting library
        self.ui.lib_change.addItem("Matplotlib")
        self.ui.lib_change.addItem("GPU: Vispy")
        # sip.delete(self.ui.lib_change)

        self.ui.show()

    def init_graph(self, color="#ffffff"):
        """
        This method recreates the graph/plot. call it to clear the graph
        """
        self.figure.clear()
        ax = self.figure.add_subplot(111)  # create axis
        ax.ticklabel_format(useOffset=False, style="plain")  # disable scientific notation on axis
        ax.set_facecolor(color)  # set background color on plot

        # adjust borders of graph
        if self.x_label == "" and self.y_label == "":  # we don't wanna hide the labels if the borders are too small
            top = 0.955
            bottom = 0.085
            left = 0.075
            right = 0.958
            hspace = 0.2
            wspace = 0.2
        else:
            top = 0.966
            bottom = 0.106
            left = 0.130
            right = 0.974
            hspace = 0.2
            wspace = 0.2
        plt.subplots_adjust(left=left, bottom=bottom, right=right, top=top, wspace=wspace, hspace=hspace)

        # axis & title
        plt.xlabel(self.x_label)
        plt.ylabel(self.y_label)
        plt.title(self.plt_title)
        # plt.axis("equal") this keep both axis the same. bad if you only wanna zoom in on only one axis

        # other stuff
        plt.grid(True, color="lightgray")
        self.set_function_label()

        self.canvas.draw()  # optional? definitely not.

    def init_colors(self, accent_0, accent_1):
        """
        This method is totally optional. It initializes the color of all widgets.
        """

        self.figure.patch.set_facecolor(accent_0[0])  # set color outside plot in HEX / value 0-1 (r,g,b)
        # here comes the graph color that u must change in the init_graph() method

        # Main window background
        palette = QtGui.QPalette()
        palette.setColor(self.backgroundRole(), QColor(accent_0[0]))
        self.ui.setPalette(palette)

        # All buttons gotta be the same !!! (bad because it removes the os styles)
        button_str = "QPushButton {{ background-color : {}; color : {}; }}".format(accent_1[0], accent_1[1])
        '''self.ui.calculate.setStyleSheet(button_str)
        self.ui.reset.setStyleSheet(button_str)
        self.ui.add_point.setStyleSheet(button_str)
        self.ui.delete_point.setStyleSheet(button_str)
        self.ui.help.setStyleSheet(button_str)
        self.ui.point_editor.setStyleSheet(button_str)'''

        # line widgets
        line_str = "QLineEdit {{ background-color : {}; color : {}; }}".format(accent_0[0], accent_0[1])
        self.ui.function.setStyleSheet(line_str)
        self.ui.add_point_field.setStyleSheet(button_str)  # this one gotta be different

        # list widgets
        list_str = "QListWidget {{ background-color : {}; color : {}; }}".format(accent_1[0], accent_1[1])
        self.ui.points_list_view.setStyleSheet(list_str)

        # labels
        label_str = "QLabel {{ background-color : {}; color : {}; }}".format(accent_0[0], accent_0[1])
        self.ui.points_label.setStyleSheet(label_str)
        self.ui.graph_label.setStyleSheet(label_str)
        self.ui.fx_label.setStyleSheet(label_str)

        # the one and only checkbox :(
        self.ui.autocalculate.setStyleSheet("QCheckBox {{ background-color : {}; color : {}; }}".format(accent_0[0], accent_0[1]))

    def add_point(self):
        """
        Add point function. bound to button add point
        """
        add_point_value = self.ui.add_point_field.text()  # read text in the box (type:str)
        add_point_value = add_point_value.split(",")  # (type:list)

        if len(add_point_value) is 2:  # check if value is correct format

            # convert_str_to_int_float returns None if conversion failed
            x = convert_str_to_int_float(add_point_value[0])  # get x coord and convert it to int/float
            y = convert_str_to_int_float(add_point_value[1])  # get y coord and convert it to int/float

            """
            MOST IMPORTANT PART OF PROGRAM
            """
            if (x, y) not in self.points:  # if point is not already added
                if x is not None:  # check if x is int or float
                    if y is not None:  # check if y is int/float
                        self.points.append((x, y))
                        self.update_list(self.points)  # update list
                        self.plot((x, y))  # put point on graph
                        self.update_point_nb_field(self.points)
                        self.show_status_bar_message("Added point ({},{})".format(x, y))
                        if self.ui.autocalculate.isChecked():  # if auto-calculate is checked...
                            self.plot(self.points, plot_line=True)  # plot the line
                        self.ui.add_point_field.setText("")  # reset text field
                    else:
                        self.show_status_bar_message("Invalid Format. '{}' is not a valid number".format(add_point_value[1]))
                else:
                    self.show_status_bar_message("Invalid Format. '{}' is not a valid number".format(add_point_value[0]))
            else:
                self.show_status_bar_message("Point already exists!")
                self.ui.add_point_field.setText("")  # reset text field
        else:
            self.show_status_bar_message("Invalid Format. Example input: 4.5,-6")

    def plot(self, points, plot_line=False):
        """
        :param points: the list of points
        :param plot_line: True/False depends if you wanna plot line or points
        """
        if len(points) > 1000:  # put a message because the user has to wait a bit longer
            self.show_status_bar_message("The more points you have, the longer the plotting will take. Please wait while it refreshes.")

        if plot_line:  # setting mode to calculate n draw line
            if len(points) >= 2:  # 2 or more points required to draw line
                try:  # handle this quick and dirty
                    self.line.pop(0).remove()  # remove the line if it exists
                except ValueError as e:
                    print_exception(e)
                except AttributeError as e:
                    print_exception(e)
                except IndexError as e:
                    print_exception(e)

                # get all x coords
                x_coord = []
                for point in range(len(points)):
                    x_coord.append(points[point][0])

                try:
                    a, b = self.calculate_line(self.points)  # get a, b
                except TypeError as e:
                    print_exception(e)
                else:
                    axes = plt.axis()  # save axes without line

                    offset = max(x_coord) * 0.25  # biggest one on x
                    line_1 = min(x_coord) - offset
                    line_2 = max(x_coord) + offset
                    #                        x1      x2           y1                      y2
                    self.line = plt.plot([line_1, line_2], [self.f(a, b, line_1), self.f(a, b, line_2)], color="red", linestyle='-', linewidth=1)

                    # plt.xlim([axes[0], axes[1]])  # apply previous axis
                    # plt.ylim([axes[2], axes[3]])  # bad dont do it

                    if not self.ui.autocalculate.isChecked():
                        self.show_status_bar_message("Line successfully drawn")
                    self.set_function_label(a, b)

            else:
                if not self.ui.autocalculate.isChecked():
                    self.show_status_bar_message("Not enough points to draw line. Minimum 2 required")

        else:  # setting mode to plot points
            if type(points) == list:  # plot every point
                for i in points:
                    # todo: fix: this re-plots points that are already plotted
                    plt.scatter(i[0], i[1], color="black")  # scatter > plot cause you can change color and stuff

            else:  # plot only the tuple x,y
                plt.scatter(points[0], points[1], color="black", s=30)  # s=size, default=36

        self.canvas.draw()

    def update_list(self, points=[]):
        """
        this method updates the widget that lists points on the left
        :type points: point list
        """
        self.ui.points_list_view.clear()  # clear list first
        self.ui.points_list_view.addItems([str(x) for x in points])  # add items back

    def update_point_nb_field(self, points=[]):
        """
        This updates the text above the point widget to show the current number of points.
        :param points: point list
        """
        self.ui.points_label.setText("Points ({})".format(len(points)))

    def delete_point(self):
        """
        method bound to delete point button
        """
        item_pos = self.ui.points_list_view.currentRow()  # get current row of selected item
        if item_pos is not -1:  # -1 if nothing is selected in the widget
            item_value = self.points[item_pos]
            del self.points[item_pos]  # delete point from list
            # todo fix: find better method instead of redrawing everything
            self.init_graph()  # clear graph
            self.plot(self.points)  # plot the points without the removed one
            if self.ui.autocalculate.isChecked():  # if auto-calculate is checked...
                self.plot(self.points, plot_line=True)  # draw line
            self.update_list(self.points)
            self.update_point_nb_field(self.points)
            self.show_status_bar_message("Deleted point {}".format(item_value))
        else:
            self.show_status_bar_message("Please select a point to delete before clicking this button")

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
            self.update_point_nb_field()
            self.update_list()  # update list with nothing
            self.show_status_bar_message("Reset successful")

    def set_function_label(self, a="a", b="b"):
        """
        Displays the a,b of the function on the function label
        :param a:  a part of ax+b
        :param b:  b part of ax+b
        """
        self.ui.function.setText("{} x + {}".format(a, b))

    def show_status_bar_message(self, message):
        """
        Shows a message to the status bar
        """
        time = 5000  # time in ms -> how long will the text be shown in status bar
        self.ui.statusbar.showMessage(message, time)

    def calculate_line(self, points):
        """
        this method calculates the line that passes closer to all points
        I am aware that using numpy it would be easier to do matrix multiplications, etc... but
        I had already done it before I knew that so why redo it?
        :param points: list of points
        :return: a,b part of line. None if not possible
        """
        num_points = len(points)

        matrix_A = []
        for x in range(num_points):
            matrix_A.append([points[x][0], 1])

        matrix_AexpT = [[], []]
        for x in range(num_points):
            matrix_AexpT[0].append(points[x][0])  # append x coords
            matrix_AexpT[1].append(1)  # append the 1s

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

        solvector = []  # y coordinates of points
        for x in points:
            solvector.append(x[1])

        # g = y1*x1+y2*x2+y3*x3...
        g = 0
        for x in range(num_points):
            g = g + solvector[x] * matrix_AexpT[0][x]

        # h = y1*1+y2*1+y3*1...
        h = 0
        for x in range(num_points):
            h = h + solvector[x] * matrix_AexpT[1][x]

        try:
            a = (g * d1 - b1 * h) / (d1 * a1 - b1 * c1)
            b = h / d1 - (c1 / d1 * a)
            return a, b
        except ZeroDivisionError as e:
            print_exception(e)
            if not self.ui.autocalculate.isChecked():
                self.show_status_bar_message("Cannot draw a vertical line")
            return None  # if cannot draw line return none

    @staticmethod
    def f(a, b, x):  # set up function for line
        """
        :param a: a of function
        :param b: b of function
        :param x: x
        :return: y
        """
        return a * x + b

    def view_help(self):
        """
        bound to Help button. opens the help window
        """
        self.help.show()

    def open_point_dialog(self):
        """
        bound to the point editor button. opens the point editor
        """
        self.point_editor.update_text(self)  # pass main window object
        self.point_editor.show()


class HelpWindow(QWidget):  # QWidget necessary to use grid layout
    """
    This is the Help window.
    """

    def __init__(self):
        super(__class__, self).__init__()
        self.setMinimumSize(800, 500)
        self.setMaximumSize(800, 500)
        self.setWindowTitle("Help")
        # self.setWindowIcon(QtGui.QIcon("python.png"))

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setFontPointSize(10)
        self.text.setText("Jon Defilla\nVersion 1.0 (04 aug 2018)\nGNU General Public License\n\n"
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

    def __init__(self, main_window_object):  # main_window_object gives this class access to the main window attributes
        super(__class__, self).__init__()
        self.setWindowTitle("Point Editor")
        self.setMinimumSize(800, 500)
        self.setMaximumSize(800, 9999)  # allow more vertical resizing -> lots of points = wanna see more

        sip.delete(self.okButton)  # delete ok button so we can recreate it later

        self.label = QLabel("Press OK to save the points or cancel to cancel. One point per line. The parenthesis are optional.\n"
                            "Lines with incorrect format will be ignored. "
                            "Example input: \n(5,6)\n-9.3,10.3")
        self.label.setStyleSheet('QLabel { font-size: 9pt }')
        self.grid.addWidget(self.label, 0, 0)

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.setStyleSheet('QPushButton { font-size: 9pt }')
        self.cancelButton.clicked.connect(self.close)
        self.horizontal_box.addWidget(self.cancelButton)

        self.okButton = QPushButton("OK")
        self.okButton.setStyleSheet('QPushButton { font-size: 9pt }')
        self.okButton.clicked.connect(lambda: self.save(main_window_object))  # pass the main window object
        self.horizontal_box.addWidget(self.okButton)

        self.text.setReadOnly(False)

    def update_text(self, main_window_object):
        """
        This method updates the text box to the current list of point
        :param main_window_object: main window object
        """
        points_str = "".join(str(point) + "\n" for point in main_window_object.points)
        self.text.setText(points_str)

    def save(self, main_window_object):  # pass the main window object
        """
        bound to the OK button on the point editor
        If you plot lots of points, the plot function is slowing down the program
        """
        warning = False
        main_window_object.points = []  # reset points
        text_in_box = self.text.toPlainText().split("\n")
        for point in text_in_box:
            if point == "":
                continue  # skip empty lines

            point = point.replace("(", "").replace(")", "")
            point = point.split(",")

            if len(point) is not 2:
                warning = True
                continue  # skip lines with > 2 commas

            x = convert_str_to_int_float(point[0])
            y = convert_str_to_int_float(point[1])

            if x is None or y is None:
                warning = True
                continue

            if (x, y) in main_window_object.points:
                continue  # skip points that already exist

            main_window_object.points.append((x, y))

        if warning is True:  # if there is a point with invalid format
            if self.pop_up_message() is not None:
                return  # if user pressed no: abort function

        main_window_object.update_list(main_window_object.points)
        main_window_object.init_graph()  # reset the graph then plot points

        self.close()  # close window before plotting

        main_window_object.plot(main_window_object.points)  # this is the line that takes ages to finish if you plot lots of points
        main_window_object.update_point_nb_field(main_window_object.points)
        main_window_object.show_status_bar_message("Points refreshed")
        if main_window_object.ui.autocalculate.isChecked():
            main_window_object.plot(main_window_object.points, plot_line=True)

    def pop_up_message(self):
        """
        Makes the pop up message if invalid points have been input.
        :return: None if user pressed Yes | reply if user pressed No
        """
        msg = "One or more points have an invalid format\nand will be skipped. Proceed?"
        reply = QMessageBox.question(self, 'Warning', msg, QMessageBox.Yes | QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            pass  # returns None
        else:
            return reply


def convert_str_to_int_float(string):
    """
    :rtype: None, int, float
    :param string: string you wanna convert to int/float
    :return: type int/float of input. None if not possible
    """
    try:  # convert x to int, then to float
        string = int(string)
    except ValueError as e:
        print_exception(e)
        try:
            string = float(string)
        except ValueError as e:
            print_exception(e)
            return None
    return string


def print_exception(exception):
    if debug:
        print(exception)


def exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


debug = True

if __name__ == '__main__':
    if sys.version_info.major >= 3:  # python 3.x.x or higher
        if debug:
            sys._excepthook = sys.excepthook
            sys.excepthook = exception_hook

        app = QApplication(sys.argv)  # can put [] instead of sys.argv

        main = MainWindow()

        sys.exit(app.exec_())
    else:
        raise Exception("Python 3 or a more recent version is required.")

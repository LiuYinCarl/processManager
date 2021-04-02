import sys
import os
import getpass
import socket
from pathlib import Path
import subprocess
import win32gui
import win32con
import win32api
import time

from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout, QMainWindow,
                            QTableWidget, QFrame, QSplitter, QPushButton, QVBoxLayout,
                            QTabWidget, QTabBar, QPlainTextEdit)
from PyQt5.QtGui import QFont, QTextCursor, QWindow
from PyQt5.QtCore import Qt, pyqtSignal, QProcess, QCoreApplication, QSettings, QEvent, QPoint, QSize, QVersionNumber, QT_VERSION_STR

# 窗口镶嵌
# https://stackoverflow.com/questions/51864808/how-to-use-pyqt-method-qwindow-fromwinidid-on-linux

# 主窗口布局
class MainWindowLayout(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('进程管理器 v0.1')
        self.setGeometry(300, 300, 1000, 600)
        
        # 将主窗口分为左右两边
        hbox = QHBoxLayout(self)

        leftFrame = LeftWindowLayout()
        leftFrame.setFrameShape(QFrame.StyledPanel)

        rightFrame = RightWindowLayout()
        rightFrame.setFrameShape(QFrame.StyledPanel)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(leftFrame)
        splitter.addWidget(rightFrame)

        hbox.addWidget(splitter)
        self.setLayout(hbox)
        self.show()


# 主窗口左半部分程序列表布局
class LeftWindowLayout(QFrame):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 窗口分为上下两部分,上部分显示按钮，下部分显示进程列表
        hbox = QHBoxLayout(self)
    
        topFrame = LeftTopFrame()
        buttonFrame = LeftButtonFrame()

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(topFrame)
        splitter.addWidget(buttonFrame)

        hbox.addWidget(splitter)
        self.setLayout(hbox)
        self.show()


class LeftTopFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        button1 = QPushButton("启动进程", self)
        button2 = QPushButton("重启进程", self)
        button3 = QPushButton("关闭进程", self)
        button4 = QPushButton("强制关闭进程", self)

        hbox = QHBoxLayout()
        hbox.addWidget(button1)
        hbox.addWidget(button2)
        hbox.addWidget(button3)
        hbox.addWidget(button4)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.show()


class LeftButtonFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        hbox = QHBoxLayout()           #横向布局
        tableWidget = QTableWidget()    #创建一个表格
        
        tableWidget.setRowCount(5)
        tableWidget.setColumnCount(4)

        tableWidget.setHorizontalHeaderLabels(['进程名','进程状态','内存占用','CUP占用'])

        hbox.addWidget(tableWidget)

        self.setLayout(hbox)
        self.show()


# 主窗口右半部分进程输出窗口列表布局
class RightWindowLayout(QFrame):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        hbox = QHBoxLayout()
        tabbar = QTabWidget()
        
        self.tab1 = TerminalWidget()
        # self.tab2 = TerminalWidget()
        # self.tab3 = TerminalWidget()
        # self.tab4 = TerminalWidget()

        tabbar.addTab(self.tab1, "progress1")
        # tabbar.addTab(self.tab2, "progress2")
        # tabbar.addTab(self.tab3, "progress3")
        # tabbar.addTab(self.tab4, "progress4")

        hbox.addWidget(tabbar)
        self.setLayout(hbox)
        self.show()


class TerminalWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

# https://stackoverflow.com/questions/41474647/run-a-foreign-exe-inside-a-python-gui-pyqt
    def initUI(self):
        # hbox = QHBoxLayout()

        exePath = "C:\\Windows\\System32\\cmd.exe"
        subprocess.Popen(exePath)

        # self.setLayout(hbox)
        self.show()







class PlainTextEdit(QPlainTextEdit):
    commandSignal = pyqtSignal(str)
    commandZPressed = pyqtSignal(str)

    def __init__(self, parent=None, movable=False):
        super(PlainTextEdit, self).__init__()

        self.installEventFilter(self)
        self.setAcceptDrops(True)
        QApplication.setCursorFlashTime(1000)
        self.process = QProcess()
        self.process.readyReadStandardError.connect(self.onReadyReadStandardError)
        self.process.readyReadStandardOutput.connect(self.onReadyReadStandardOutput)

        self.name = (str(getpass.getuser()) + "@" + str(socket.gethostname()) 
                                + ":" + str(os.getcwd()) + "$ ")
        self.appendPlainText(self.name)
        self.commands = []  # This is a list to track what commands the user has used so we could display them when
        # up arrow key is pressed
        self.tracker = 0
        self.setStyleSheet("QPlainTextEdit{background-color: #212121; color: #f3f3f3; padding: 8;}")
        self.verticalScrollBar().setStyleSheet("background-color: #212121;")
        self.text = None
        self.setFont(QFont("Noto Sans Mono", 8))
        self.previousCommandLength = 0


    def eventFilter(self, source, event):
        if (event.type() == QEvent.DragEnter):
            event.accept()
            print ('DragEnter')
            return True
        elif (event.type() == QEvent.Drop):
            print ('Drop')
            self.setDropEvent(event)
            return True
        else:
            return False ### super(QPlainTextEdit).eventFilter(event)

    def setDropEvent(self, event):
        if event.mimeData().hasUrls():
            f = str(event.mimeData().urls()[0].toLocalFile())
            self.insertPlainText(f)
            event.accept()
        elif event.mimeData().hasText():
            ft = event.mimeData().text()
            print("text:", ft)
            self.insertPlainText(ft)
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, e):
        cursor = self.textCursor()

        if e.modifiers() == Qt.ControlModifier and e.key() == Qt.Key_A:
            return

        if e.modifiers() == Qt.ControlModifier and e.key() == Qt.Key_Z:
            self.commandZPressed.emit("True")
            return

        if e.modifiers() == Qt.ControlModifier and e.key() == Qt.Key_C:
            self.process.kill()
            self.name = (str(getpass.getuser()) + "@" + str(socket.gethostname()) 
                                    + ":" + str(os.getcwd()) + "$ ")
            self.appendPlainText("process cancelled")
            self.appendPlainText(self.name)
            self.textCursor().movePosition(QTextCursor.End)
            return

        if e.key() == Qt.Key_Return:  ### 16777220:  # This is the ENTER key
            text = self.textCursor().block().text()

            if text == self.name + text.replace(self.name, "") and text.replace(self.name, "") != "":  # This is to prevent adding in commands that were not meant to be added in
                self.commands.append(text.replace(self.name, ""))
#                print(self.commands)
            self.handle(text)
            self.commandSignal.emit(text)
            self.appendPlainText(self.name)

            return

        if e.key() == Qt.Key_Up:
            try:
                if self.tracker != 0:
                    cursor.select(QTextCursor.BlockUnderCursor)
                    cursor.removeSelectedText()
                    self.appendPlainText(self.name)

                self.insertPlainText(self.commands[self.tracker])
                self.tracker -= 1

            except IndexError:
                self.tracker = 0

            return

        if e.key() == Qt.Key_Down:
            try:
                cursor.select(QTextCursor.BlockUnderCursor)
                cursor.removeSelectedText()
                self.appendPlainText(self.name)

                self.insertPlainText(self.commands[self.tracker])
                self.tracker += 1

            except IndexError:
                self.tracker = 0

        if e.key() == Qt.Key_Backspace:   ### 16777219:
            if cursor.positionInBlock() <= len(self.name):
                return

            else:
                cursor.deleteChar()

        super().keyPressEvent(e)
        cursor = self.textCursor()
        e.accept()

    def ispressed(self):
        return self.pressed

    def onReadyReadStandardError(self):
        self.error = self.process.readAllStandardError().data().decode()
        self.appendPlainText(self.error.strip('\n'))

    def onReadyReadStandardOutput(self):
        self.result = self.process.readAllStandardOutput().data().decode()
        self.appendPlainText(self.result.strip('\n'))
        self.state = self.process.state()
#        print(self.result)

    def run(self, command):
        """Executes a system command."""
        if self.process.state() != 2:
            self.process.start(command)
            self.process.waitForFinished()
            self.textCursor().movePosition(QTextCursor.End)


    def handle(self, command):
#        print("begin handle") 
        """Split a command into list so command echo hi would appear as ['echo', 'hi']"""
        real_command = command.replace(self.name, "")

        if command == "True":
            if self.process.state() == 2:
                self.process.kill()
                self.appendPlainText("Program execution killed, press enter")

        if real_command.startswith("python"):
            pass

        if real_command != "":
            command_list = real_command.split()
        else:
            command_list = None
        """Now we start implementing some commands"""
        if real_command == "clear":
            self.clear()

        elif command_list is not None and command_list[0] == "echo":
            self.appendPlainText(" ".join(command_list[1:]))

        elif real_command == "exit":
            quit()

        elif command_list is not None and command_list[0] == "cd" and len(command_list) > 1:
            try:
                os.chdir(" ".join(command_list[1:]))
                self.name = (str(getpass.getuser()) + "@" + str(socket.gethostname()) 
                                        + ":" + str(os.getcwd()) + "$ ")
                self.textCursor().movePosition(QTextCursor.End)

            except FileNotFoundError as E:
                self.appendPlainText(str(E))

        elif command_list is not None and len(command_list) == 1 and command_list[0] == "cd":
            os.chdir(str(Path.home()))
            self.name = (str(getpass.getuser()) + "@" + str(socket.gethostname()) 
                                    + ":" + str(os.getcwd()) + "$ ")
            self.textCursor().movePosition(QTextCursor.End)

        elif self.process.state() == 2:
            self.process.write(real_command.encode())
            self.process.closeWriteChannel()

        elif command == self.name + real_command:
            self.run(real_command)
        else:
            pass



# # 管理单个进程的一些信息
# class ProcessManager():
#     def __init__(self):
#         self.processPath = ''
#         self.

# #　单个进程
# class Process():
#     def __init__(self):
#         self.path = ''
#         self.isAlive = False
#         self.pid = 0
#         self.memUsage =0
#         self.CUPUsage = 0
#         self.outFile = ''
    
#     def startProcess(self) -> int:
#         if self.isAlive == True:
#             return 1
#         else:
#             # todo: check process path is reachable
#             if self.path:
#                 subprocess.Popen(self.path)


            






if __name__ == '__main__':
    v_compare = QVersionNumber(5,6,0)
    v_current,_ = QVersionNumber.fromString(QT_VERSION_STR) #获取当前Qt版本
    if QVersionNumber.compare(v_current,v_compare) >=0 :
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  #Qt从5.6.0开始，支持High-DPI
        app = QApplication(sys.argv)  #
    else:
        app = QApplication(sys.argv)
        font = QFont("宋体")
        pointsize = font.pointSize()
        font.setPixelSize(pointsize*90/72)
        app.setFont(font)

    # app = QApplication(sys.argv)
    mainWindow = MainWindowLayout()
    sys.exit(app.exec_())
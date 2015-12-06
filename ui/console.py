# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt\ui\console.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Console(object):
    def setupUi(self, Console):
        Console.setObjectName(_fromUtf8("Console"))
        Console.resize(689, 369)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/monokuma-green.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Console.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(Console)
        self.verticalLayout.setMargin(2)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.txtConsole = XLoggerWidget(Console)
        self.txtConsole.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        self.txtConsole.setObjectName(_fromUtf8("txtConsole"))
        self.verticalLayout.addWidget(self.txtConsole)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(4, -1, 0, -1)
        self.horizontalLayout.setSpacing(8)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(Console)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.cboLevels = QtGui.QComboBox(Console)
        self.cboLevels.setObjectName(_fromUtf8("cboLevels"))
        self.horizontalLayout.addWidget(self.cboLevels)
        self.chkWordWrap = QtGui.QCheckBox(Console)
        self.chkWordWrap.setObjectName(_fromUtf8("chkWordWrap"))
        self.horizontalLayout.addWidget(self.chkWordWrap)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButton = QtGui.QPushButton(Console)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.horizontalLayout.addWidget(self.pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Console)
        QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.txtConsole.clear)
        QtCore.QObject.connect(self.cboLevels, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(QString)")), Console.updateLogLevel)
        QtCore.QMetaObject.connectSlotsByName(Console)

    def retranslateUi(self, Console):
        Console.setWindowTitle(_translate("Console", "Console", None))
        self.label.setText(_translate("Console", "Logging Level", None))
        self.chkWordWrap.setText(_translate("Console", "Word wrap", None))
        self.pushButton.setText(_translate("Console", "Clear", None))

from projexui.xloggerwidget import XLoggerWidget
import icons_rc

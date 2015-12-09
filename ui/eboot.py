# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt\ui\eboot.ui'
#
# Created: Tue Jul 16 17:26:47 2013
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_EbootEditor(object):
    def setupUi(self, EbootEditor):
        EbootEditor.setObjectName(_fromUtf8("EbootEditor"))
        EbootEditor.resize(610, 374)
        EbootEditor.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        EbootEditor.setWindowTitle(QtGui.QApplication.translate("EbootEditor", "EBOOT Text Editor", None, QtGui.QApplication.UnicodeUTF8))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/monokuma.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        EbootEditor.setWindowIcon(icon)
        self.buttonBox = QtGui.QDialogButtonBox(EbootEditor)
        self.buttonBox.setGeometry(QtCore.QRect(260, 340, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.lstLines = QtGui.QListWidget(EbootEditor)
        self.lstLines.setGeometry(QtCore.QRect(10, 40, 131, 291))
        self.lstLines.setObjectName(_fromUtf8("lstLines"))
        self.txtTranslated = SpellCheckEdit(EbootEditor)
        self.txtTranslated.setGeometry(QtCore.QRect(150, 40, 451, 91))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Meiryo UI"))
        font.setPointSize(11)
        self.txtTranslated.setFont(font)
        self.txtTranslated.setObjectName(_fromUtf8("txtTranslated"))
        self.txtOriginal = QtGui.QPlainTextEdit(EbootEditor)
        self.txtOriginal.setGeometry(QtCore.QRect(150, 180, 451, 91))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Meiryo UI"))
        font.setPointSize(11)
        self.txtOriginal.setFont(font)
        self.txtOriginal.setReadOnly(True)
        self.txtOriginal.setTabStopWidth(20)
        self.txtOriginal.setObjectName(_fromUtf8("txtOriginal"))
        self.txtEncoding = QtGui.QLineEdit(EbootEditor)
        self.txtEncoding.setGeometry(QtCore.QRect(150, 310, 451, 20))
        self.txtEncoding.setReadOnly(True)
        self.txtEncoding.setObjectName(_fromUtf8("txtEncoding"))
        self.label_6 = QtGui.QLabel(EbootEditor)
        self.label_6.setGeometry(QtCore.QRect(150, 0, 131, 41))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Meiryo UI"))
        font.setPointSize(18)
        self.label_6.setFont(font)
        self.label_6.setText(QtGui.QApplication.translate("EbootEditor", "Translated", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.label_7 = QtGui.QLabel(EbootEditor)
        self.label_7.setGeometry(QtCore.QRect(150, 140, 131, 41))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Meiryo UI"))
        font.setPointSize(18)
        self.label_7.setFont(font)
        self.label_7.setText(QtGui.QApplication.translate("EbootEditor", "Original", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.label_10 = QtGui.QLabel(EbootEditor)
        self.label_10.setGeometry(QtCore.QRect(150, 280, 121, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Meiryo UI"))
        font.setPointSize(11)
        self.label_10.setFont(font)
        self.label_10.setText(QtGui.QApplication.translate("EbootEditor", "Encoding", None, QtGui.QApplication.UnicodeUTF8))
        self.label_10.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.label_11 = QtGui.QLabel(EbootEditor)
        self.label_11.setGeometry(QtCore.QRect(10, 10, 121, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Meiryo UI"))
        font.setPointSize(11)
        self.label_11.setFont(font)
        self.label_11.setText(QtGui.QApplication.translate("EbootEditor", "Lines", None, QtGui.QApplication.UnicodeUTF8))
        self.label_11.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.lblOrigLength = QtGui.QLabel(EbootEditor)
        self.lblOrigLength.setGeometry(QtCore.QRect(290, 150, 121, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Meiryo UI"))
        font.setPointSize(9)
        self.lblOrigLength.setFont(font)
        self.lblOrigLength.setText(QtGui.QApplication.translate("EbootEditor", "Length: XX", None, QtGui.QApplication.UnicodeUTF8))
        self.lblOrigLength.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.lblOrigLength.setObjectName(_fromUtf8("lblOrigLength"))
        self.lblTransLength = QtGui.QLabel(EbootEditor)
        self.lblTransLength.setGeometry(QtCore.QRect(290, 10, 121, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Meiryo UI"))
        font.setPointSize(9)
        self.lblTransLength.setFont(font)
        self.lblTransLength.setText(QtGui.QApplication.translate("EbootEditor", "Length: XX", None, QtGui.QApplication.UnicodeUTF8))
        self.lblTransLength.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.lblTransLength.setObjectName(_fromUtf8("lblTransLength"))

        self.retranslateUi(EbootEditor)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), EbootEditor.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), EbootEditor.reject)
        QtCore.QObject.connect(self.txtTranslated, QtCore.SIGNAL(_fromUtf8("textChanged()")), EbootEditor.changedTranslation)
        QtCore.QObject.connect(self.lstLines, QtCore.SIGNAL(_fromUtf8("currentRowChanged(int)")), EbootEditor.changedLine)
        QtCore.QMetaObject.connectSlotsByName(EbootEditor)

    def retranslateUi(self, EbootEditor):
        pass

from spellcheck_edit import SpellCheckEdit
import icons_rc

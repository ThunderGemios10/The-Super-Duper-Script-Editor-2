# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt\ui\termedit.ui'
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

class Ui_TermEdit(object):
    def setupUi(self, TermEdit):
        TermEdit.setObjectName(_fromUtf8("TermEdit"))
        TermEdit.resize(448, 97)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/monokuma.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        TermEdit.setWindowIcon(icon)
        self.buttonBox = QtGui.QDialogButtonBox(TermEdit)
        self.buttonBox.setGeometry(QtCore.QRect(370, 39, 71, 51))
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.txtJapanese = QtGui.QLineEdit(TermEdit)
        self.txtJapanese.setGeometry(QtCore.QRect(70, 40, 291, 20))
        self.txtJapanese.setObjectName(_fromUtf8("txtJapanese"))
        self.txtEnglish = QtGui.QLineEdit(TermEdit)
        self.txtEnglish.setGeometry(QtCore.QRect(70, 70, 291, 20))
        self.txtEnglish.setObjectName(_fromUtf8("txtEnglish"))
        self.label = QtGui.QLabel(TermEdit)
        self.label.setGeometry(QtCore.QRect(10, 10, 431, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(TermEdit)
        self.label_2.setGeometry(QtCore.QRect(10, 40, 51, 18))
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(TermEdit)
        self.label_3.setGeometry(QtCore.QRect(10, 70, 51, 18))
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName(_fromUtf8("label_3"))

        self.retranslateUi(TermEdit)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), TermEdit.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), TermEdit.reject)
        QtCore.QMetaObject.connectSlotsByName(TermEdit)
        TermEdit.setTabOrder(self.txtJapanese, self.txtEnglish)
        TermEdit.setTabOrder(self.txtEnglish, self.buttonBox)

    def retranslateUi(self, TermEdit):
        TermEdit.setWindowTitle(_translate("TermEdit", "Term", None))
        self.label.setText(_translate("TermEdit", "Please input the original Japanese and the English translation of the term.", None))
        self.label_2.setText(_translate("TermEdit", "Japanese", None))
        self.label_3.setText(_translate("TermEdit", "English", None))

import icons_rc

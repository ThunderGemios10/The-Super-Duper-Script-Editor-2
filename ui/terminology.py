# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt\ui\terminology.ui'
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

class Ui_TerminologyEditor(object):
    def setupUi(self, TerminologyEditor):
        TerminologyEditor.setObjectName(_fromUtf8("TerminologyEditor"))
        TerminologyEditor.resize(479, 341)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(TerminologyEditor.sizePolicy().hasHeightForWidth())
        TerminologyEditor.setSizePolicy(sizePolicy)
        TerminologyEditor.setMinimumSize(QtCore.QSize(479, 341))
        TerminologyEditor.setMaximumSize(QtCore.QSize(479, 341))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/monokuma-green.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        TerminologyEditor.setWindowIcon(icon)
        TerminologyEditor.setSizeGripEnabled(False)
        self.tabTerminology = QtGui.QTabWidget(TerminologyEditor)
        self.tabTerminology.setGeometry(QtCore.QRect(10, 10, 364, 326))
        self.tabTerminology.setMovable(True)
        self.tabTerminology.setObjectName(_fromUtf8("tabTerminology"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.tabTerminology.addTab(self.tab, _fromUtf8(""))
        self.btnAddSection = QtGui.QPushButton(TerminologyEditor)
        self.btnAddSection.setGeometry(QtCore.QRect(380, 131, 91, 23))
        self.btnAddSection.setObjectName(_fromUtf8("btnAddSection"))
        self.btnAddWord = QtGui.QPushButton(TerminologyEditor)
        self.btnAddWord.setGeometry(QtCore.QRect(380, 30, 91, 23))
        self.btnAddWord.setObjectName(_fromUtf8("btnAddWord"))
        self.btnDeleteWord = QtGui.QPushButton(TerminologyEditor)
        self.btnDeleteWord.setGeometry(QtCore.QRect(380, 90, 91, 23))
        self.btnDeleteWord.setObjectName(_fromUtf8("btnDeleteWord"))
        self.btnDeleteSection = QtGui.QPushButton(TerminologyEditor)
        self.btnDeleteSection.setGeometry(QtCore.QRect(380, 191, 91, 23))
        self.btnDeleteSection.setObjectName(_fromUtf8("btnDeleteSection"))
        self.btnClose = QtGui.QPushButton(TerminologyEditor)
        self.btnClose.setGeometry(QtCore.QRect(380, 310, 91, 23))
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.btnEditWord = QtGui.QPushButton(TerminologyEditor)
        self.btnEditWord.setGeometry(QtCore.QRect(380, 60, 91, 23))
        self.btnEditWord.setObjectName(_fromUtf8("btnEditWord"))
        self.btnRenameSection = QtGui.QPushButton(TerminologyEditor)
        self.btnRenameSection.setGeometry(QtCore.QRect(380, 161, 91, 23))
        self.btnRenameSection.setObjectName(_fromUtf8("btnRenameSection"))
        self.line = QtGui.QFrame(TerminologyEditor)
        self.line.setGeometry(QtCore.QRect(380, 122, 91, 3))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.line_2 = QtGui.QFrame(TerminologyEditor)
        self.line_2.setGeometry(QtCore.QRect(380, 223, 91, 3))
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.btnRefresh = QtGui.QPushButton(TerminologyEditor)
        self.btnRefresh.setGeometry(QtCore.QRect(380, 232, 91, 23))
        self.btnRefresh.setObjectName(_fromUtf8("btnRefresh"))

        self.retranslateUi(TerminologyEditor)
        self.tabTerminology.setCurrentIndex(0)
        QtCore.QObject.connect(self.btnClose, QtCore.SIGNAL(_fromUtf8("clicked()")), TerminologyEditor.accept)
        QtCore.QObject.connect(self.btnAddSection, QtCore.SIGNAL(_fromUtf8("clicked()")), TerminologyEditor.add_section_button)
        QtCore.QObject.connect(self.btnDeleteSection, QtCore.SIGNAL(_fromUtf8("clicked()")), TerminologyEditor.delete_section)
        QtCore.QObject.connect(self.btnAddWord, QtCore.SIGNAL(_fromUtf8("clicked()")), TerminologyEditor.add_term_button)
        QtCore.QObject.connect(self.btnDeleteWord, QtCore.SIGNAL(_fromUtf8("clicked()")), TerminologyEditor.delete_term)
        QtCore.QObject.connect(self.btnEditWord, QtCore.SIGNAL(_fromUtf8("clicked()")), TerminologyEditor.edit_term)
        QtCore.QObject.connect(self.btnRenameSection, QtCore.SIGNAL(_fromUtf8("clicked()")), TerminologyEditor.rename_section)
        QtCore.QObject.connect(self.btnRefresh, QtCore.SIGNAL(_fromUtf8("clicked()")), TerminologyEditor.refresh_ui)
        QtCore.QMetaObject.connectSlotsByName(TerminologyEditor)
        TerminologyEditor.setTabOrder(self.tabTerminology, self.btnAddWord)
        TerminologyEditor.setTabOrder(self.btnAddWord, self.btnEditWord)
        TerminologyEditor.setTabOrder(self.btnEditWord, self.btnDeleteWord)
        TerminologyEditor.setTabOrder(self.btnDeleteWord, self.btnAddSection)
        TerminologyEditor.setTabOrder(self.btnAddSection, self.btnRenameSection)
        TerminologyEditor.setTabOrder(self.btnRenameSection, self.btnDeleteSection)
        TerminologyEditor.setTabOrder(self.btnDeleteSection, self.btnClose)

    def retranslateUi(self, TerminologyEditor):
        TerminologyEditor.setWindowTitle(_translate("TerminologyEditor", "Terminology", None))
        self.tabTerminology.setTabText(self.tabTerminology.indexOf(self.tab), _translate("TerminologyEditor", "General", None))
        self.btnAddSection.setText(_translate("TerminologyEditor", "Add Section", None))
        self.btnAddWord.setText(_translate("TerminologyEditor", "Add Term", None))
        self.btnDeleteWord.setText(_translate("TerminologyEditor", "Delete Term", None))
        self.btnDeleteSection.setText(_translate("TerminologyEditor", "Delete Section", None))
        self.btnClose.setText(_translate("TerminologyEditor", "Close", None))
        self.btnEditWord.setText(_translate("TerminologyEditor", "Edit Term", None))
        self.btnRenameSection.setText(_translate("TerminologyEditor", "Rename Section", None))
        self.btnRefresh.setText(_translate("TerminologyEditor", "Refresh List", None))

import icons_rc

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt\ui\scriptdump.ui'
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

class Ui_ScriptDumpMenu(object):
    def setupUi(self, ScriptDumpMenu):
        ScriptDumpMenu.setObjectName(_fromUtf8("ScriptDumpMenu"))
        ScriptDumpMenu.resize(480, 324)
        ScriptDumpMenu.setMinimumSize(QtCore.QSize(480, 324))
        ScriptDumpMenu.setMaximumSize(QtCore.QSize(16777215, 16777215))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/monokuma-green.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ScriptDumpMenu.setWindowIcon(icon)
        self.horizontalLayout = QtGui.QHBoxLayout(ScriptDumpMenu)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.treeFileList = QtGui.QTreeWidget(ScriptDumpMenu)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.treeFileList.sizePolicy().hasHeightForWidth())
        self.treeFileList.setSizePolicy(sizePolicy)
        self.treeFileList.setAlternatingRowColors(True)
        self.treeFileList.setIndentation(15)
        self.treeFileList.setAnimated(True)
        self.treeFileList.setObjectName(_fromUtf8("treeFileList"))
        self.treeFileList.header().setVisible(False)
        self.horizontalLayout.addWidget(self.treeFileList)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(ScriptDumpMenu)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Meiryo UI"))
        font.setPointSize(11)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.lblChapter = QtGui.QLabel(ScriptDumpMenu)
        self.lblChapter.setIndent(10)
        self.lblChapter.setObjectName(_fromUtf8("lblChapter"))
        self.verticalLayout.addWidget(self.lblChapter)
        self.label_3 = QtGui.QLabel(ScriptDumpMenu)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Meiryo UI"))
        font.setPointSize(11)
        self.label_3.setFont(font)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout.addWidget(self.label_3)
        self.lblScene = QtGui.QLabel(ScriptDumpMenu)
        self.lblScene.setIndent(10)
        self.lblScene.setObjectName(_fromUtf8("lblScene"))
        self.verticalLayout.addWidget(self.lblScene)
        self.label_4 = QtGui.QLabel(ScriptDumpMenu)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Meiryo UI"))
        font.setPointSize(11)
        self.label_4.setFont(font)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout.addWidget(self.label_4)
        self.lblRoom = QtGui.QLabel(ScriptDumpMenu)
        self.lblRoom.setIndent(10)
        self.lblRoom.setObjectName(_fromUtf8("lblRoom"))
        self.verticalLayout.addWidget(self.lblRoom)
        self.label_6 = QtGui.QLabel(ScriptDumpMenu)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Meiryo UI"))
        font.setPointSize(11)
        self.label_6.setFont(font)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.verticalLayout.addWidget(self.label_6)
        self.lblMode = QtGui.QLabel(ScriptDumpMenu)
        self.lblMode.setIndent(10)
        self.lblMode.setObjectName(_fromUtf8("lblMode"))
        self.verticalLayout.addWidget(self.lblMode)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.chkStripClt = QtGui.QCheckBox(ScriptDumpMenu)
        self.chkStripClt.setObjectName(_fromUtf8("chkStripClt"))
        self.verticalLayout.addWidget(self.chkStripClt)
        self.chkLineNumbers = QtGui.QCheckBox(ScriptDumpMenu)
        self.chkLineNumbers.setObjectName(_fromUtf8("chkLineNumbers"))
        self.verticalLayout.addWidget(self.chkLineNumbers)
        self.chkOnlyVoiced = QtGui.QCheckBox(ScriptDumpMenu)
        self.chkOnlyVoiced.setObjectName(_fromUtf8("chkOnlyVoiced"))
        self.verticalLayout.addWidget(self.chkOnlyVoiced)
        self.chkUntranslated = QtGui.QCheckBox(ScriptDumpMenu)
        self.chkUntranslated.setChecked(False)
        self.chkUntranslated.setObjectName(_fromUtf8("chkUntranslated"))
        self.verticalLayout.addWidget(self.chkUntranslated)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.btnDump = QtGui.QPushButton(ScriptDumpMenu)
        self.btnDump.setObjectName(_fromUtf8("btnDump"))
        self.horizontalLayout_2.addWidget(self.btnDump)
        self.btnClose = QtGui.QPushButton(ScriptDumpMenu)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.horizontalLayout_2.addWidget(self.btnClose)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.retranslateUi(ScriptDumpMenu)
        QtCore.QObject.connect(self.treeFileList, QtCore.SIGNAL(_fromUtf8("currentItemChanged(QTreeWidgetItem*,QTreeWidgetItem*)")), ScriptDumpMenu.changeSelection)
        QtCore.QObject.connect(self.treeFileList, QtCore.SIGNAL(_fromUtf8("itemChanged(QTreeWidgetItem*,int)")), ScriptDumpMenu.updateChecks)
        QtCore.QObject.connect(self.btnDump, QtCore.SIGNAL(_fromUtf8("clicked()")), ScriptDumpMenu.dump_script)
        QtCore.QObject.connect(self.btnClose, QtCore.SIGNAL(_fromUtf8("clicked()")), ScriptDumpMenu.accept)
        QtCore.QMetaObject.connectSlotsByName(ScriptDumpMenu)

    def retranslateUi(self, ScriptDumpMenu):
        ScriptDumpMenu.setWindowTitle(_translate("ScriptDumpMenu", "Script Dumper", None))
        self.treeFileList.headerItem().setText(0, _translate("ScriptDumpMenu", "1", None))
        self.label.setText(_translate("ScriptDumpMenu", "Chapter", None))
        self.lblChapter.setText(_translate("ScriptDumpMenu", "TextLabel", None))
        self.label_3.setText(_translate("ScriptDumpMenu", "Scene", None))
        self.lblScene.setText(_translate("ScriptDumpMenu", "TextLabel", None))
        self.label_4.setText(_translate("ScriptDumpMenu", "Room", None))
        self.lblRoom.setText(_translate("ScriptDumpMenu", "TextLabel", None))
        self.label_6.setText(_translate("ScriptDumpMenu", "Mode", None))
        self.lblMode.setText(_translate("ScriptDumpMenu", "TextLabel", None))
        self.chkStripClt.setText(_translate("ScriptDumpMenu", "Strip CLT tags", None))
        self.chkLineNumbers.setText(_translate("ScriptDumpMenu", "Include line numbers", None))
        self.chkOnlyVoiced.setText(_translate("ScriptDumpMenu", "Only dump voiced lines", None))
        self.chkUntranslated.setText(_translate("ScriptDumpMenu", "Dump untranslated text", None))
        self.btnDump.setText(_translate("ScriptDumpMenu", "Dump", None))
        self.btnClose.setText(_translate("ScriptDumpMenu", "Close", None))

import icons_rc

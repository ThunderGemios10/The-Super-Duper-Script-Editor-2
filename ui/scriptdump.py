# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt\ui\scriptdump.ui'
#
# Created: Tue Jul 16 17:26:48 2013
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ScriptDumpMenu(object):
    def setupUi(self, ScriptDumpMenu):
        ScriptDumpMenu.setObjectName(_fromUtf8("ScriptDumpMenu"))
        ScriptDumpMenu.resize(480, 324)
        ScriptDumpMenu.setMinimumSize(QtCore.QSize(480, 324))
        ScriptDumpMenu.setMaximumSize(QtCore.QSize(16777215, 16777215))
        ScriptDumpMenu.setWindowTitle(QtGui.QApplication.translate("ScriptDumpMenu", "Script Dumper", None, QtGui.QApplication.UnicodeUTF8))
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
        self.treeFileList.headerItem().setText(0, QtGui.QApplication.translate("ScriptDumpMenu", "1", None, QtGui.QApplication.UnicodeUTF8))
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
        self.label.setText(QtGui.QApplication.translate("ScriptDumpMenu", "Chapter", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.lblChapter = QtGui.QLabel(ScriptDumpMenu)
        self.lblChapter.setText(QtGui.QApplication.translate("ScriptDumpMenu", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.lblChapter.setIndent(10)
        self.lblChapter.setObjectName(_fromUtf8("lblChapter"))
        self.verticalLayout.addWidget(self.lblChapter)
        self.label_3 = QtGui.QLabel(ScriptDumpMenu)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Meiryo UI"))
        font.setPointSize(11)
        self.label_3.setFont(font)
        self.label_3.setText(QtGui.QApplication.translate("ScriptDumpMenu", "Scene", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout.addWidget(self.label_3)
        self.lblScene = QtGui.QLabel(ScriptDumpMenu)
        self.lblScene.setText(QtGui.QApplication.translate("ScriptDumpMenu", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.lblScene.setIndent(10)
        self.lblScene.setObjectName(_fromUtf8("lblScene"))
        self.verticalLayout.addWidget(self.lblScene)
        self.label_4 = QtGui.QLabel(ScriptDumpMenu)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Meiryo UI"))
        font.setPointSize(11)
        self.label_4.setFont(font)
        self.label_4.setText(QtGui.QApplication.translate("ScriptDumpMenu", "Room", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout.addWidget(self.label_4)
        self.lblRoom = QtGui.QLabel(ScriptDumpMenu)
        self.lblRoom.setText(QtGui.QApplication.translate("ScriptDumpMenu", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.lblRoom.setIndent(10)
        self.lblRoom.setObjectName(_fromUtf8("lblRoom"))
        self.verticalLayout.addWidget(self.lblRoom)
        self.label_6 = QtGui.QLabel(ScriptDumpMenu)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Meiryo UI"))
        font.setPointSize(11)
        self.label_6.setFont(font)
        self.label_6.setText(QtGui.QApplication.translate("ScriptDumpMenu", "Mode", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.verticalLayout.addWidget(self.label_6)
        self.lblMode = QtGui.QLabel(ScriptDumpMenu)
        self.lblMode.setText(QtGui.QApplication.translate("ScriptDumpMenu", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.lblMode.setIndent(10)
        self.lblMode.setObjectName(_fromUtf8("lblMode"))
        self.verticalLayout.addWidget(self.lblMode)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.chkStripClt = QtGui.QCheckBox(ScriptDumpMenu)
        self.chkStripClt.setText(QtGui.QApplication.translate("ScriptDumpMenu", "Strip CLT tags", None, QtGui.QApplication.UnicodeUTF8))
        self.chkStripClt.setObjectName(_fromUtf8("chkStripClt"))
        self.verticalLayout.addWidget(self.chkStripClt)
        self.chkLineNumbers = QtGui.QCheckBox(ScriptDumpMenu)
        self.chkLineNumbers.setText(QtGui.QApplication.translate("ScriptDumpMenu", "Include line numbers", None, QtGui.QApplication.UnicodeUTF8))
        self.chkLineNumbers.setObjectName(_fromUtf8("chkLineNumbers"))
        self.verticalLayout.addWidget(self.chkLineNumbers)
        self.chkOnlyVoiced = QtGui.QCheckBox(ScriptDumpMenu)
        self.chkOnlyVoiced.setText(QtGui.QApplication.translate("ScriptDumpMenu", "Only dump voiced lines", None, QtGui.QApplication.UnicodeUTF8))
        self.chkOnlyVoiced.setObjectName(_fromUtf8("chkOnlyVoiced"))
        self.verticalLayout.addWidget(self.chkOnlyVoiced)
        self.chkUntranslated = QtGui.QCheckBox(ScriptDumpMenu)
        self.chkUntranslated.setText(QtGui.QApplication.translate("ScriptDumpMenu", "Dump untranslated text", None, QtGui.QApplication.UnicodeUTF8))
        self.chkUntranslated.setChecked(False)
        self.chkUntranslated.setObjectName(_fromUtf8("chkUntranslated"))
        self.verticalLayout.addWidget(self.chkUntranslated)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.btnDump = QtGui.QPushButton(ScriptDumpMenu)
        self.btnDump.setText(QtGui.QApplication.translate("ScriptDumpMenu", "Dump", None, QtGui.QApplication.UnicodeUTF8))
        self.btnDump.setObjectName(_fromUtf8("btnDump"))
        self.horizontalLayout_2.addWidget(self.btnDump)
        self.btnClose = QtGui.QPushButton(ScriptDumpMenu)
        self.btnClose.setText(QtGui.QApplication.translate("ScriptDumpMenu", "Close", None, QtGui.QApplication.UnicodeUTF8))
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
        pass

import icons_rc

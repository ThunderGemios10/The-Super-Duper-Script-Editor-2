# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt\ui\nonstopplayer.ui'
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

class Ui_NonstopPlayer(object):
    def setupUi(self, NonstopPlayer):
        NonstopPlayer.setObjectName(_fromUtf8("NonstopPlayer"))
        NonstopPlayer.resize(498, 311)
        NonstopPlayer.setMinimumSize(QtCore.QSize(498, 311))
        NonstopPlayer.setMaximumSize(QtCore.QSize(498, 311))
        NonstopPlayer.setWindowTitle(QtGui.QApplication.translate("NonstopPlayer", "Nonstop Debate Player", None, QtGui.QApplication.UnicodeUTF8))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/monokuma.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        NonstopPlayer.setWindowIcon(icon)
        self.buttonBox = QtGui.QDialogButtonBox(NonstopPlayer)
        self.buttonBox.setGeometry(QtCore.QRect(339, 280, 151, 31))
        self.buttonBox.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.lblPreview = QtGui.QLabel(NonstopPlayer)
        self.lblPreview.setGeometry(QtCore.QRect(9, 9, 480, 272))
        self.lblPreview.setFrameShape(QtGui.QFrame.StyledPanel)
        self.lblPreview.setFrameShadow(QtGui.QFrame.Sunken)
        self.lblPreview.setText(_fromUtf8(""))
        self.lblPreview.setObjectName(_fromUtf8("lblPreview"))

        self.retranslateUi(NonstopPlayer)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), NonstopPlayer.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), NonstopPlayer.reject)
        QtCore.QMetaObject.connectSlotsByName(NonstopPlayer)

    def retranslateUi(self, NonstopPlayer):
        pass

import icons_rc

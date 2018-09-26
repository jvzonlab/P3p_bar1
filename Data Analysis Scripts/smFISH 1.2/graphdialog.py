# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'graphdialog.ui'
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

class Ui_GraphDialog(object):
    def setupUi(self, GraphDialog):
        GraphDialog.setObjectName(_fromUtf8("GraphDialog"))
        GraphDialog.resize(419, 331)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(GraphDialog.sizePolicy().hasHeightForWidth())
        GraphDialog.setSizePolicy(sizePolicy)
        GraphDialog.setMinimumSize(QtCore.QSize(400, 300))
        GraphDialog.setMaximumSize(QtCore.QSize(420, 331))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(GraphDialog)
        self.horizontalLayout_2.setMargin(11)
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setMargin(11)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setMargin(11)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.pushButton = QtGui.QPushButton(GraphDialog)
        self.pushButton.setObjectName(_fromUtf8("<"))
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton_2 = QtGui.QPushButton(GraphDialog)
        self.pushButton_2.setObjectName(_fromUtf8("<<"))
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.pushButton_3 = QtGui.QPushButton(GraphDialog)
        self.pushButton_3.setObjectName(_fromUtf8(">>"))
        self.horizontalLayout.addWidget(self.pushButton_3)
        self.pushButton_4 = QtGui.QPushButton(GraphDialog)
        self.pushButton_4.setObjectName(_fromUtf8(">"))
        self.horizontalLayout.addWidget(self.pushButton_4)
        self.pushButton_5 = QtGui.QPushButton(GraphDialog)
        self.pushButton_5.setObjectName(_fromUtf8("Set"))
        self.horizontalLayout.addWidget(self.pushButton_5)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(GraphDialog)
        QtCore.QMetaObject.connectSlotsByName(GraphDialog)

    def retranslateUi(self, GraphDialog):
        GraphDialog.setWindowTitle(_translate("GraphDialog", "GraphDialog", None))
        self.pushButton.setText(_translate("GraphDialog", "PushButton", None))
        self.pushButton_2.setText(_translate("GraphDialog", "PushButton", None))
        self.pushButton_3.setText(_translate("GraphDialog", "PushButton", None))
        self.pushButton_4.setText(_translate("GraphDialog", "PushButton", None))
        self.pushButton_5.setText(_translate("GraphDialog", "PushButton", None))


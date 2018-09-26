# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialog.ui'
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(330, 276)
        self.horizontalLayout = QtGui.QHBoxLayout(Dialog)
        self.horizontalLayout.setMargin(11)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.widget = QtGui.QWidget(Dialog)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout.setMargin(11)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.lineEdit = QtGui.QLineEdit(self.widget)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.verticalLayout.addWidget(self.lineEdit)
        self.lineEdit_2 = QtGui.QLineEdit(self.widget)
        self.lineEdit_2.setObjectName(_fromUtf8("lineEdit_2"))
        self.verticalLayout.addWidget(self.lineEdit_2)
        self.lineEdit_3 = QtGui.QLineEdit(self.widget)
        self.lineEdit_3.setObjectName(_fromUtf8("lineEdit_3"))
        self.verticalLayout.addWidget(self.lineEdit_3)
        self.lineEdit_4 = QtGui.QLineEdit(self.widget)
        self.lineEdit_4.setObjectName(_fromUtf8("lineEdit_4"))
        self.verticalLayout.addWidget(self.lineEdit_4)
        self.lineEdit_5 = QtGui.QLineEdit(self.widget)
        self.lineEdit_5.setObjectName(_fromUtf8("lineEdit_5"))
        self.verticalLayout.addWidget(self.lineEdit_5)
        self.lineEdit_6 = QtGui.QLineEdit(self.widget)
        self.lineEdit_6.setObjectName(_fromUtf8("lineEdit_6"))
        self.verticalLayout.addWidget(self.lineEdit_6)
        self.widget_4 = QtGui.QWidget(self.widget)
        self.widget_4.setObjectName(_fromUtf8("widget_4"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.widget_4)
        self.verticalLayout_3.setMargin(11)
        self.verticalLayout_3.setSpacing(6)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.checkBox = QtGui.QCheckBox(self.widget_4)
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.verticalLayout_3.addWidget(self.checkBox)
        self.checkBox_2 = QtGui.QCheckBox(self.widget_4)
        self.checkBox_2.setObjectName(_fromUtf8("checkBox_2"))
        self.verticalLayout_3.addWidget(self.checkBox_2)
        self.checkBox_3 = QtGui.QCheckBox(self.widget_4)
        self.checkBox_3.setObjectName(_fromUtf8("checkBox_3"))
        self.verticalLayout_3.addWidget(self.checkBox_3)
        self.verticalLayout.addWidget(self.widget_4)
        self.horizontalLayout.addWidget(self.widget)
        self.widget_2 = QtGui.QWidget(Dialog)
        self.widget_2.setMinimumSize(QtCore.QSize(200, 0))
        self.widget_2.setObjectName(_fromUtf8("widget_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.widget_2)
        self.verticalLayout_2.setMargin(11)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.comboBox = QtGui.QComboBox(self.widget_2)
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.verticalLayout_2.addWidget(self.comboBox)
        self.comboBox_2 = QtGui.QComboBox(self.widget_2)
        self.comboBox_2.setObjectName(_fromUtf8("comboBox_2"))
        self.verticalLayout_2.addWidget(self.comboBox_2)
        self.comboBox_3 = QtGui.QComboBox(self.widget_2)
        self.comboBox_3.setObjectName(_fromUtf8("comboBox_3"))
        self.verticalLayout_2.addWidget(self.comboBox_3)
        self.comboBox_4 = QtGui.QComboBox(self.widget_2)
        self.comboBox_4.setObjectName(_fromUtf8("comboBox_4"))
        self.verticalLayout_2.addWidget(self.comboBox_4)
        self.comboBox_5 = QtGui.QComboBox(self.widget_2)
        self.comboBox_5.setObjectName(_fromUtf8("comboBox_5"))
        self.verticalLayout_2.addWidget(self.comboBox_5)
        self.comboBox_6 = QtGui.QComboBox(self.widget_2)
        self.comboBox_6.setObjectName(_fromUtf8("comboBox_6"))
        self.verticalLayout_2.addWidget(self.comboBox_6)
        self.widget_3 = QtGui.QWidget(self.widget_2)
        self.widget_3.setObjectName(_fromUtf8("widget_3"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.widget_3)
        self.horizontalLayout_2.setMargin(11)
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.accept = QtGui.QPushButton(self.widget_3)
        self.accept.setObjectName(_fromUtf8("accept"))
        self.horizontalLayout_2.addWidget(self.accept)
        self.verticalLayout_2.addWidget(self.widget_3)
        self.horizontalLayout.addWidget(self.widget_2)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.checkBox.setText(_translate("Dialog", "CheckBox", None))
        self.checkBox_2.setText(_translate("Dialog", "CheckBox", None))
        self.checkBox_3.setText(_translate("Dialog", "CheckBox", None))
        self.accept.setText(_translate("Dialog", "Accept", None))


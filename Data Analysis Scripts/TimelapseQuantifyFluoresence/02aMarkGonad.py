import sys
from tifffile import *
from timelapseFun import *
import pickle
import os
from PyQt4 import QtGui, QtCore
import numpy as np
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends import qt_compat
import glob
import pandas as pd
use_pyside = qt_compat.QT_API == qt_compat.QT_API_PYSIDE

########################################################################################################################

class GUI(QtGui.QWidget):
    
    def __init__(self):

        super(GUI, self).__init__()
        
        self.setWindowTitle( 'Region of Interest Marking' )
        self.side = 'L'
        self.lbltxt = '"wheel" press: change side, currently %s\n"i" or "u" press: change cell sides'
        self.seamCellNames = ['a','b','c','1','2','3','4','5','6','t']
        self.initUI()
        
    #-----------------------------------------------------------------------------------------------
    # INITIALIZATION OF THE WINDOW - DEFINE AND PLACE ALL THE WIDGETS
    #-----------------------------------------------------------------------------------------------

    def initUI(self):
        
        # SET THE GEOMETRY
        
        mainWindow = QtGui.QVBoxLayout()
        mainWindow.setSpacing(15)
        
        fileBox = QtGui.QHBoxLayout()
        spaceBox1 = QtGui.QHBoxLayout()
        rawDataBox = QtGui.QHBoxLayout()
        
        mainWindow.addLayout(fileBox)
        mainWindow.addLayout(spaceBox1)
        mainWindow.addLayout(rawDataBox)
        
        Col1 = QtGui.QGridLayout()
        Col2 = QtGui.QHBoxLayout()
        
        rawDataBox.addLayout(Col1)
        rawDataBox.addLayout(Col2)
        
        self.setLayout(mainWindow)

        # DEFINE ALL WIDGETS AND BUTTONS
        
        loadBtn = QtGui.QPushButton('Load DataSet')
        saveBtn = QtGui.QPushButton('Save data (F12)')
        
        tpLbl = QtGui.QLabel('Timepoint:')
        
        self.tp = QtGui.QSpinBox(self)
        self.tp.setValue(0)
        self.tp.setMaximum(100000)
        
        self._488nmBtn = QtGui.QRadioButton('488nm')
        self._561nmBtn = QtGui.QRadioButton('561nm')
        self.CoolLEDBtn = QtGui.QRadioButton('CoolLED')
        
        self.sld1 = QtGui.QSlider(QtCore.Qt.Vertical, self)
        self.sld1.setMaximum(2**16-1)
        self.sld1.setValue(0)
        self.sld2 = QtGui.QSlider(QtCore.Qt.Vertical, self)
        self.sld2.setMaximum(2**16)
        self.sld2.setValue(2**16-1)

        self.fig1 = Figure((8.0, 8.0), dpi=100)
        self.fig1.subplots_adjust(left=0., right=1., top=1., bottom=0.)
        self.ax1 = self.fig1.add_subplot(111)
        self.canvas1 = FigureCanvas(self.fig1)
        self.canvas1.setFocusPolicy( QtCore.Qt.ClickFocus )
        self.canvas1.setFocus()
        self.canvas1.setFixedSize(QtCore.QSize(900,900))
#        self.canvas1.setFixedSize(QtCore.QSize(1000,1000))

        self.canvas1.setSizePolicy( QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding )

        # PLACE ALL THE WIDGET ACCORDING TO THE GRIDS

        fileBox.addWidget(loadBtn)
        fileBox.addWidget(saveBtn)

        spaceBox1.addWidget(self.HLine())

        Col1.addWidget(tpLbl, 0, 0)#, 1, 1, Qt.AlignTop)
        Col1.addWidget(self.tp, 0, 1)#, 1, 1, Qt.AlignTop)
        Col1.addWidget(self._488nmBtn, 3, 0 )
        Col1.addWidget(self._561nmBtn, 4, 0 )
        Col1.addWidget(self.CoolLEDBtn, 5, 0 )
        
        Col2.addWidget(self.sld1)
        Col2.addWidget(self.sld2)
        Col2.addWidget(self.canvas1)
        
        self.setFocus()
        self.show()
        
        # BIND BUTTONS TO FUNCTIONS
        
        loadBtn.clicked.connect(self.selectWorm)
        saveBtn.clicked.connect(self.saveData)

        self.tp.valueChanged.connect(self.updateAllCanvas)
        self.sld1.valueChanged.connect(self.updateAllCanvas)
        self.sld2.valueChanged.connect(self.updateAllCanvas)

        self._488nmBtn.toggled.connect(self.radioClicked)
        self._561nmBtn.toggled.connect(self.radioClicked)
        self.CoolLEDBtn.toggled.connect(self.radioClicked)

        self.fig1.canvas.mpl_connect('button_press_event',self.onMouseClickOnCanvas1)        
        self.fig1.canvas.mpl_connect('scroll_event',self.wheelEvent)        
        
    #-----------------------------------------------------------------------------------------------
    # FORMATTING THE WINDOW
    #-----------------------------------------------------------------------------------------------

    def center(self):
        
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    def HLine(self):
        
        toto = QtGui.QFrame()
        toto.setFrameShape(QtGui.QFrame.HLine)
        toto.setFrameShadow(QtGui.QFrame.Sunken)
        return toto

    def VLine(self):
        
        toto = QtGui.QFrame()
        toto.setFrameShape(QtGui.QFrame.VLine)
        toto.setFrameShadow(QtGui.QFrame.Sunken)
        return toto

    def heightForWidth(self, width):
        
        return width
    
    #-----------------------------------------------------------------------------------------------
    # BUTTON FUNCTIONS
    #-----------------------------------------------------------------------------------------------

    def selectWorm(self):

        self.pathDial = QtGui.QFileDialog.getExistingDirectory(self, 'Select a folder', 'Y:\\Images')
        self.worm = self.pathDial.split("\\")[-1]
        self.path = self.pathDial[:-len(self.worm)]
        
        if not os.path.isfile(self.path+self.worm+'\\LEDmovie.tif'):
            QtGui.QMessageBox.about(self,'Warning!','There is no movie in this folder! Create a movie first!')
            return

        # print(path + worm + '\\z*.txt')
        self.channels = {}
        if os.path.isfile(self.path + self.worm + '\\488nmmovie.tif'):
            self.channels['488nm'] = loadstack(self.path + self.worm + '\\488nmmovie.tif')
        if os.path.isfile(self.path + self.worm + '\\561nmmovie.tif'):
            self.channels['561nm'] = loadstack(self.path + self.worm + '\\561nmmovie.tif')
        if os.path.isfile(self.path + self.worm + '\\LEDmovie.tif'):
            self.channels['CoolLED'] = loadstack(self.path + self.worm + '\\LEDmovieWithTime.tif')

        self.currentChannel = list(self.channels.keys())[0]
        self.tp.setMaximum(len(self.channels[self.currentChannel])-1)
        
        self.df = pickle.load( open(self.path + '\\worm' + self.worm.split('_')[0] + '.pickle','rb') )

        if 'gonadPos' not in list(self.df.keys()):
            self.df['gonadPos'] = np.nan
            self.df.gonadPos = self.df.gonadPos.astype(object)

        self.compression = self.df.ix[ self.df.rowtype == 'param', 'compression' ].values[0]
        self.hatchingtidx = int( np.abs( np.min( self.df.ix[ self.df.rowtype== 'body', 'tidx' ].values ) ) )

        self.tp.setValue( self.hatchingtidx )
        self.setWindowTitle('Body Length Analysis - ' + self.pathDial)

        # self.pathDial.show()
        self.updateAllCanvas()
        self.setFocus()

    def saveData(self):
        
        pickle.dump( self.df, open(self.path+'\\worm'+self.worm.split('_')[0]+'.pickle','wb'), protocol=2 )        
        
    def updateAllCanvas(self):
        self.updateRadioBtn()
        self.updateCanvas1()
        
    def radioClicked(self):
        if self._488nmBtn.isChecked():
            if '488nm' in self.channels.keys():
                self.currentChannel = '488nm'
            else:
                QtGui.QMessageBox.about(self, 'Warning', 'No 488nm channel!')
        elif self._561nmBtn.isChecked():
            if '561nm' in self.channels.keys():
                self.currentChannel = '561nm'
            else:
                QtGui.QMessageBox.about(self, 'Warning', 'No 561nm channel!')
        elif self.CoolLEDBtn.isChecked():
            if 'CoolLED' in self.channels.keys():
                self.currentChannel = 'CoolLED'
            else:
                QtGui.QMessageBox.about(self, 'Warning', 'No CoolLED channel!')
        self.setBCslidersMinMax()
        self.resetBC()
        self.setFocus()
        self.updateAllCanvas()

    #-----------------------------------------------------------------------------------------------
    # DEFAULT FUNCTION FOR KEY AND MOUSE PRESS ON WINDOW
    #-----------------------------------------------------------------------------------------------

    def wheelEvent(self,event):
        if self.canvas1.underMouse():
            step = event.step
        else:          
            step = event.delta()/abs(event.delta())
        self.tp.setValue( self.tp.value() + step) 

    #-----------------------------------------------------------------------------------------------
    # ADDITIONAL FUNCTIONS FOR KEY AND MOUSE PRESS ON CANVASES
    #-----------------------------------------------------------------------------------------------

    def onMouseClickOnCanvas1(self, event):
        
        # print(event.button,event.xdata,event.ydata)
        
        tp = self.tp.value()
        
        x = event.xdata
        y = event.ydata

        if event.button == 1:

            # left button: add a point to the outline
            gonadPos = np.array( [ x, y ] ) * self.compression

        if event.button == 3:

            gonadPos = np.nan

        # update the dataframe with the new gonadPos
        self.df.gonadPos.values[list(self.df.tidx == (tp - self.hatchingtidx)).index(True)] = gonadPos
        self.updateCanvas1()
        self.setFocus()

    #-----------------------------------------------------------------------------------------------
    # UTILS
    #-----------------------------------------------------------------------------------------------

    def updateRadioBtn(self):
        if self.currentChannel == '488nm':
            self._488nmBtn.setChecked(True)
        elif self.currentChannel == '561nm':
            self._561nmBtn.setChecked(True)
        elif self.currentChannel == 'CoolLED':
            self.CoolLEDBtn.setChecked(True)
        self.setFocus()

    def setBCslidersMinMax(self):
        self.sld1.setMaximum(np.max(self.channels[self.currentChannel]))
        self.sld1.setMinimum(np.min(self.channels[self.currentChannel]))
        self.sld2.setMaximum(np.max(self.channels[self.currentChannel]))
        self.sld2.setMinimum(np.min(self.channels[self.currentChannel]))

    def resetBC(self):
        self.sld1.setValue(np.min(self.channels[self.currentChannel]))
        self.sld2.setValue(np.max(self.channels[self.currentChannel]))
        
    def updateCanvas1(self):
        
        rowmask = self.df.rowtype == 'body'
        
        # plot the image
        self.ax1.cla()
        imgplot = self.ax1.imshow(self.channels[self.currentChannel][self.tp.value()], cmap = 'gray')
        
        # remove the white borders and plot outline and spline
        self.ax1.autoscale(False)
        self.ax1.axis('Off')
        self.fig1.subplots_adjust(left=0., right=1., top=1., bottom=0.)

        # change brightness and contrast
        self.sld1.setValue(np.min([self.sld1.value(),self.sld2.value()]))
        self.sld2.setValue(np.max([self.sld1.value(),self.sld2.value()]))
        imgplot.set_clim(self.sld1.value(), self.sld2.value())  

        # print gonad position
        gonadPos = self.df.ix[self.df.tidx == (self.tp.value()-self.hatchingtidx),'gonadPos'].values[0] / self.compression
        if len( gonadPos.shape ) > 0:
            self.ax1.plot( gonadPos[0], gonadPos[1], 'o', color='red', ms=10, mew=0, alpha=.5, lw = 0 )      

        # redraw the canvas
        self.canvas1.draw()
        self.setFocus()
        
########################################################################################################################
        
if __name__ == '__main__':
    
    app = QtGui.QApplication.instance() # checks if QApplication already exists 
    if not app: # create QApplication if it doesnt exist 
        app = QtGui.QApplication(sys.argv)
    
    gui = GUI()
    app.setStyle("plastique")
    # app.installEventFilter(gui)
    sys.exit(app.exec_())
    



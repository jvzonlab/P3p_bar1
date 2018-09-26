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
        self.setWindowTitle( 'Label Cells' )
#        self.seamCellNames = ['a','b','1','2','3','4']
        self.seamCellNames = ['a','b','1','2','3','4', '5']
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
        Col3 = QtGui.QVBoxLayout()
        
        rawDataBox.addLayout(Col1)
        rawDataBox.addLayout(Col2)
        rawDataBox.addLayout(Col3)
        
        self.setLayout(mainWindow)

        # DEFINE ALL WIDGETS AND BUTTONS
        
        loadBtn = QtGui.QPushButton('Load DataSet')
        saveBtn = QtGui.QPushButton('Save data (F12)')
        
        tpLbl = QtGui.QLabel('Timepoint:')
        slLbl = QtGui.QLabel('Slice:')
        
        self.tp = QtGui.QSpinBox(self)
        self.tp.setValue(0)
        self.tp.setMaximum(100000)

        self.sl = QtGui.QSpinBox(self)
        self.sl.setValue(0)
        self.sl.setMaximum(100000)
        
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
        self.canvas1.setFixedSize(QtCore.QSize(600,600))
        self.canvas1.setSizePolicy( QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding )

        self.cellTbl = QtGui.QTableWidget()

        self.fig2 = Figure((4.0, 4.0), dpi=100)
        self.fig2.subplots_adjust(left=0., right=1., top=1., bottom=0.)
        self.ax2 = self.fig2.add_subplot(111)
        self.canvas2 = FigureCanvas(self.fig2)
        self.canvas2.setFixedSize(QtCore.QSize(300,300))
        self.canvas2.setSizePolicy( QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding )

        # PLACE ALL THE WIDGET ACCORDING TO THE GRIDS

        fileBox.addWidget(loadBtn)
        fileBox.addWidget(saveBtn)

        spaceBox1.addWidget(self.HLine())

        Col1.addWidget(tpLbl, 0, 0)#, 1, 1, Qt.AlignTop)
        Col1.addWidget(self.tp, 0, 1)#, 1, 1, Qt.AlignTop)
        Col1.addWidget(slLbl, 1, 0)#, 1, 1, Qt.AlignTop)
        Col1.addWidget(self.sl, 1, 1)#, 1, 1, Qt.AlignTop)
        Col1.addWidget(self._488nmBtn, 3, 0 )
        Col1.addWidget(self._561nmBtn, 4, 0 )
        Col1.addWidget(self.CoolLEDBtn, 5, 0 )
        
        Col2.addWidget(self.sld1)
        Col2.addWidget(self.sld2)
        Col2.addWidget(self.canvas1)

        Col3.addWidget(self.cellTbl)
        Col3.addWidget(self.canvas2)
        
        self.setFocus()
        self.show()
        
        # BIND BUTTONS TO FUNCTIONS
        
        loadBtn.clicked.connect(self.selectWorm)
        saveBtn.clicked.connect(self.saveData)

        self.tp.valueChanged.connect(self.loadNewStack)
        self.sl.valueChanged.connect(self.updateAllCanvas)
        self.sld1.valueChanged.connect(self.updateAllCanvas)
        self.sld2.valueChanged.connect(self.updateAllCanvas)

        self._488nmBtn.toggled.connect(self.radioClicked)
        self._561nmBtn.toggled.connect(self.radioClicked)
        self.CoolLEDBtn.toggled.connect(self.radioClicked)

        self.fig1.canvas.mpl_connect('button_press_event',self.onMouseClickOnCanvas1)        
        self.fig1.canvas.mpl_connect('scroll_event',self.wheelEvent)        
        # self.connect(mainWindow, SIGNAL("tabPressed"),self.keyPressEvent)        
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

        # load the dataframe file
        self.df = pickle.load( open(self.path + '\\worm' + self.worm.split('_')[0] + '.pickle','rb') )
        if not( 'cXoutline' in self.df.keys().values ):
            self.df['cXoutline'] = np.nan
            self.df['cYoutline'] = np.nan
            self.df.cXoutline = self.df.cXoutline.astype(object)
            self.df.cYoutline = self.df.cYoutline.astype(object)
            for i in np.arange(1,len(self.df.cXoutline.values)):    
                self.df.cXoutline.values[i] = np.array([np.nan])
                self.df.cYoutline.values[i] = np.array([np.nan])

        self.compression = self.df.ix[ self.df.rowtype == 'param', 'compression' ].values[0]
        self.hatchingtidx = int( np.abs( np.min( self.df.ix[ self.df.rowtype== 'body', 'tidx' ].values ) ) )

        self.tp.setValue( 0 )
        self.setWindowTitle('Mark Cells - ' + self.pathDial)

        # detect available channels
        self.channels = []
        chns = ['488nm','561nm','CoolLED']
        for c in chns:
            flist = glob.glob(self.path + self.worm + '\\z*'+c+'.tif')
            if len(flist)>0:
                self.channels.append(c)
        self.currentChannel = '488nm'

        self.currentCell = ''

        # read in all the metadata files
        self.fMetaList = glob.glob(self.path + self.worm + '\\z*.txt')

        self.tp.setMaximum(1000)
        
        self.loadNewStack()

        # self.pathDial.show()
        self.updateAllCanvas()
        self.setFocus()

    def loadNewStack(self):
        
        # print(self.fList['gfp'][self.tp.value()])
        
        self.stacks = {}
        for ch in self.channels:
            filename = self.path+self.worm+'\\z%.3d_%s.tif'%(self.tp.value()+self.hatchingtidx+1,ch)
            if os.path.isfile(filename):
                self.stacks[ch] = loadstack(filename)

        if len( self.stacks.keys() ) > 0:
            # print(self.stacks.keys(), self.stacksStraight)
            self.sl.setMaximum(self.stacks[self.currentChannel].shape[0]-1)

            self.setBCslidersMinMax()
        
        tpmask = self.df.tidx == self.tp.value()
        cellmask = self.df.rowtype == 'cell'

        cnames = list( self.df.ix[tpmask&cellmask,'cname'].values )
        cZpos = list( self.df.ix[tpmask&cellmask,'cZpos'].values )

        print('labeled cells: ' + str(cnames) ) 
        if len( cnames ) > 0:
            self.currentCell = cnames[0]
            self.sl.setValue(cZpos[0])
        else:
            self.currentCell = ''

        # self.updateTable()
        self.updateAllCanvas()

    def saveData(self):
        
        pickle.dump( self.df, open(self.path+'\\worm'+self.worm.split('_')[0]+'.pickle','wb'), protocol=2 )        
        self.setFocus()
        
    def updateAllCanvas(self):
        self.updateRadioBtn()
        self.updateCanvas1()
        self.updateCanvas2()
        
    def radioClicked(self):
        if self._488nmBtn.isChecked():
            if '488nm' in self.channels:
                self.currentChannel = '488nm'
            else:
                QtGui.QMessageBox.about(self, 'Warning', 'No 488nm channel!')
        elif self._561nmBtn.isChecked():
            if '561nm' in self.channels:
                self.currentChannel = '561nm'
            else:
                QtGui.QMessageBox.about(self, 'Warning', 'No 561nm channel!')
        elif self.CoolLEDBtn.isChecked():
            if 'CoolLED' in self.channels:
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

    def keyPressEvent(self, event):
        
        # print(event.key())

        # change timepoint
        if event.key() == QtCore.Qt.Key_Right:
            self.changeSpaceTime( self.tp, +1 )

        elif event.key() == QtCore.Qt.Key_Left:
            self.changeSpaceTime( self.tp, -1 )

        # change slice
        elif event.key() == QtCore.Qt.Key_Up:
            self.changeSpaceTime( self.sl, +1 )
            
        elif event.key() == QtCore.Qt.Key_Down:
            self.changeSpaceTime( self.sl, -1 )

        elif event.key() == QtCore.Qt.Key_Space:
            tpmask = self.df.tidx == self.tp.value()
            cellmask = self.df.rowtype == 'cell'

            cnames = list(self.df.ix[tpmask&cellmask,'cname'].values)
            cZpos = list(self.df.ix[tpmask&cellmask,'cZpos'].values)

            idx = np.mod( cnames.index(self.currentCell)+1, len(cnames) )
            if len( cnames ) > 0:
                self.currentCell = cnames[idx]
                self.sl.setValue(cZpos[idx])
            else:
                self.currentCell = ''
            self.updateAllCanvas()

        self.setFocus()

    def wheelEvent(self,event):
        if self.canvas1.underMouse():
            step = event.step
        else:          
            step = event.delta()/abs(event.delta())
        self.sl.setValue( self.sl.value() + step) 

    #-----------------------------------------------------------------------------------------------
    # ADDITIONAL FUNCTIONS FOR KEY AND MOUSE PRESS ON CANVASES
    #-----------------------------------------------------------------------------------------------

    def onMouseClickOnCanvas1(self, event):

        pos = np.array( [ int(event.xdata), int(event.ydata), int(self.sl.value()) ] )  

        cellmask = self.df['cname'] == self.currentCell
        tpmask = self.df['tidx'] == self.tp.value()
        Xoutline = self.df.ix[ tpmask & cellmask, 'cXoutline'].values[0]
        Youtline = self.df.ix[ tpmask & cellmask, 'cYoutline'].values[0]

        if event.button == 1:

            # create an empty cell: the only entries are tidx, times, xyzpos, side
            Xoutline = np.append(Xoutline,pos[0])
            Youtline = np.append(Youtline,pos[1])

            # if the first line is still full of nan, remove it
            if np.isnan(Xoutline[0]):
                Xoutline = Xoutline[1:]
            if np.isnan(Youtline[0]):
                Youtline = Youtline[1:]

        elif event.button == 3:
            Xoutline = Xoutline[:-1]
            Youtline = Youtline[:-1]

        index = self.df.ix[tpmask&cellmask].index[0]
        self.df.cXoutline.values[index] = Xoutline
        self.df.cYoutline.values[index] = Youtline
        self.df = self.df.sort(['tidx','rowtype','cZpos']).reset_index(drop=True)

        self.updateCanvas1()
        self.setFocus()
        # print(event.button,event.xdata,event.ydata)

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
        self.sld1.setMaximum(np.max(self.stacks[self.currentChannel]))
        self.sld1.setMinimum(np.min(self.stacks[self.currentChannel]))
        self.sld2.setMaximum(np.max(self.stacks[self.currentChannel]))
        self.sld2.setMinimum(np.min(self.stacks[self.currentChannel]))

    def resetBC(self):
        self.sld1.setValue(np.min(self.stacks[self.currentChannel]))
        self.sld2.setValue(np.max(self.stacks[self.currentChannel]))
        
    def updateCanvas1(self):

        if ( len( self.stacks.keys() ) == 0 ) or ( self.currentCell == '' ):
            self.fig1.clf()
            self.fig1.subplots_adjust(left=0., right=1., top=1., bottom=0.)
            self.ax1 = self.fig1.add_subplot(111)
            self.canvas1.draw()
            return

        # extract current cell data
        tpmask = self.df.tidx == self.tp.value()
        currentcellmask = self.df.cname == self.currentCell
        cData = self.df.ix[tpmask&currentcellmask]

        # plot the image
        self.ax1.cla()
        imgplot = self.ax1.imshow(self.stacks[self.currentChannel][self.sl.value(),cData.cYpos-50:cData.cYpos+51,cData.cXpos-50:cData.cXpos+51], cmap = 'gray', interpolation = 'nearest')
        
        # remove the white borders and plot outline and spline
        self.ax1.autoscale(False)
        self.ax1.axis('Off')
        self.fig1.subplots_adjust(left=0., right=1., top=1., bottom=0.)

        # print cell name
        if cData.cZpos.values[0] == self.sl.value():
            self.ax1.text( 50, 60, self.currentCell, color='yellow', size='small', alpha=.8,
                    rotation=90, fontsize = 20)
            self.ax1.plot( 50, 50, 'x', color='yellow', alpha = .8, ms = 10 )

        # # draw outline
        Xoutline = self.df.ix[tpmask&currentcellmask,'cXoutline'].values[0]
        if len(Xoutline) > 1:
            Xoutline = np.append(Xoutline, Xoutline[0])
        Youtline = self.df.ix[tpmask&currentcellmask,'cYoutline'].values[0]
        if len(Youtline) > 1:
            Youtline = np.append(Youtline, Youtline[0])
        self.ax1.plot( Xoutline, Youtline, '-x', color='yellow', ms=5, alpha=1., lw = .5 )      

        # change brightness and contrast
        self.sld1.setValue(np.min([self.sld1.value(),self.sld2.value()]))
        self.sld2.setValue(np.max([self.sld1.value(),self.sld2.value()]))
        imgplot.set_clim(self.sld1.value(), self.sld2.value())  

        # redraw the canvas
        self.canvas1.draw()
        self.setFocus()

    def updateCanvas2(self):
        
        # plot the image
        self.ax2.cla()
        imgplot = self.ax2.imshow(self.stacks[self.currentChannel][self.sl.value()], cmap = 'gray')
        
        # remove the white borders and plot outline and spline
        self.ax2.autoscale(False)
        self.ax2.axis('Off')
        self.fig2.subplots_adjust(left=0., right=1., top=1., bottom=0.)

        # cell text on the image
        tpmask = self.df['tidx'] == self.tp.value()
        cellmask = self.df['rowtype'] == 'cell'

        for idx, cell in self.df[tpmask & cellmask].iterrows():

            if cell.cZpos == self.sl.value():
                clabel = str(cell.cname)
                color = 'red'
                if clabel == self.currentCell:
                    color = 'yellow'
                self.ax2.text( cell.cXpos, cell.cYpos + 10, clabel, color=color, size='small', alpha=.8,
                        rotation=90)
                self.ax2.plot( cell.cXpos, cell.cYpos, 'x', color=color, alpha = .8 )


        # redraw the canvas
        self.canvas2.draw()
        self.setFocus()

    def changeSpaceTime(self, whatToChange, increment):

        whatToChange.setValue( whatToChange.value() + increment )

########################################################################################################################

if __name__ == '__main__':
    
    app = QtGui.QApplication.instance() # checks if QApplication already exists 
    if not app: # create QApplication if it doesnt exist 
        app = QtGui.QApplication(sys.argv)    
    gui = GUI()
    app.setStyle("plastique")
    # app.installEventFilter(gui)
    sys.exit(app.exec_())
    



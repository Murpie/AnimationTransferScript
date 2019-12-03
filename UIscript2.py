from maya import OpenMayaUI as omui
import PySide2
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtUiTools import *
from PySide2.QtWidgets import *
from shiboken2 import wrapInstance
from finalTransferAnimation3NEW import *

sJoints = []
tJoints = []


def getMayaWin():
	mayaWinPtr = omui.MQtUtil.mainWindow( )
	mayaWin = wrapInstance( long( mayaWinPtr ), QWidget )


def loadUI( path ):
	loader = QUiLoader()
	uiFile = QFile( path )

	dirIconShapes = ""
	buff = None

	if uiFile.exists():
		dirIconShapes = path
		uiFile.open( QFile.ReadOnly )

		buff = QByteArray( uiFile.readAll() )
		uiFile.close()
	else:
		print "UI file missing! Exiting..."
		exit(-1)

	fixXML( path, buff )
	qbuff = QBuffer()
	qbuff.open( QBuffer.ReadOnly | QBuffer.WriteOnly )
	qbuff.write( buff )
	qbuff.seek( 0 )
	ui = loader.load( qbuff, parentWidget = getMayaWin() )
	ui.path = path

	return ui


def fixXML( path, qbyteArray ):
	if path[-1] != '/':
		path += '/'
	path = path.replace( "/", "\\" )

	tempArr = QByteArray( "<pixmap>" + path + "\\" )

	lastPos = qbyteArray.indexOf( "<pixmap>", 0 )
	while lastPos != -1:
		qbyteArray.replace( lastPos, len( "<pixmap>" ), tempArr )
		lastPos = qbyteArray.indexOf( "<pixmap>", lastPos + 1 )
	return


class UIController:
    def __init__( self, ui ):
    	sJoints = []
    	tJoints = []
    	selectionR = pm.ls(sl = True)
    	selIndex = 0
    	for sel in selectionR:
    	    selIndex += 1
    	if selIndex == 2:
    	    sJoints, tJoints = fixBeforeTransfer()

        self.ResetButton(sJoints, tJoints)
        ui.FindSkeleton.clicked.connect( self.findRoots )  
    	ui.SourceUp.clicked.connect( self.sUpButtonPress )
    	ui.SourceDown.clicked.connect( self.sDownButtonPress )
    	ui.SourceDelete.clicked.connect( self.sDeleteButtonPress )
        ui.TargetUp.clicked.connect( self.tUpButtonPress )
    	ui.TargetDown.clicked.connect( self.tDownButtonPress )
    	ui.TargetDelete.clicked.connect( self.tDeleteButtonPress )
    	ui.buttonBox.clicked.connect( self.ButtonClicked )
        ui.buttonBox.rejected.connect( self.CancelButtonPress )
    	self.ui = ui
    	ui.setWindowFlags( Qt.WindowStaysOnTopHint )
    	ui.show()
		
		
    def ResetButton(self, sJoints, tJoints):
        ui.SourceJoints.clear()
        ui.TargetJoints.clear()
        for bone in sJoints:
            newItem = QListWidgetItem()
            newItem.setText(str(bone))
            ui.SourceJoints.insertItem(ui.SourceJoints.count(), newItem)
        print "Sources Done"
        for bone in tJoints:
            newItem = QListWidgetItem()
            newItem.setText(str(bone))
            ui.TargetJoints.insertItem(ui.TargetJoints.count(), newItem)
        print "Target Done"
        del sJoints[:]
        del tJoints[:]
        
    def findRoots(self):
        sJoints = []
    	tJoints = []
        sRootText = ui.sRoot.text()
        tRootText = ui.tRoot.text()
        pm.select( sRootText, r=True )
        pm.select( tRootText, add=True )
        sJoints, tJoints = fixBeforeTransfer()
        self.ResetButton(sJoints, tJoints)
            
    def sUpButtonPress(self):
        temp = ui.SourceJoints.currentRow()
        tempJoint = ui.SourceJoints.takeItem(temp)
        ui.SourceJoints.insertItem(temp-1, tempJoint)
        ui.SourceJoints.setCurrentRow(temp-1)
        
    def sDownButtonPress(self):
        temp = ui.SourceJoints.currentRow()
        tempJoint = ui.SourceJoints.takeItem(temp)
        ui.SourceJoints.insertItem(temp+1, tempJoint)
        ui.SourceJoints.setCurrentRow(temp+1)
	
    def sDeleteButtonPress(self):
        temp = ui.SourceJoints.currentRow()
        tempJoint = ui.SourceJoints.takeItem(temp)
    
    def tUpButtonPress(self):
        temp = ui.TargetJoints.currentRow()
        tempJoint = ui.TargetJoints.takeItem(temp)
        ui.TargetJoints.insertItem(temp-1, tempJoint)
        ui.TargetJoints.setCurrentRow(temp-1)
        
    def tDownButtonPress(self):
        temp = ui.TargetJoints.currentRow()
        tempJoint = ui.TargetJoints.takeItem(temp)
        ui.TargetJoints.insertItem(temp+1, tempJoint)
        ui.TargetJoints.setCurrentRow(temp+1)
	
    def tDeleteButtonPress(self):
        temp = ui.TargetJoints.currentRow()
        tempJoint = ui.TargetJoints.takeItem(temp)


        
    def ButtonClicked( self ):
        
        sJointList = []
        tJointList = []
        for i in range(ui.SourceJoints.count()):
            sJointList.append(ui.SourceJoints.item(i).text())
        for i in range(ui.TargetJoints.count()):
            tJointList.append(ui.TargetJoints.item(i).text())
    	    
    	transferAnimation(int(ui.lineEdit.text()), int(ui.lineEdit_2.text()), sJointList, tJointList)
            
    def CancelButtonPress( self ):
        ui.close()

ui = loadUI("C:\Users\Leon\Documents\maya\scripts\example.ui")
gui = UIController(ui)
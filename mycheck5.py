# -*- coding: UTF-8 -*-
__version__ = 0.99

import os, time, shutil, re, sys, subprocess, inspect, filecmp
from os.path import dirname
from glob import glob
import urllib
import maya.OpenMayaUI as apiUI
import random
import maya.cmds as mc
import maya.mel as mel





#from PySide import QtGui, QtCore
try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide import QtCore, QtGui
    QtWidgets = QtGui


try:
    import pysideuic
    from shiboken import wrapInstance
except ImportError:
    import pyside2uic as pysideuic
    from shiboken2 import wrapInstance    
    
import xml.etree.ElementTree as ET
from cStringIO import StringIO
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')


MAYA_APP_DIR = os.path.abspath(os.environ['ONION_APP_ROOT']).decode("gb2312")#os.path.dirname(os.path.realpath(__file__))#os.environ['ONION_APP_ROOT']#
#MAYA_FILES_DIR=os.environ['ONION_FILES_ROOT']
                    #os.path.dirname("Z:\\scripts\\Storage\\")#\\\\server\\Share


def loadUiType(uiFile):
    """
    Pyside lacks the "loadUiType" command, so we have to convert the ui file to py code in-memory first
    and then execute it in a special frame to retrieve the form_class.
    """
    parsed = ET.parse(uiFile)
    widget_class = parsed.find('widget').get('class')
    form_class = parsed.find('class').text
    with open(uiFile, 'r') as f:
        o = StringIO()
        frame = {}
        pysideuic.compileUi(f, o, indent=0)
        pyc = compile(o.getvalue(), '<string>', 'exec')
        exec pyc in frame
        form_class = frame['Ui_%s' % form_class]
        base_class = getattr(QtWidgets, widget_class) #eval('QtGui.%s' % widget_class)
    return (form_class, base_class)


def getMayaWindow():
    """
    Get the main Maya window as a QtGui.QMainWindow instance
    @return: QtGui.QMainWindow instance of the top level Maya windows
    from Nathan Horne
    """
    
    ptr = apiUI.MQtUtil.mainWindow()
    if ptr is not None:
        return wrapInstance(long(ptr), QtWidgets.QWidget)


def maya_api_version():
    return int(mc.about(api=True))


def ui_PublishWindow(ifcreate=True,path='',fileInput=''):
    
    global uip
    try:
	uip.close()
    except:
	pass	
    

    uip = PublishWindow(parent=None,create=ifcreate, save=True, sel=False, version=None,pathDir=path,fileName=fileInput)
    uip.show()
    uip.move(200,200)  
    



def ui_snapshot(item, secondary = False, toolButton = False):
    """
    """
    global ui_s
    try:
        ui_s.close()
    except:
        pass
    
    ui_s = SnapWindow(parent=getMayaWindow(),update=[item, secondary, toolButton], root=os.path.dirname(os.path.realpath(__file__)) + '/ui')
    ui_s.run()
    ui_s.move (300,200) 
    
    #getattr(uip,"raise")()
    #uip.activateWindow()
    

    



snap_form, snap_base = loadUiType(os.path.dirname(os.path.realpath(__file__)) + '/ui/st_assets_snap.ui')
create_form, create_base = loadUiType(os.path.dirname(os.path.realpath(__file__)) + '/ui/st_assets_create.ui')





def toQtObject(mayaName):
    """
    Convert a Maya ui path to a Qt object
    @param mayaName: Maya UI Path to convert (Ex: "scriptEditorPanel1Window|TearOffPane|scriptEditorPanel1|testButton" )
    @return: PyQt representation of that object
    from Nathan Horne
    """
    ptr = apiUI.MQtUtil.findControl(mayaName)
    if ptr is None:
        ptr = apiUI.MQtUtil.findLayout(mayaName)
    if ptr is None:
        ptr = apiUI.MQtUtil.findMenuItem(mayaName)
    if ptr is not None:
        return wrapInstance(long(ptr), QtWidgets.QWidget)


def listWidget_item_create_icon(items, file):
    """
    items = list of QWidget to add QIcon to.
    file = image file for QIcon(QPixmap)
    <return> = QIcon object
    """
    pixmap = QtGui.QPixmap(file)
    bmpmap = QtGui.QBitmap(pixmap)
    scaled = pixmap.transformed(QtGui.QTransform().scale(0.2, 0.2))
    icon = QtGui.QIcon()
    icon.addPixmap(pixmap)
    for i in items:
        i.pixmapFile = file
        i.pixmapWidget = pixmap
        i.iconWidget = icon
        i.setIcon(icon)

    return icon









class PublishWindow(create_form, create_base):
    """
    """

    def __init__(self, parent, create = True, save = True, sel = True, version=__version__, pathDir='',fileName=''):
        super(PublishWindow, self).__init__(parent)
	#self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        
	
        self.setupUi(self)
        self.create = create
        self.save = save
        self.sel = sel
        self.mode = 'Create'
        self.currentVersion = __version__
	self.pathDir=pathDir
	self.fileName=fileName
	#self.raise_()
        if self.save:
            self.mode = 'Create from Current Scene'
        elif self.sel:
            self.mode = 'Create from Selection'
        self.root = os.path.dirname(os.path.realpath(__file__)) + '/ui/'
        self.sectionWidget =  w.newComboBox
        self.optvar_mayaType = 'st_assets_manager_mayaFileType'
        #self.projects_init(self.p_comboBox, w.newComboBox)
        self.projects_init(self.s_comboBox, w.newComboBox)
	#self.projects_init(self.ss_comboBox, w.newComboBox)
    #    self.sections_init(self.s_comboBox, 'self.sectionWidget')
     #   self.sections_init(self.ss_comboBox, 'self.sectionWidget.currentWidget()')
        if not self.create:
            self.mode = 'Publish'#修改
       #     self.current = self.sectionWidget.currentWidget().currentWidget().currentItem()
       #     self.checkBox.setHidden(True)

	#    self.checkBox.setEnabled(True)
	    self.s_comboBox.setEnabled(True)
	    #self.ss_comboBox.setEnabled(True)
	    self.lineEdit.setText(self.fileName)
	    self.lineEdit.setEnabled(True)
	    #self.d_plainTextEdit.setPlainText(u'车辆信息：')
	    #self.n_plainTextEdit.setPlainText(u'零件信息：')
	    name = os.path.splitext(self.fileName)[0]	    
	    path=os.path.join(self.pathDir,name)
	    screenshot=os.path.join(self.pathDir,name+".jpg")
	    if not os.path.isfile(screenshot):
		screenshot = os.path.join(MAYA_APP_DIR, "ui\\AM_unknown.jpg")
	    shutil.copy2(screenshot,os.path.join(MAYA_APP_DIR,"ui\\Temp.jpg"))
	    icon=QtGui.QIcon(screenshot)
	    if os.path.isfile(os.path.join(self.pathDir, self.fileName+'.inf')):
		tree=ET.parse(os.path.join(self.pathDir, self.fileName+'.inf'))
		
		root=tree.getroot()
		desc=root.find('des').text
		self.d_plainTextEdit.setPlainText(desc)
		note=root.find('nop').text
		self.n_plainTextEdit.setPlainText(note)
		ty=root.find('type').text
		self.typenum=0
		for i in range(0,self.s_comboBox.count(),1):
		    if cmp(self.s_comboBox.itemText(i),ty)==0:
			self.typenum=i
		
			

		#self.ss_comboBox.setCurrentIndex(self.typenum)
		self.s_comboBox.setCurrentIndex(self.typenum)
	    """
	    for node in root.iter('des'):
		#print node.tag+node.attrib
		if node.name is 'des':
		    self.d_plainTextEdit.setPlainText(str(nod.attrib))
	    for node1 in root.iter('nop'):
		strAtt1=node1.attrib
		if node.name is 'nop':
		    self.n_plainTextEdit.setPlainText(str(nod.attrib))	 
	    """
	    
	   
		
            self.toolButton.setIcon(icon)
	    self.pushButton.setText(u'Update')
        else:
      #      self.current = self.sectionWidget.currentWidget().currentWidget()
            self.lineEdit.setFocus()
	    screenshot = os.path.join(MAYA_APP_DIR, "ui\\AM_unknown.jpg")
	    icon=QtGui.QIcon(screenshot)
	    self.s_comboBox.setEnabled(True)
		
            self.toolButton.setIcon(icon)	
	    self.pushButton.setText(u'Create')
	    shutil.copy2(screenshot,os.path.join(MAYA_APP_DIR,"ui\\Temp.jpg"))
	    
	    
	    
	    
	    
     #   self.t_checkBox.setCheckState(setPySideCheckState(int(self.current.snap[1])))
     #   self.r_checkBox.setCheckState(setPySideCheckState(int(self.current.snap[4])))
     #   self.s_checkBox.setCheckState(setPySideCheckState(int(self.current.snap[7])))
        self.label_init()
        self.toolButton.imageFile = 'No Image'
        #self.s_comboBox.activated.connect(lambda : self.sections_activated(self.s_comboBox, self.sectionWidget))
   #     self.ss_comboBox.activated.connect(lambda : self.sections_activated(self.ss_comboBox, self.sectionWidget.currentWidget(), init=False))
        self.toolButton.clicked.connect(lambda : ui_snapshot(False, toolButton=self.toolButton))
        self.pushButton.clicked.connect(self.savefile)
	
    def snapwindowshow(self,item, secondary = False, toolButton = False):
	"""
	"""
	global ui_s
	try:
	    ui_s.close()
	except:
	    pass
    
	ui_s = SnapWindow(parent=getMayaWindow(),update=[item, secondary, toolButton], root=os.path.dirname(os.path.realpath(__file__)) + '/ui')
	ui_s.run()
	ui_s.move (200,200) 
	#self.setWindowFlags(QtCore.Qt.Popup)
	#self.raise_()
	
	
	
	#self.setWindowFlags(QtCore.Qt.Popup)
	#self.setWindowFlags(QtCore.Qt.Popup)    
	self.setWindowFlags(QtCore.Qt.WindowActive)    
    
    
    
    
    
    
    
    


    def savefile(self):
	name = self.lineEdit.text()
	if name == "":
            logger.warning("Please enter a name for your asset")
	    return
	else:
	    if w.doesItExist(name):
		# OVERWRITE DIALOG
		response = mc.confirmDialog(
		    title=u'Override...',
		    message=u'Already have, Do you want to override?',
		    button=[u'Yes',u'No'],
		    defaultButton=u'No',
		    cancelButton=u'No',
		    dismissString=u'No')
		
		if response == u"No":
		    # 将创建窗口再次呼出到最靠前
		    getattr(uip,"raise")()
		    uip.activateWindow()		    
		    return


	    #### SAVE HERE
	    currentScene = mc.file(query=True, sceneName=True)

	    savePath = os.path.join(self.pathDir, '%s.ma' % name)
	    mc.file(rename=savePath)

	    if mc.ls(selection=True):
		mc.file(force=True, type='mayaAscii', exportSelected=True)
	    else:
		mc.file(force=True, save=True, type='mayaAscii')

	    mc.file(rename=currentScene) # restore previous scene name

	    # SAVE SCREENSHOT
	    if not self.create:
		if cmp(self.fileName,self.lineEdit.text())!=0:
		    shutil.copy2(os.path.join(self.pathDir,self.fileName+'.ma'),os.path.join(self.pathDir,self.lineEdit.text()+'.ma'))
		if os.path.isfile(os.path.join(self.pathDir,self.fileName+'.jpg')):
		    os.remove(os.path.join(self.pathDir,self.fileName+'.jpg'))
		if os.path.isfile(os.path.join(self.pathDir,self.fileName+'.ma')):
		    if cmp(self.fileName,self.lineEdit.text())!=0:
			os.remove(os.path.join(self.pathDir,self.fileName+'.ma'))
	    self.MakeXML(self.lineEdit.text())
	    self.saveScreenPic(self.lineEdit.text())#存在os.path.join(MAYA_APP_DIR,"Temp.jpg")里面
	    
	    
	    
	    logger.info("Asset saved in " + savePath)
	    File=self.pathDir.decode("utf-8").encode("gb2312")
	    w.populate(File)
	    self.close()
    
    def saveScreenPic(self, name):
	path = os.path.join(self.pathDir, '%s.jpg' % name)
	#if cmp(name,self.fileName)!=0:
	shutil.copy2(os.path.join(MAYA_APP_DIR,"ui\\Temp.jpg"), path)
	
    
    def MakeXML(self, name): 
	if not self.create:
	    #shutil.copy2(os.path.join(self.pathDir,self.fileName+'.inf'),os.path.join(self.pathDir,name+'.inf'))
	    if os.path.isfile(os.path.join(self.pathDir,self.fileName+'.inf')):
		os.remove(os.path.join(self.pathDir,self.fileName+'.inf'))
	    
	
	
	root=ET.Element('root', {'name':name})

	son1=ET.SubElement(root, 'type')
	son1.text=self.s_comboBox.currentText()
	son2=ET.SubElement(root, 'des')
	son2.text=self.d_plainTextEdit.toPlainText()
	son3=ET.SubElement(root, 'nop')
	son3.text=self.n_plainTextEdit.toPlainText()
	tree=ET.ElementTree(root)
	tree.write(os.path.join(self.pathDir,name+'.inf'),encoding="utf-8")
	
    
    

    def label_init(self):
        """
        """
        label = self.s_comboBox.currentText()
        if self.sel:
            label = self.s_comboBox.currentText() + ' from selection'
        if not self.create:
            label = 'abc'#self.current.text()
        self.title = self.setWindowTitle(self.mode + ' ' + label)
    #    self.pushButton.setText(self.mode + ' ' + label)

    def projects_init(self, comboBox, source):
        """
        Add items to combobox based on source comboBox items.
        """

        for r in range(source.count()):
	    item = comboBox.addItem(source.itemText(r))
      
        comboBox.setCurrentIndex(source.currentIndex())
        comboBox.setEnabled(False)

    def sections_init(self, comboBox, tabWidget):
        comboBox.clear()
	item = comboBox.addItem(tabWidget)
	comboBox.setCurrentIndex(0)
	comboBox.setEnabled(True)	
        """
        Add items to comboBox based on tabWidget items.
        
        comboBox.clear()
        if tabWidget.count() > 0:
            comboBox.setEnabled(True)
            self.ui_enable()
            for r in range(tabWidget.count()):
                item = comboBox.addItem(tabWidget.widget(r).folderName)

            try:
                comboBox.setCurrentIndex(comboBox.findText(tabWidget.currentWidget().folderName))
            except:
                comboBox.setCurrentIndex(0)

        else:
            comboBox.setEnabled(False)
            self.ui_enable(False)
	"""
    def sections_activated(self, comboBox, tabWidget, init = True):
        """
        comboBox activated signal function.
        Update comboBox items based on tabwidget items if init is True.
        Update tabwidget current Item based of comboBox current item
        """
        for r in range(tabWidget.count()):
            if tabWidget.widget(r).folderName == comboBox.currentText():
                if init:
                    self.sections_init(self.s_comboBox, tabWidget.widget(r))
                tabWidget.setCurrentIndex(r)

        self.label_init()

    def ui_enable(self, bool = True):
        """
        Enable/Disbale part of the ui.
        """
        self.pushButton.setEnabled(bool)
        self.toolButton.setEnabled(bool)
        self.a_groupBox.setEnabled(bool)
        self.d_groupBox.setEnabled(bool)
        self.n_groupBox.setEnabled(bool)

    def ui_defaultValue(self):
        """
        """
        self.lineEdit.setText('')
        self.d_plainTextEdit.setPlainText('')
        self.n_plainTextEdit.setPlainText('')
   #     self.t_checkBox.setCheckState(setPySideCheckState(2))
   #     self.r_checkBox.setCheckState(setPySideCheckState(2))
   #     self.s_checkBox.setCheckState(setPySideCheckState(0))
	"""
    def version(self, sectionWidget):
       

        close = True
        project = self.p_comboBox.currentText()
        section = self.s_comboBox.currentText()
        subsection = self.ss_comboBox.currentText()
        name = self.lineEdit.text()
        description = self.d_plainTextEdit.toPlainText()
        note = self.n_plainTextEdit.toPlainText()
        snap = [self.t_checkBox.checkState() == QtCore.Qt.Checked and 2 or 0, self.r_checkBox.checkState() == QtCore.Qt.Checked and 2 or 0, self.s_checkBox.checkState() == QtCore.Qt.Checked and 2 or 0]
        typ = mayaType()
        filename = self.currentVersion > 0.96 and name + '_' or ''
        if self.create:
            asset = createFolder(self.root + '/' + project + '/' + section + '/' + subsection, self, name=name, type=subsection)
            if asset:
                if not isinstance(asset, bool):
                    if len(asset) == 2:
                        folders = createFoldersFromTemplate(asset[0] + '/' + asset[1], self, ui.assets_default)
                        mayafile = createVersion(asset[0] + '/' + asset[1], self, save=self.save, sel=self.sel, note=note, description=description, snap=snap, pad=numpad, typ=typ, icon=self.toolButton.imageFile, version=self.currentVersion)
                        item = listWidget_add_item(sectionWidget.currentWidget().currentWidget(), mayafile, name, icon_default, self.currentVersion)
                        sectionWidget.currentWidget().currentWidget().sortItems(QtCore.Qt.AscendingOrder)
                        sectionWidget.currentWidget().currentWidget().setCurrentItem(item)
                else:
                    close = False
        else:
            if mc.optionVar(q=optvar_manageTexture):
                manageFileTexture(os.path.split(self.current.sceneFile)[0] + '/' + images_folder, self)
            mayafile = createVersion(os.path.split(self.current.sceneFile)[0], self, note=note, description=description, snap=snap, pad=numpad, typ=typ, icon=self.toolButton.imageFile, version=self.currentVersion)
            self.current.sceneFile = mayafile
            self.current.note = note
            self.current.description = description
            self.current.snap = str(snap)
            icon_file = os.path.split(self.current.sceneFile)[0] + '/' + ui_folder + '/' + os.path.splitext(str(os.path.split(self.current.sceneFile)[1]))[0] + '.jpeg'
            if not os.path.isfile(icon_file):
                icon_file = icon_default
            item = listWidget_item_create_icon([self.current], icon_file)
            self.current.nextVersion = v_prefix + return_padded_integer(int(self.current.nextVersion.split(v_prefix)[1]) + 1, numpad)
            self.current.masterFile = os.path.split(mayafile)[0] + '/' + filename + masterReference + typ[1]
            self.current.masterVersion = os.path.splitext(os.path.split(mayafile)[1])[0]
            self.current.masterVersionFile = os.path.split(mayafile)[0] + '/' + ui_folder + '/' + os.path.splitext(os.path.split(mayafile)[1])[0] + '.' + masterReference
            ui.all_init(self.current)
        if not self.checkBox.isChecked():
            if close:
                self.close()
        self.lineEdit.setFocus()        
	"""
    def closeEvent(self, event):
        """
        reimplemented close event to delete snapshot image
        """
        try:
            os.remove(self.toolButton.imageFile)
        except:
            pass

        event.accept()




class SnapWindow(snap_form,snap_base):# QtWidgets.QMainWindow):
    MAYA2014 = 201400
    MAYA2015 = 201500
    MAYA2016 = 201600
    MAYA2016_5 = 201650
    MAYA2017 = 201700
    MAYA2018 = 201800
    MAYA2019 = 201900
    """
    """
    window = 'snap_window'
    formLayout = 'snap_formLayout'
    modelEditor = 'snap_modelEditor'
    camera = 'snap_cam'
    base_wight	= 500
    base_height = 600
    box_height = 32
    optvar_renderer = 'st_asset_manager_snapui_renderer'
    optvar_displayLights = 'st_asset_manager_snapui_displayLights'
    optvar_modifiers = 'st_asset_manager_snapui_modifiers'
    optvar_preferences = 'st_asset_manager_snapui_preferences'
    optvar_snapMatchActiveCamera ='st_asset_manager_snapMatchActiveCamera'
    optvar_useSnapCamStoredInfo = 'st_asset_manager_useSnapCamStoredInfo'
    match_attr = ['horizontalFilmAperture',
     'verticalFilmAperture',
     'lensSqueezeRatio',
     'cameraScale',
     'nearClipPlane',
     'farClipPlane',
     'focalLength']

    def __init__(self, parent = None, update = [False, False, False], root = False):
        super(SnapWindow, self).__init__(parent)#parent will change
       
        #self.setWindowFlags(QtCore.Qt.Tool)
	#snap_form, snap_base = loadUiType(os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/ui/st_assets_snap.ui')
      #  self=snap_form()
	
        
        self.setupUi(self)
	self.resize(520, 700)
	#self.raise_()
        self.root = root
        self.current = update[0]
        self.secondary = update[1]
        self.button = update[2]
        label = u'Snap'
        separator = ' '
        if self.secondary:
            label = label + ' ' + self.secondary.text()
            if self.current:
                separator = '/'
        if self.current:
            label = label + separator + self.current.text()
        self.title = self.setWindowTitle(label)
        self.pushButton.setText(label)
        self.window = mc.window()
        self.form = mc.formLayout(self.formLayout)
        self.model = mc.modelEditor(self.modelEditor)
        mc.formLayout(self.form, e=True, af=[(self.model, 'top', 0),
         (self.model, 'bottom', 0),
         (self.model, 'left', 0),
         (self.model, 'right', 0)])
        self.formqt = toQtObject(self.form)
        self.formqt.setParent(self.frame)
        self.frame.layout().addWidget(self.formqt)
        self.formqt.setMinimumSize(500, 500)
        self.hot_F = QtWidgets.QShortcut(self)
        self.hot_F.setKey('f')
        self.hot_6 = QtWidgets.QShortcut(self)
        self.hot_6.setKey('6')
        self.hot_7 = QtWidgets.QShortcut(self)
        self.hot_7.setKey('7')
        self.menu_init()
        self.pushButton.clicked.connect(self.blast)
        self.hot_F.activated.connect(self.camera_frame)
        self.hot_6.activated.connect(lambda : self.menuLighting_clicked_dl(self.actionUse_Default_Lighting))
        self.hot_7.activated.connect(lambda : self.menuLighting_clicked_dl(self.actionUse_All_Lights))
        self.doubleSpinBox.valueChanged.connect(lambda : self.camera_focalLength(self.doubleSpinBox, self.horizontalSlider))
        self.horizontalSlider.valueChanged.connect(lambda : self.camera_focalLength(self.horizontalSlider, self.doubleSpinBox))
        self.near_doubleSpinBox.valueChanged.connect(lambda : self.camera_setAttr(self.near_doubleSpinBox, 'nearClipPlane'))
        self.far_doubleSpinBox.valueChanged.connect(lambda : self.camera_setAttr(self.far_doubleSpinBox, 'farClipPlane'))
        self.setMinimumHeight(self.base_height)
        self.setMaximumHeight(self.base_height)
        self.menuPref_clicked(self.actionShow_Lens, self.horizontalGroupBox)
        self.menuPref_clicked(self.actionShow_Clip_Plane, self.clip_groupBox)
        self.cam = self.camera_create(self.model)
        #self.formqt.setFocus()




	
    def run(self):
        '''
		2017 docking is a little different...
	'''
	def run2017():
            self.show()#dockable=True, area='right', floating=False)
	#    self.move (700,200) 

        def run2016():
            self.show()#dockable=True, area='right', floating=False)
	 #   self.move (700,200) 

        if maya_api_version() < SnapWindow.MAYA2017:
            run2016()
        else:
            run2017()

    
    def menu_init(self):
        """
        Initialize the 4 menus based on optionVar info and connects to according signals.
        It creates the optionVar with default value if it didn't exists.
        """
        actions = self.menuShow.actions()
        for a in actions:
            if not a.isSeparator():
                self.connect(a, QtCore.SIGNAL('triggered()'), lambda a = a: self.menuShow_clicked(a))
                if a.property('modifier') != 'alo':
                    if mc.optionVar(ex=self.optvar_modifiers + '_' + a.property('modifier')):
                        a.setChecked(mc.optionVar(q=self.optvar_modifiers + '_' + a.property('modifier')))
                    else:
                        mc.optionVar(iv=[self.optvar_modifiers + '_' + a.property('modifier'), a.isChecked()])

        for a in self.menuLighting.actions():
            if a.property('value') != None:
                self.connect(a, QtCore.SIGNAL('triggered()'), lambda a = a: self.menuLighting_clicked_dl(a))
                if mc.optionVar(ex=self.optvar_displayLights):
                    if mc.optionVar(q=self.optvar_displayLights) == a.property('value'):
                        a.setChecked(True)
                    else:
                        a.setChecked(False)
                else:
                    mc.optionVar(sv=[self.optvar_displayLights, 'default'])
            elif not a.isSeparator():
                self.connect(a, QtCore.SIGNAL('triggered()'), lambda a = a: self.menuLighting_clicked(a))
                if mc.optionVar(ex=self.optvar_modifiers + '_' + a.property('modifier')):
                    a.setChecked(mc.optionVar(q=self.optvar_modifiers + '_' + a.property('modifier')))
                else:
                    mc.optionVar(iv=[self.optvar_modifiers + '_' + a.property('modifier'), a.isChecked()])

        for a in self.menuRenderers.actions():
            self.connect(a, QtCore.SIGNAL('triggered()'), lambda a = a: self.menuRenderers_clicked(a))
            if mc.optionVar(ex=self.optvar_renderer):
                if mc.optionVar(q=self.optvar_renderer) == a.property('value'):
                    a.setChecked(True)
                else:
                    a.setChecked(False)
            else:
                mc.optionVar(sv=[self.optvar_renderer, 'base_OpenGL_Renderer'])

        self.actionShow_Lens.triggered.connect(lambda : self.menuPref_clicked(self.actionShow_Lens, self.horizontalGroupBox))
        self.actionShow_Clip_Plane.triggered.connect(lambda : self.menuPref_clicked(self.actionShow_Clip_Plane, self.clip_groupBox))
        for a in self.menuPreferences.actions():
            if mc.optionVar(ex=self.optvar_preferences + '_' + a.text()):
                a.setChecked(mc.optionVar(q=self.optvar_preferences + '_' + a.text()))
            else:
                mc.optionVar(iv=[self.optvar_preferences + '_' + a.text(), a.isChecked()])

    def menuShow_clicked(self, action):
        """
        Toggle snapshot viewport showoption and update show_menu ui.
        """
        if action.property('modifier') == 'alo':
            command = 'mc.modelEditor("' + self.model + '", e = True, ' + action.property('modifier') + ' = ' + str(action.property('value')) + ')'
            actions = self.menuShow.actions()
            for a in actions:
                if not a.isSeparator():
                    try:
                        a.setChecked(action.property('value'))
                    except:
                        pass
                    else:
                        mc.optionVar(iv=[self.optvar_modifiers + '_' + a.property('modifier'), a.isChecked()])

        else:
            command = 'mc.modelEditor("' + self.model + '", e = True, ' + action.property('modifier') + ' = ' + str(action.isChecked()) + ')'
            mc.optionVar(iv=[self.optvar_modifiers + '_' + action.property('modifier'), action.isChecked()])
        eval(command)

    def menuRenderers_clicked(self, action):
        """
        Renderers menu command connected to clicked signal.
        It changes the renderername(rnm) options. 
        and adjust optionVars accordingly
        """
        mc.modelEditor(self.modelEditor, e=True, rnm=action.property('value'))
        mc.optionVar(sv=[self.optvar_renderer, action.property('value')])
        actions = self.menuRenderers.actions()
        for a in actions:
            if a.property('value') == mc.modelEditor(self.modelEditor, q=True, rnm=True):
                a.setChecked(True)
            else:
                a.setChecked(False)

    def menuLighting_clicked_dl(self, action, mod = False):
        """
        Lighting menu command connected to clicked signal.
        It changes the displayLight(dl) options. Default, Selected or All are supported.
        and adjust optionVars accordingly
        """
        mc.modelEditor(self.modelEditor, e=True, dl=action.property('value'))
        mc.optionVar(sv=[self.optvar_displayLights, action.property('value')])
        actions = self.menuLighting.actions()
        for a in actions:
            if a.property('value') != None:
                if a.property('value') == mc.modelEditor(self.modelEditor, q=True, dl=True):
                    a.setChecked(True)
                else:
                    a.setChecked(False)

    def menuLighting_clicked(self, action):
        """
        Lighting menu command connected to clicked signal.
        It edit the modelEditor by turning on or off the selected item and adjust optionVars accordingly.
        """
        command = 'mc.modelEditor("' + self.model + '", e = True, ' + action.property('modifier') + ' = ' + str(action.isChecked()) + ')'
        mc.optionVar(iv=[self.optvar_modifiers + '_' + action.property('modifier'), action.isChecked()])
        eval(command)

    def menuPref_clicked(self, action, widget):
        """
        Preference menu command connected to clicked signal.
        It shows or hide the widget based on action menu chcked state, adjusting the window size when necessary.
        """
        if action.isChecked():
            widget.setHidden(False)
            self.setMinimumHeight(self.minimumHeight() + self.box_height)
            self.setMaximumHeight(self.maximumHeight() + self.box_height)
            mc.optionVar(iv=[self.optvar_preferences + '_' + action.text(), action.isChecked()])
        else:
            widget.setHidden(True)
            self.setMinimumHeight(self.minimumHeight() - self.box_height)
            self.setMaximumHeight(self.maximumHeight() - self.box_height)
            mc.optionVar(iv=[self.optvar_preferences + '_' + action.text(), action.isChecked()])

    def camera_query(self, preferred = False):
        """
        Query and return active view camera. return False value if no active view is found.
        """
        panels = []

        ac = False
        proceed = True
        if proceed:
            for p in mc.lsUI(p=True):
                if mc.modelPanel(p, ex=True):
                    panels.append(p)

            for p in panels:
                if mc.modelEditor(p, q=True, av=True):
                    av = p

            if av:
                ac = mc.modelPanel(av, q=True, cam=True)
        if mc.camera(ac, q=True, sc=True):
            return ac
        else:
            return mc.listRelatives(ac, p=True)[0]

    def camera_create(self, modelEditor):
        """
        
        """
        ac = self.camera_query()
        self.cam = mc.camera(n=self.camera, fl=50, ncp=1, fcp=100000)
        if ac:
            mc.xform(self.cam[0], ws=True, t=mc.xform(ac, q=True, ws=True, t=True))
            mc.xform(self.cam[0], ws=True, ro=mc.xform(ac, q=True, ws=True, ro=True))
            if mc.optionVar(q=self.optvar_snapMatchActiveCamera):
                for a in self.match_attr:
                    mc.setAttr(self.cam[1] + '.' + a, mc.getAttr(mc.listRelatives(ac, s=True)[0] + '.' + a))

                self.doubleSpinBox.setValue(mc.getAttr(mc.listRelatives(ac, s=True)[0] + '.' + a))
                self.horizontalSlider.setValue(mc.getAttr(mc.listRelatives(ac, s=True)[0] + '.' + a))
        mc.modelEditor(modelEditor, e=True, cam=self.cam[0])
        mc.modelEditor(self.model, e=True, av=True)
        mc.modelEditor(self.model, e=True, da='smoothShaded')
        mc.modelEditor(self.model, e=True, dtx=True)
        mc.modelEditor(self.model, e=True, st=True)
        for a in self.menuShow.actions():
            if not a.isSeparator():
                if a.property('modifier') != 'alo':
                    if a.property('modifier') != '':
                        command = 'mc.modelEditor("' + self.model + '", e = True, ' + a.property('modifier') + ' = ' + str(a.isChecked()) + ')'
                        eval(command)

        for a in self.menuLighting.actions():
            if a.property('value') != None:
                if a.isChecked():
                    mc.modelEditor(self.model, e=True, dl=a.property('value'))
            elif not a.isSeparator():
                command = 'mc.modelEditor("' + self.model + '", e = True, ' + a.property('modifier') + ' = ' + str(a.isChecked()) + ')'
                eval(command)

        for a in self.menuRenderers.actions():
            if a.isChecked():
                mc.modelEditor(self.model, e=True, rnm=a.property('value'))

        return self.cam

    def camera_focalLength(self, widget, updateWidget):
        """
        Def connected to the lens spinbox and slider.
        """
        mc.setAttr(self.cam[1] + '.focalLength', widget.value())
        if widget.value() > updateWidget.maximum():
            updateWidget.setMaximum(widget.value())
        if widget.value() < updateWidget.minimum():
            updateWidget.setMinimum(widget.value())
        updateWidget.setValue(widget.value())

    def camera_setAttr(self, widget, attr):
        """
        Def connects a widget to a self.camShape attribute. 
        """
        mc.setAttr(self.cam[1] + '.' + attr, widget.value())

    def camera_frame(self):
        """
        """
        mc.viewFit(self.cam[0])

    def camera_info(self):
        """
        store snap cam info. in progress
        """
        trs = mc.xform(self.cam, q=True, t=True, ws=True)
        rot = mc.xform(self.cam, q=True, t=True, ws=True)
        values = []
        for a in self.match_attr:
            values.append(mc.getAttr(self.cam[1] + '.' + a))

        info = [trs,
         rot,
         self.match_attr,
         values]

    def blast(self):
        """
        """
        mc.modelEditor(self.model, e=True, av=True)
        mc.modelEditor(self.model, e=True, sel=False)
        offs = False
        if mc.modelEditor(self.model, q=True, rnm=True) == 'ogsRenderer':
            offs = True
        self.camera_info()
        image = mc.playblast(completeFilename=os.path.join(MAYA_APP_DIR,"ui\\Temp.jpg"),f=self.root + '/' + 'temp', fr=float(mc.currentTime(q=True)), p=100, wh=[256, 256], fmt='image', c='jpg', fo=True, orn=False, v=False, fp=1, os=offs)
        mc.modelEditor(self.model, e=True, sel=True)
        self.image = image.replace('.####', '.0')
        if self.current:
            if os.path.isfile(os.path.split(self.current.sceneFile)[0] + '/' + ui_folder + '/' + os.path.splitext(os.path.split(self.current.sceneFile)[1])[0] + '.jpeg'):
                os.remove(os.path.split(self.current.sceneFile)[0] + '/' + ui_folder + '/' + os.path.splitext(os.path.split(self.current.sceneFile)[1])[0] + '.jpeg')
            move = shutil.move(self.image, os.path.split(self.current.sceneFile)[0] + '/' + ui_folder + '/' + os.path.splitext(os.path.split(self.current.sceneFile)[1])[0] + '.jpeg')
            icon = listWidget_item_create_icon([self.current], os.path.split(self.current.sceneFile)[0] + '/' + ui_folder + '/' + os.path.splitext(os.path.split(self.current.sceneFile)[1])[0] + '.jpeg')
            if self.secondary:
                if os.path.split(self.secondary.sceneFile)[1] in self.current.text():
                    listWidget_item_create_icon([self.secondary], os.path.split(self.current.sceneFile)[0] + '/' + ui_folder + '/' + os.path.splitext(os.path.split(self.current.sceneFile)[1])[0] + '.jpeg')
            if self.button:
                self.button.setIcon(icon)
		
		
	else:
            icon = listWidget_item_create_icon([self.button], self.image)
            self.button.imageFile = self.image
	
	#将创建窗口设置回到最前端 
	getattr(uip,"raise")()
	uip.activateWindow()	
        self.close()

    def closeEvent(self, event):
        """
        reimplemented close event to delete cam and maya ui
        """
	getattr(uip,"raise")()
	uip.activateWindow()	
        try:
            mc.delete(self.cam[0])
        except:
            pass

        try:
            mc.deleteUI(self.model)
        except:
            pass

        try:
            mc.deleteUI(self.form)
        except:
            pass

        try:
            mc.deleteUI(self.window)
        except:
            pass

        event.accept()






#Log
import logging

logging.basicConfig()
logger = logging.getLogger('AssetManager')
logger.setLevel(logging.INFO)




def start(path=MAYA_APP_DIR,storagepath=''):
  
    if path == "":
        path = MAYA_APP_DIR
    
    if cmp(storagepath,'')==0:
	storagepath=os.environ['ONION_FILES_ROOT']
    logger.debug("Starting")
    ### DOWNLOAD FOLDER ICON

    url = "http://pepperusso.uk/scripts/assetManager/"
    # Get current maya version
    version = mc.about(version=True)

    # Download Icon
    appPath = path

    folderImg = os.path.join(appPath, "ui\\AM_folder.png")
    unknownImg = os.path.join(appPath, "ui\\AM_unknown.jpg")
    """
    try:
        if not os.path.isfile(folderImg):
            urllib.urlretrieve(url+"AM_folder.png", folderImg)
        if not os.path.isfile(unknownImg):
            urllib.urlretrieve(url+"AM_unknown.jpg", unknownImg)
    except:
        logger.info("Can't download icons. Please download them manually from the following links and paste them in Documents\maya\VERSION\prefs\icons")
        logger.info("http://pepperusso.uk/scripts/assetManager/AM_folder.png")
        logger.info("http://pepperusso.uk/scripts/assetManager/AM_unknown.jpg")
	folderImg = os.path.join(appPath, "ui\\AM_folder.png")
	unknownImg = os.path.join(appPath, "ui\\AM_unknown.jpg")
    """
    ## START
    global w    
    w = AssetManager(appPath,storagepath)
    w.show()
    w.move (100,200)    

def isHiDPI():
    screenH = QtWidgets.QDesktopWidget().screenGeometry().height()
    screenW = QtWidgets.QDesktopWidget().screenGeometry().width()
    if screenH < 1081 or screenW < 1921:  # Non HIDPI
        return False
    else:
        return True

class AssetManager(QtWidgets.QMainWindow):
    def __init__(self, path=MAYA_APP_DIR,storagepath=MAYA_APP_DIR):
        super(AssetManager, self).__init__()
        windowName = 'AssetManagerWindow'
        # Delete if exists
        if mc.window(windowName, exists=True):
            mc.deleteUI(windowName)
            logger.debug('Deleted previous UI')
        else:
            logger.debug('No previous UI exists')
            pass
	



        # Get Maya window and parent the controller to it
        mayaMainWindow = {o.objectName(): o for o in QtWidgets.qApp.topLevelWidgets()}["MayaWindow"]
        self.setParent(mayaMainWindow)
        self.setWindowFlags(QtCore.Qt.Window)

        self.setWindowTitle('Model Manager')
        self.setObjectName(windowName)
        if isHiDPI():
            self.resize(600, 600)
        else:
            self.resize(300, 300)
	self.parentroottypes={}
        self.buildUI()
        self.populate(storagepath)



    def buildUI(self):
        # Main widget
        widget = QtWidgets.QWidget(self)
        self.setCentralWidget(widget)

        # Main Layout
        layout = QtWidgets.QGridLayout()
        widget.setLayout(layout)
	try:
	    layout.setMargin(3)
	    layout.setSpacing(9)
	    
	except:
	    layout.setContentsMargins(3,9,3,9)
	    



        # Directory above button
        upBtn = QtWidgets.QPushButton()
        upBtn.setStyleSheet('QPushButton {background-color: #444444; color: red;}')
	upBtn.setIconSize(QtCore.QSize(16,16))
        #upBtn.setIcon(upBtn.style().standardIcon(QtWidgets.QStyle.SP_FileDialogToParent))
	#upBtn.setText(u'向上')
	screenpic = os.path.join(MAYA_APP_DIR, "ui\\goup.png")
	iconpic=QtGui.QIcon(screenpic)	
	upBtn.setIcon(iconpic)
        upBtn.clicked.connect(self.getParentDir)
        layout.addWidget(upBtn,0,0,1,1)

        # Current directory
        self.currentDirTxt = QtWidgets.QLineEdit()
	self.currentDirTxt.setStyleSheet("border: 2px groove black; border-radius: 4px;background-color:#ffffff")
        self.currentDirTxt.returnPressed.connect(lambda: self.populate(self.currentDirTxt.text()))
	self.currentDirTxt.setEnabled(False)
        layout.addWidget(self.currentDirTxt,0,1,1,12)

        # New Folder button
        newDirBtn = QtWidgets.QPushButton()
	newDirBtn.setStyleSheet('QPushButton {background-color: #444444; color: red;}')
	newDirBtn.setIconSize(QtCore.QSize(16,16))
        #newDirBtn.setIcon(newDirBtn.style().standardIcon(QtWidgets.QStyle.SP_FileDialogNewFolder))
	#newDirBtn.setText(u'当前')
	screenpic = os.path.join(MAYA_APP_DIR, "ui\\menu.png")
	iconpic=QtGui.QIcon(screenpic)	
	newDirBtn.setIcon(iconpic)	
        newDirBtn.clicked.connect(self.OpenFolderDialog)
        layout.addWidget(newDirBtn,0,13)





       
       
 	# Label
	self.newLabel=QtWidgets.QLabel()
	self.newLabel.setText("Class Infomation     ")
	self.newLabel.setAlignment(QtCore.Qt.AlignCenter)
	layout.addWidget(self.newLabel,1,0,1,2)

	# ComboBox
	self.newComboBox=QtWidgets.QComboBox()
	self.newComboBox.addItem(u'All')	
	self.classinffile=os.path.join(os.path.abspath(MAYA_APP_DIR), 'ui\\Class.inf')
	self.treeList=ET.parse(self.classinffile)

	
	
	
	
	self.roottype=self.treeList.getroot()
	for ty in self.roottype:
	    inf=ty.text
	    self.newComboBox.addItem(inf)
    
	
	self.parentclassinf=os.path.join(os.path.abspath(os.environ['ONION_FILES_ROOT']), 'Class.clx')
	self.parenttreeList=ET.parse(self.parentclassinf)
	self.parentroottypes=self.parenttreeList.getroot()

	for pty in self.parentroottypes:
	    if self.newComboBox.findText(pty.text)<0:
		self.newComboBox.addItem(pty.text)
		son=ET.Element(pty.text) 
		son.tag=pty.text
		son.text= pty.text
		self.roottype.append(son)
	self.treeList.write(self.classinffile,encoding="utf-8")
		
	
	

	
	#self.newComboBox.addItem(u'零件')
	self.newComboBox.setCurrentIndex(0)
	self.newComboBox.setMinimumWidth(256)
	self.newComboBox.setStyleSheet("border: 2px groove black; border-radius: 4px;background-color:#ffffff;color:#000000")
	layout.addWidget(self.newComboBox,1,2,1,4)
  


	# Add Button
	newAddBtn = QtWidgets.QPushButton()
	screenpic = os.path.join(MAYA_APP_DIR, "ui\\classadd.png")
	iconpic=QtGui.QIcon(screenpic)	
	
	newAddBtn.setIcon(iconpic)
	newAddBtn.setStyleSheet('QPushButton {background-color: #3ba2e5; color: red;}')
	newAddBtn.setIconSize(QtCore.QSize(45,16))
	#newAddBtn.setText(u'增加分类')
	newAddBtn.clicked.connect(self.AddComboBoxList)
	layout.addWidget(newAddBtn,1,6,1,1)	
	
	
	"""
	# Edit Class
	self.EditTxt = QtWidgets.QLineEdit()
	self.EditTxt.setMaximumWidth(1000)
	self.EditTxt.setMinimumWidth(500)
	self.EditTxt.setStyleSheet("border: 2px groove black; border-radius: 4px;")
	#self.EditTxt.returnPressed.connect(lambda: self.populate(self.EditTxt.text()))
	layout.addWidget(self.EditTxt,2,1) 
	"""
	
	# Rename Button
	newUpDateBtn = QtWidgets.QPushButton()
	screenpic = os.path.join(MAYA_APP_DIR, "ui\\classedit.png")
	iconpic=QtGui.QIcon(screenpic)	
	newUpDateBtn.setIcon(iconpic)	
	newUpDateBtn.setStyleSheet('QPushButton {background-color: #3ba2e5; color: red;}')
	newUpDateBtn.setIconSize(QtCore.QSize(45,16))
	#newUpDateBtn.setText(u'修改分类')
	newUpDateBtn.clicked.connect(self.UpdateComboBoxList)
	layout.addWidget(newUpDateBtn,1,7,1,1)	 
 



	# Del Button
	newDelBtn = QtWidgets.QPushButton()
	screenpic = os.path.join(MAYA_APP_DIR, "ui\\classdel.png")
	iconpic=QtGui.QIcon(screenpic)	
	newDelBtn.setIcon(iconpic)
	newDelBtn.setStyleSheet('QPushButton {background-color: #3ba2e5; color: red;}')
	newDelBtn.setIconSize(QtCore.QSize(45,16))
	#newDelBtn.setText(u'删除分类')
	newDelBtn.clicked.connect(self.DelComboBoxList)
	layout.addWidget(newDelBtn,1,8,1,1)	   

 
 
	# Label
	self.newLabel2=QtWidgets.QLabel()
	self.newLabel2.setText("View Style")
	
	layout.addWidget(self.newLabel2,1,11,1,1)
 
 
	#View Style
	self.ViewStyle=QtWidgets.QComboBox()
	self.ViewStyle.addItem(u'Small Icon')	
	self.ViewStyle.addItem(u'Middle Icon')	
	self.ViewStyle.addItem(u'Large Icon')	
	self.ViewStyle.addItem(u'Small List Style')	
	self.ViewStyle.addItem(u'Normal List Style')	
	self.ViewStyle.setCurrentIndex(0)
	self.ViewStyle.setStyleSheet("border: 2px groove black; border-radius: 4px;background-color:#ffffff;color:#000000")
	layout.addWidget(self.ViewStyle,1,12,1,2)



	self.newLabel3=QtWidgets.QLabel()
	self.newLabel3.setText("Search:")
	self.newLabel3.setAlignment(QtCore.Qt.AlignCenter)
	layout.addWidget(self.newLabel3,2,0,1,1)		
 
 
	# Search field
	self.searchFld = QtWidgets.QLineEdit()
	self.searchFld.setPlaceholderText('Search...')
	self.searchFld.textChanged.connect(self.search)
	self.searchFld.setMinimumWidth(256)
	self.searchFld.setStyleSheet("border: 2px groove black; border-radius: 4px;background-color:#ffffff;color:#000000")
	layout.addWidget(self.searchFld,2,1,1,3)
	
	self.searchFld.setFocus()

	# New Asset Search button
	newSearchBtn = QtWidgets.QPushButton()
#	newSearchBtn.setIcon(newSearchBtn.style().standardIcon(QtWidgets.QStyle.SP_DialogSaveButton))
	#newSearchBtn.setText(u'搜索')
	screenpic = os.path.join(MAYA_APP_DIR, "ui\\search.png")
	iconpic=QtGui.QIcon(screenpic)	
	newSearchBtn.setStyleSheet('QPushButton {background-color: #3ba2e5; color: red;}')
	newSearchBtn.setIcon(iconpic)	
	newSearchBtn.setIconSize(QtCore.QSize(16,16))
	newSearchBtn.clicked.connect(self.search)
	layout.addWidget(newSearchBtn,2,4,1,1)
	
	self.newComboBox.currentIndexChanged.connect(self.RefreshFolder)

 
 
 
	# New Asset Save button
	newSaveBtn = QtWidgets.QPushButton()
	newSaveBtn.setIcon(newSaveBtn.style().standardIcon(QtWidgets.QStyle.SP_DialogSaveButton))
	screenpic = os.path.join(MAYA_APP_DIR, "ui\\save.png")
	iconpic=QtGui.QIcon(screenpic)	
	newSaveBtn.setIcon(iconpic)
	newSaveBtn.setStyleSheet('QPushButton {background-color: #3ba2e5; color: red;}')
	newSaveBtn.setIconSize(QtCore.QSize(45,16))
	#newSaveBtn.setText(u'存储模型')
	newSaveBtn.clicked.connect(self.save)
	layout.addWidget(newSaveBtn,2,7,1,1)
 


	#Edit Button
	newEditModelBtn = QtWidgets.QPushButton()
	newEditModelBtn.setStyleSheet('QPushButton {background-color: #9a9a9a; color: red;}')
	screenpic = os.path.join(MAYA_APP_DIR, "ui\\edit.png")
	iconpic=QtGui.QIcon(screenpic)
	
	newEditModelBtn.setIcon(iconpic)	
	newEditModelBtn.setIconSize(QtCore.QSize(45,16))
	#newEditModelBtn.setText(u'修改/命名')
	newEditModelBtn.clicked.connect(self.EditInfo)
	layout.addWidget(newEditModelBtn,2,8,1,1)


	#New Folder Button
	newFolderBtn = QtWidgets.QPushButton()
	newFolderBtn.setStyleSheet('QPushButton {background-color: #9a9a9a; color: red;}')
	screenpic = os.path.join(MAYA_APP_DIR, "ui\\new.png")
	iconpic=QtGui.QIcon(screenpic)	
	
	newFolderBtn.setIcon(iconpic)	
	newFolderBtn.setIconSize(QtCore.QSize(45,16))
	#newFolderBtn.setText(u'新文件夹')
	newFolderBtn.clicked.connect(self.newFolder)
	layout.addWidget(newFolderBtn,2,9,1,1)



	#Open Button
	newOpenBtn = QtWidgets.QPushButton()
	screenpic = os.path.join(MAYA_APP_DIR, "ui\\open.png")
	iconpic=QtGui.QIcon(screenpic)	
	newOpenBtn.setIcon(iconpic)
	newOpenBtn.setStyleSheet('QPushButton {background-color: #3ba2e5; color: red;}')
	newOpenBtn.setIconSize(QtCore.QSize(45,16))
	#newOpenBtn.setText(u'打开/导入')
	newOpenBtn.clicked.connect(self.load)
	layout.addWidget(newOpenBtn,2,10,1,1)	   	
	
	   	
	
	#Move Button
	newMoveModelBtn = QtWidgets.QPushButton()
	newMoveModelBtn.setStyleSheet('QPushButton {background-color: #9a9a9a; color: red;}')
	screenpic = os.path.join(MAYA_APP_DIR, "ui\\move.png")
	iconpic=QtGui.QIcon(screenpic)	
	newMoveModelBtn.setIcon(iconpic)
	newMoveModelBtn.setIconSize(QtCore.QSize(45,16))
	#newMoveModelBtn.setText(u'移动')
	newMoveModelBtn.clicked.connect(self.moveItem)
	layout.addWidget(newMoveModelBtn,2,11,1,1)	
	
	
	#Delete Button
	newDelModelBtn = QtWidgets.QPushButton()
	newDelModelBtn.setStyleSheet('QPushButton {background-color: #9a9a9a; color: red;}')
	screenpic = os.path.join(MAYA_APP_DIR, "ui\\del.png")
	iconpic=QtGui.QIcon(screenpic)	
	newDelModelBtn.setIcon(iconpic)	
	newDelModelBtn.setIconSize(QtCore.QSize(45,16))
	#newDelModelBtn.setText(u'删除')
	newDelModelBtn.clicked.connect(self.delete)
	layout.addWidget(newDelModelBtn,2,12,1,1)	



	#Refresh Folder Button
	newRefreshBtn = QtWidgets.QPushButton()
	screenpic = os.path.join(MAYA_APP_DIR, "ui\\refresh.png")
	iconpic=QtGui.QIcon(screenpic)	
	newRefreshBtn.setIcon(iconpic)
	newRefreshBtn.setStyleSheet('QPushButton {background-color: #3ba2e5; color: red;}')
	newRefreshBtn.setIconSize(QtCore.QSize(45,16))
	#newRefreshBtn.setText(u'刷新')
	newRefreshBtn.clicked.connect(self.RefreshFolder)
	layout.addWidget(newRefreshBtn,2,13,1,1)
 
 
 
 
 
        
       
        # List Widget
	
        ## HiDPI Fix
        if isHiDPI():
            self.iconSize = 64
            self.padding = 4
        else:
            self.iconSize = 256
            self.padding = 16
	self.iconSize = 64
	self.ViewMode=0
        self.listWidget = QtWidgets.QListWidget()

        self.listWidget.setViewMode(QtWidgets.QListWidget.IconMode)
        self.listWidget.setIconSize(QtCore.QSize(self.iconSize, self.iconSize))
        self.listWidget.setResizeMode(QtWidgets.QListWidget.Adjust)
        self.listWidget.setMovement(QtWidgets.QListWidget.Static) # disable drag and drop
        self.listWidget.setGridSize(QtCore.QSize(self.iconSize + self.padding, self.iconSize + self.padding))

        self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)  # enable multiple selection
        self.listWidget.itemDoubleClicked.connect(self.load)

	self.listWidget.setMinimumHeight(350)
        layout.addWidget(self.listWidget,3,0,8,14)

        # RIGHT CLICK MENU
        self.listWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.listWidget.customContextMenuRequested.connect(self.openMenu)





	self.ViewStyle.currentIndexChanged.connect(self.changeListStyle)

	"""
	newViewFunBtn = QtWidgets.QPushButton()
	screenpic = os.path.join(MAYA_APP_DIR, "ui\\view.png")
	iconpic=QtGui.QIcon(screenpic)	
	newViewFunBtn.setIcon(iconpic)
	newViewFunBtn.setIconSize(QtCore.QSize(45,16))	
	#newViewFunBtn.setText(u'浏览方式')
	newViewFunBtn.clicked.connect(self.changeListStyle)
	layout.addWidget(newViewFunBtn,11,2,1,1)	
	"""

    def CheckAdmin(self):
	result = mc.promptDialog(
            title=u'验证窗口',
            message=u'需要提升权限\n请输入管理员密码:',
            button=['OK', 'Cancel'],
            defaultButton='OK',
            cancelButton='Cancel',
            dismissString='Cancel')	
	if result == 'OK':
	    SecName = mc.promptDialog(query=True, text=True)

	    if not SecName: # Empty field
		logger.error(u"请输入一个密码")	
		return False
	    elif cmp(SecName,'123456')!=0:
		logger.error(u"密码不正确")	
		return False
	    else:
		return True
	else:
	    return False


    def OpenFolderDialog(self):
	
	if not self.CheckAdmin():
	    return
		
	
	file_path =  QtWidgets.QFileDialog.getExistingDirectory(self,"Change Folder",self.userPath ) 
	if file_path =="":
	    return

	if type(file_path)==unicode:
	    GBfile_path=file_path.encode('utf-8')
	    self.currentDirTxt.setText(GBfile_path)
	elif type(file_path)==str:
	    GBfile_path=file_path
	    self.currentDirTxt.setText(file_path)
	else:
	    response = mc.confirmDialog(
		        title=u'调试显示浏览目录类型...',
		        message=type(file_path),
		        button=[u'是',u'否'],
		        defaultButton=u'否',
		        cancelButton=u'否',
		        dismissString=u'否')	    
	self.populate(GBfile_path)

    def AddComboBoxList(self):
	
	#index=self.newComboBox.findText(self.EditTxt.text())
	#if index>=0 or cmp(self.EditTxt.text(),"")==0:
	#    return
	
	
	result = mc.promptDialog(
            title='Add Class',
            message='Please Input a New Class Name : \n',
            button=['OK', 'Cancel'],
            defaultButton='OK',
            cancelButton='Cancel',
            dismissString='Cancel')

	if result == 'OK':
	    newName = mc.promptDialog(query=True, text=True)

	    if not newName: # Empty field
		logger.warning("Please insert a new class name")
		return
	    elif self.newComboBox.findText(newName)>=0: # New name == old name
		logger.warning("We already have a same class")
		return	
	    elif cmp(newName, "")==0:
		logger.warning("The name is empty")
		return
	
	    self.newComboBox.addItem(newName)
	    self.newComboBox.setCurrentIndex(self.newComboBox.findText(newName))
	
	    #self.treeList=ET.parse(self.classinffile)
	    #self.roottype=self.treeList.getroot()
	    Name=""
	    if type(newName)==unicode:
		Name=newName.encode('utf-8')
	    elif type(newName)==str:
		Name=newName
	    else:
		response = mc.confirmDialog(
	                    title=u'调试显示name类型...',
	                    message=type(newName),
	                    button=[u'是',u'否'],
	                    defaultButton=u'否',
	                    cancelButton=u'否',
	                    dismissString=u'否')	
	    son=ET.Element(Name) 
	    son.tag=Name
	    son.text= Name
	    self.roottype.append(son)
	    #ET.SubElement(self.treeList,self.EditTxt.text())
	    #
	    #for nowindex in range(self.newComboBox.count()):
	    
	    #    son=ET.Element(self.newComboBox.itemText(nowindex)) 
	    #    son.tag=self.newComboBox.itemText(nowindex)
	    #    son.text= self.newComboBox.itemText(nowindex)
	    #    self.treeList.append(son)#self.newComboBox.count()
	    self.treeList.write(self.classinffile,encoding="utf-8")
	    return
	
    def DelComboBoxList(self):
	
	if self.newComboBox.currentIndex()==0:
	    return	
	

	    
	
	
	#self.treeList=ET.parse(self.classinffile)
	#self.roottype=self.treeList.getroot()		
	for ty in self.roottype.findall(self.newComboBox.currentText()):
	    if(cmp(ty.text,self.newComboBox.currentText())==0):
		for pty in self.parentroottypes:
		    if cmp(pty.text,ty.text)==0:
			return
		self.roottype.remove(ty)

	self.treeList.write(self.classinffile,encoding="utf-8")	

	self.newComboBox.removeItem(self.newComboBox.currentIndex())
	if self.newComboBox.count()>=1:
	    self.newComboBox.setCurrentIndex(0)
	    
	"""
	for nowindex in range(self.newComboBox.count()):
	    
	    son=ET.Element(self.newComboBox.itemText(nowindex)) 
	    son.tag=self.newComboBox.itemText(nowindex)
	    son.text= self.newComboBox.itemText(nowindex)
	    self.treeList.append(son)#self.newComboBox.count()
	self.treeList.write(self.classinffile,encoding="utf-8")
	"""
	return
	    
    def UpdateComboBoxList(self):
	if self.newComboBox.currentIndex()==0:
	    return
	#index=self.newComboBox.findText(self.EditTxt.text())

	#if index>=0 or cmp(self.EditTxt.text(),"")==0:
	#    return
	Name=""
	result = mc.promptDialog(
            title='Edit Class',
            message='Changing class name from: '+self.newComboBox.currentText()+' to : \n',
            button=['OK', 'Cancel'],
            defaultButton='OK',
            cancelButton='Cancel',
            dismissString='Cancel')
	
	if result == 'OK':
	    newName = mc.promptDialog(query=True, text=True)
	
	    if not newName: # Empty field
		logger.warning("Please insert a new class name")
		return
	    elif self.newComboBox.findText(newName)>=0: # New name == old name
		logger.warning("We already have a same class")
		return	
	    elif cmp(newName, "")==0:
		logger.warning("The input name is empty")
		return
	    else:
		if type(newName)==unicode:
		    Name=newName.encode('utf-8')
		elif type(newName)==str:
		    Name=newName
		else:
		    response = mc.confirmDialog(
			        title=u'调试显示name类型...',
			        message=type(newName),
			        button=[u'是',u'否'],
			        defaultButton=u'否',
			        cancelButton=u'否',
			        dismissString=u'否')	  		    
	else:
	    return
	    
	for ty in self.roottype.findall(self.newComboBox.currentText()):
	    if(cmp(ty.text,self.newComboBox.currentText())==0):
		for pty in self.parentroottypes:
		    if cmp(pty.text,ty.text)==0:
			logger.warning("This section is stored on server! We can not change it.")
			return	

		
		ty.tag=Name
		ty.text=Name#self.EditTxt.text()
		
		    
	self.treeList.write(self.classinffile,encoding="utf-8")
	self.newComboBox.setItemText(self.newComboBox.currentIndex(),newName)
	
	#self.newComboBox.removeItem(self.newComboBox.currentIndex())	
	


    def RefreshFolder(self):
	self.populate(self.userPath)
	return
   
    def changeListStyle(self):
        listStyle = self.listWidget.viewMode()
	self.ViewMode=self.ViewStyle.currentIndex()
        #if listStyle == QtWidgets.QListWidget.IconMode:
	#while index is large the icon is large
	if self.ViewMode<3 and self.ViewMode>=0:
	    self.listWidget.setViewMode(QtWidgets.QListWidget.IconMode)
	    self.iconSize=64*(2**(self.ViewMode))
	else:# self.ViewMode>=3:  
	    self.listWidget.setViewMode(QtWidgets.QListWidget.ListMode) 
	    self.iconSize=64*(2**(self.ViewMode-3))
	
	
	self.listWidget.setIconSize(QtCore.QSize(self.iconSize, self.iconSize))
	self.listWidget.setGridSize(QtCore.QSize(self.iconSize + self.padding, self.iconSize + self.padding))
	self.listWidget.setResizeMode(QtWidgets.QListWidget.Adjust)	    

	return

    def getParentDir(self):
	if not self.CheckAdmin():
	    return
        parentDir = dirname(self.userPath)
        self.populate(parentDir)

    def populate(self, userPath=MAYA_APP_DIR):

        if not os.path.isdir(userPath):
            logger.error("Directory doesn't exist: "+ userPath)
	    #路径不存在则退回上次的userPath
            self.populate()
            return



	if type(userPath)==str:
	    self.userPath = os.path.abspath(userPath)
	elif type(userPath)==unicode:
	    self.userPath = os.path.abspath(userPath).encode('utf-8')
	    userPath=self.userPath
	else:
	    response = mc.confirmDialog(
		        title=u'调试显示浏览目录类型...',
		        message=type(userPath),
		        button=[u'是',u'否'],
		        defaultButton=u'否',
		        cancelButton=u'否',
		        dismissString=u'否')	    
	    return

        logger.debug("Reading path: " + userPath)


        self.currentDirTxt.setText(self.userPath)

        # FINDING ASSETS
        self.assets = {}
        folders = {}
        files = {}
	self.infs={}

        ## FIND FOLDERS
        path = os.path.join(userPath, "*/")

        for folder in glob(path):
	    
            name = os.path.basename(os.path.normpath(folder))
	    try:
		UTF8name=name.decode('gb2312')#decode('gb2312').encode('utf8')
		UTF8folder=folder.decode('gb2312')#.decode('gb2312').encode('utf8')
	    except UnicodeEncodeError as err:
		print(err)
		UTF8name=name
		UTF8folder=folder
		name=name.encode('gb2312')
		folder=folder.encode('gb2312')
            folders = {'name': name, 'path': folder, 'type': 'folder','UTF8name':UTF8name,'UTF8path':UTF8folder}

            self.assets[name] = folders

        ## FIND MAYA FILES
        for f in os.listdir(userPath):
            if f.endswith(".ma"):
                name = os.path.splitext(f)[0]
		
                path = os.path.join(userPath, f)
		
		try:
		    UTF8name=name.decode('gb2312')#.decode('gb2312').encode('utf-8')
		    UTF8folder=path.decode('gb2312')#.decode('gb2312').encode('utf-8')
		except UnicodeEncodeError as err:
		    print(err)
		    UTF8name=name
		    UTF8folder=path
		    name=UTF8name.encode('gb2312')
		    path=UTF8folder.encode('gb2312')		  
		
                screenshot = os.path.join(userPath, name + ".jpg")

                if not os.path.isfile(screenshot):
                    screenshot = os.path.join(MAYA_APP_DIR, "ui\\AM_unknown.jpg")

                files = {'name': name, 'path': path, 'screenshot': screenshot, 'type': 'maya','UTF8name':UTF8name,'UTF8path':UTF8folder}

                self.assets[name] = files
		infpath=os.path.join(userPath, name + ".inf")
		if os.path.isfile(infpath):
		    tree=ET.parse(infpath)
		    
		    root=tree.getroot()
		    for ty in root.findall('type'):
			self.infs[name]=ty.text
		    


        # POPULATING LISTWIDGET

        self.listWidget.clear()

        for name in self.assets:
            item = QtWidgets.QListWidgetItem(self.assets[name]['UTF8name'])

            if (self.assets[name]['type'] == 'folder') and (cmp(u'All',self.newComboBox.currentText())==0):
                item.setIcon(QtGui.QIcon(os.path.abspath(os.path.join(MAYA_APP_DIR,  "ui\\AM_folder.png")))) # Folder icon
                
                item.setData(QtCore.Qt.UserRole, 'folder')
		self.listWidget.addItem(item)

            elif self.assets[name]['type'] == 'maya':
		if (cmp(self.infs[name] ,self.newComboBox.currentText())==0) or (cmp(u'All',self.newComboBox.currentText())==0):
		    
		    icon = QtGui.QIcon(self.assets[name]['screenshot'].decode('gb2312'))
		    item.setIcon(icon)
		    
		    item.setData(QtCore.Qt.UserRole, 'maya')
		    self.listWidget.addItem(item)


            

        self.listWidget.sortItems()#sort class
        self.listWidget.setCurrentRow(0) # select first item, to fix right click not showing at startup

        # if directory empty
        if self.listWidget.count() == 0:
            pass
            # TODO: show text saying empty
	return

    def openMenu(self, position):
        currentItem = self.listWidget.currentItem()
        if not currentItem:
            return

        menu = QtWidgets.QMenu(self)

        importAction = menu.addAction("Import")
        moveAction = menu.addAction("Move to")
        renameAction = menu.addAction("Rename")
        deleteAction = menu.addAction("Delete")
        menu.addSeparator()
        newFileAction = menu.addAction("New Asset")
        newFolderAction = menu.addAction("New Folder")
        menu.addSeparator()
        browseAction = menu.addAction("Browse Folder")
        refreshAction = menu.addAction("Refresh List")
        changeStyleAction = menu.addMenu("Change list style")
	#二级菜单
	SmallIconAction = changeStyleAction.addAction("SmallIcon")
	MiddleIconAction = changeStyleAction.addAction("MiddleIcon")
	LargeIconAction = changeStyleAction.addAction("LargeIcon")
	SmallListStyleAction = changeStyleAction.addAction("SmallListStyle")	
	NormalListStyleAction = changeStyleAction.addAction("NormalListStyle")		

        if currentItem.data(QtCore.Qt.UserRole) == 'folder':
            importAction.setVisible(False)
            #moveAction.setVisible(False)

        action = menu.exec_(self.listWidget.mapToGlobal(position))

        if action == importAction:
            self.load()
        elif action == moveAction:
            self.moveItem()
        elif action == renameAction:
            self.rename()
        elif action == deleteAction:
            self.delete()
        elif action == newFileAction:
            self.save()
        elif action == newFolderAction:
            self.newFolder()
        elif action == refreshAction:
            self.populate(self.userPath)
        elif action == SmallIconAction:
            self.ViewStyle.setCurrentIndex(0)
	    self.changeListStyle()
        elif action == MiddleIconAction:
            self.ViewStyle.setCurrentIndex(1)
	    self.changeListStyle()	
        elif action == LargeIconAction:
            self.ViewStyle.setCurrentIndex(2)
	    self.changeListStyle()	    
        elif action == SmallListStyleAction:
            self.ViewStyle.setCurrentIndex(3)
	    self.changeListStyle()	
        elif action == NormalListStyleAction:
            self.ViewStyle.setCurrentIndex(4)
	    self.changeListStyle()	
        elif action == browseAction:
            self.OpenFolderDialog()
    
    def search(self):
        items = self.listWidget.findItems(self.searchFld.text(), QtCore.Qt.MatchContains)

        # Find all items in self.listWidget and store them in allItems
        allItems = []
        for index in xrange(self.listWidget.count()):
             allItems.append(self.listWidget.item(index))

        # hide all items found
        for each in allItems:
	    each.setHidden(True)
         #   self.listWidget.setItemHidden(each, True)

        # Show only the ones that match the search
        for found in items:
	    found.setHidden(False)
	 #   self.listWidget.setItemHidden(found, False)
	#self.listWidget.update()

    def save(self):
	

	#ui_PublishWindow(self.userPath)
	ui_PublishWindow(ifcreate=True,path=self.userPath,fileInput='')
	
	
	"""
        result = mc.promptDialog(
                title='Save asset',
                message='Enter asset name:',
                button=['OK', 'Cancel'],
                defaultButton='OK',
                cancelButton='Cancel',
                dismissString='Cancel')

        if result == 'OK':
            name = mc.promptDialog(query=True, text=True)
            if name == "":
                logger.warning("Please enter a name for your asset")
                self.save()
            else:
                if self.doesItExist(name):
                    # OVERWRITE DIALOG
                    response = mc.confirmDialog(
                        title='Overwrite...',
                        message='An asset with the same name already exists, overwrite?',
                        button=['Yes','No'],
                        defaultButton='No',
                        cancelButton='No',
                        dismissString='No')

                    if response == "No":
                        return


                #### SAVE HERE
                currentScene = mc.file(query=True, sceneName=True)

                savePath = os.path.join(self.userPath, '%s.ma' % name)
                mc.file(rename=savePath)

                if mc.ls(selection=True):
                    mc.file(force=True, type='mayaAscii', exportSelected=True)
                else:
                    mc.file(force=True, save=True, type='mayaAscii')

                mc.file(rename=currentScene) # restore previous scene name

                # SAVE SCREENSHOT
                self.saveScreenshot(name)
                logger.info("Asset saved in " + savePath)
                self.populate(self.userPath)
	    """

    def saveScreenshot(self, name):
        path = os.path.join(self.userPath, '%s.jpg' % name)
	
        shutil.copy2(os.path.join(MAYA_APP_DIR,"ui\\Temp.jpg"), path)
        """  
        activePanel = mc.paneLayout('viewPanes', q=True, pane1=True)
        mc.viewFit()
        mc.setAttr('defaultRenderGlobals.imageFormat', 8)

        # Isolate selection
        if mc.ls(selection=True):
            mc.isolateSelect(activePanel, update=1)
            mc.isolateSelect(activePanel, state=1)
            mc.isolateSelect(activePanel, addSelected=1)

        mc.modelEditor(activePanel, edit=True, sel=False)


        mc.playblast(completeFilename=path, forceOverwrite=True, format='image', width=200, height= 200,
                       showOrnaments=False, startTime=1, endTime=1, viewer=False)


        mc.modelEditor(activePanel, edit=True, sel=True)

        mc.isolateSelect(activePanel, state=0)
        """
        #return path

    def EditInfo(self):
	if not self.CheckAdmin():
	    return
	
	
	
	for item in self.listWidget.selectedItems():
	    itemType = item.data(QtCore.Qt.UserRole)

	    if itemType == 'maya':
		path = self.assets[item.text().encode('gb2312')]['path']
		logger.info("Importing: " + path)
		ui_PublishWindow(ifcreate=False,path=self.userPath,fileInput=item.text())
		#uip = PublishWindow(parent=None,create=False, save=True, sel=False, version=None,pathDir=self.userPath,fileName=item.text())
		#uip.show()		
		
#		mc.file(path, i=True, usingNamespaces=False)
		return

	    elif itemType == 'folder':
		newPath = os.path.join(self.userPath, item.text())
		logger.debug("Populating list with this path: " + newPath)
		self.rename()
		return


    def load(self):
        """This loads the currently selected assets, or opens the folder"""
        for item in self.listWidget.selectedItems():
            itemType = item.data(QtCore.Qt.UserRole)

            if itemType == 'maya':
                path = self.assets[item.text().encode('gb2312')]['path']
                logger.info("Importing: " + path)
                mc.file(path, i=True, usingNamespaces=False)

            elif itemType == 'folder':
		if not self.CheckAdmin():
		    return		
                newPath = os.path.join(self.userPath, item.text().encode('gb2312'))
                logger.debug("Populating list with this path: " + newPath)
                self.populate(newPath)
		return

    def delete(self):
	# CONFIRMATION DIALOG
	if not self.CheckAdmin():
	    return
	
	
	
	
	
	
	
	
	
	
	
        response = mc.confirmDialog(
            title='Deleting...',
            message='Are you sure?',
            button=['Yes','No'],
            defaultButton='No',
            cancelButton='No',
            dismissString='No')

        if response == "No":
            return

        for item in self.listWidget.selectedItems():
            itemType = item.data(QtCore.Qt.UserRole)

            if itemType == 'maya':
                path = os.path.join(self.userPath, '%s.ma' % item.text())
                screenshot = os.path.join(self.userPath, '%s.jpg' % item.text())
                infpath=os.path.join(self.userPath, '%s.inf' % item.text())
                try:
                    os.remove(path)
                    os.remove(screenshot)
		    os.remove(infpath)
                except OSError:
                    logger.error("Error deleting: "+item.text())


            elif itemType == 'folder':
                # CONFIRMATION DIALOG
                response = mc.confirmDialog(
                    title='Deleting...',
                    message='Deleting the folder ' + item.text()+ ' will delete all of its contents, are you sure?',
                    button=['Yes','No'],
                    defaultButton='No',
                    cancelButton='No',
                    dismissString='No')

                if response == "Yes":
                    path = os.path.join(self.userPath, item.text())

                    try:
                        shutil.rmtree(path, ignore_errors=False, onerror=None)
                        logger.info("Directory deleted: " + item.text())
                    except OSError:
                        logger.error("Error deleting: "+ item.text())
                elif response == "No":
                    logger.info("Directory not deleted: " + item.text())

        self.populate(self.userPath)

    def rename(self):
        for item in self.listWidget.selectedItems():
            result = mc.promptDialog(
                title='Rename Object',
                message='Enter new name for:\n'+item.text(),
                button=['OK', 'Cancel'],
                defaultButton='OK',
                cancelButton='Cancel',
                dismissString='Cancel')

            if result == 'OK':
                newName = mc.promptDialog(query=True, text=True)

                if not newName: # Empty field
                    logger.error("Please insert a name")
                    self.populate(self.userPath)
                    #return

                elif newName==item.text(): # New name == old name
                    logger.error("Please choose a different name")
                    self.populate(self.userPath)
                    return

                elif newName in self.assets:# New name already exists

                    if item.data(QtCore.Qt.UserRole) != self.assets[newName]['type']: # if different type stop script
                        logger.error("An element of a different type with the same name already exist, please choose a different name")
                        return

                    response = mc.confirmDialog(
                        title='Attention',
                        message='An element with the same name already exists, do you want to overwrite it?',
                        button=['Yes','No'],
                        defaultButton='No',
                        cancelButton='No',
                        dismissString='No')
                    if response == "No":
                        return
                    elif response == "Yes":
                        if item.data(QtCore.Qt.UserRole) == "maya":
			    if os.path.isfile(os.path.join(self.userPath, newName + ".ma")):
				os.remove(os.path.join(self.userPath, newName + ".ma"))
			    if os.path.isfile(os.path.join(self.userPath, newName + ".jpg")):
			        os.remove(os.path.join(self.userPath, newName + ".jpg"))
                        elif item.data(QtCore.Qt.UserRole) == "folder":
                            shutil.rmtree(os.path.join(self.userPath, newName))

                if item.data(QtCore.Qt.UserRole) == "maya":
                    os.rename(os.path.join(self.userPath, item.text() + ".ma"), os.path.join(self.userPath, newName + ".ma"))
                    os.rename(os.path.join(self.userPath, item.text() + ".jpg"), os.path.join(self.userPath, newName + ".jpg"))
                elif item.data(QtCore.Qt.UserRole) == "folder":
                    shutil.move(os.path.join(self.userPath, item.text()), os.path.join(self.userPath, newName))

        self.populate(self.userPath)

    def moveItem(self):
	
	if not self.CheckAdmin():
	    return
	
	
        destination = mc.fileDialog2(caption='Move to:', fileMode=2, okCaption='Move', startingDirectory=self.userPath)[0]
        if not destination:
            return
        for item in self.listWidget.selectedItems():
            try:
                shutil.move(self.assets[item.text().encode('gb2312')]['path'], destination)

                # copy screenshot too if maya file
                itemType = item.data(QtCore.Qt.UserRole)
                if itemType == 'maya':
		    return
                    #shutil.move(self.assets[item.text().encode('gb2312')]['screenshot'], destination)
            except:
                logger.error("Error copying " + item.text() + " to: " + destination + "\nThe file/folder already exists")



	
        self.populate(destination.decode('gb2312'))

    def doesItExist(self, getName):
        if getName in self.assets:
            return True
        else:
            return False

    def newFolder(self):
	if not self.CheckAdmin():
	    return	
        result = mc.promptDialog(
                title='Folder name',
                message='Enter a name for the new folder',
                button=['OK', 'Cancel'],
                defaultButton='OK',
                cancelButton='Cancel',
                dismissString='Cancel')

        if result == 'OK':
            newName = mc.promptDialog(query=True, text=True)
            newPath = os.path.join(self.userPath, newName)

            if not os.path.exists(newPath):
                os.makedirs(newPath)
                self.populate(newPath)
            else:
                logger.error("A directory with the same name already exists, please choose a different name.")
                self.newFolder()

    def openExplorer(self):
        path = self.userPath
        import subprocess
        try:
            os.startfile(path)
        except:
            subprocess.Popen(['xdg-open', path])

    def test(self, *args):
        print "test"

##################################




def ImportAndExportMesh():
    axi=mc.upAxis( q=True, axis=True )    
    response0 = mc.confirmDialog(
                title=u'选择...',
                message=u'请选择下列功能:',
                button=[u'Z轴向上',u'Y轴向上',u'转换文件',u'退出'],
                defaultButton=u'Z轴向上',
                cancelButton=u'退出',
                dismissString=u'退出')
    if response0==u"Z轴向上":
	if axi=="y":
	    mc.upAxis(ax='z',rv=True)
	return
    elif response0==u"Y轴向上":
	if axi=="z":	
	    mc.upAxis(ax='y',rv=True)
	return
    elif response0==u"退出":
	return
    response = mc.confirmDialog(
                title=u'Warning...',
                message=u'此功能需要新建一个场景.请检查之前场景是否保存.若未保存请选否退出。\n是否继续?',
                button=[u'Yes',u'No'],
                defaultButton=u'No',
                cancelButton=u'No',
                dismissString=u'No')    
    if response=="No":
	return

    #select import file
    fileName,fileType = QtWidgets.QFileDialog.getOpenFileName(None,
	                                   u'选取需要改变坐标轴的fbx文件',
	                                   './',
	                                   'All Files(*.fbx);;Fbx Files(*.fbx)')
 
    #create new scene
    scene = mc.file(new=True,force=True)
    
    #make Z up

    print "Old"+axi+"Up\n"
    if axi!="z":
	    mc.upAxis( ax='z', rv=True )
    
    #import fbx
    path = fileName
    mc.file(path,i=True,usingNamespaces=False,type = 'FBX')
    
    #select all
    mc.select(clear=True )
    mc.select(ado=True,hi=True)

    #Save fbx
    #savePath = os.path.join(self.pathDir, '%s.fbx' % name)
    savePath=fileName
    #mc.file(rename=savePath)
    #mel.eval('FBXExportFileVersion "FBX201000"')
    #mel.eval('FBXConvertUnitString "cm"')
    #mel.eval('FBXExportInputConnections -v 0')
    full_file_path=savePath.replace('\\','/')
    mel.eval('FBXExportInAscii -v true')
    mel.eval("FBXExport -f \""+full_file_path+"\" -s")
    
    #delet all
#    mc.select(ado=True,adn=True,hi=True)
#    mc.delete()
    scene = mc.file(new=True,force=True)    
    
    #reset axis
    if axi!="z":
	    mc.upAxis( ax='y', rv=True )

    result = mc.confirmDialog(
		title=u'消息窗口',
		message=u'已经成功将fbx转换为Z轴向上',
		button=['OK'],
		defaultButton='OK',
		cancelButton='OK',
                dismissString='OK')	



##################################
def install():
    env = 'ONION_FILES_ROOT'
    modules = 'Modules'
    title = u'设置模型库位置'

    maya = mc.about(v = True)
    if len(maya) == 4:
	maya = maya + ' x64'
    url = 'http://pepperusso.uk/scripts/assetManager/icon.png'
    pathX="Z:\\scripts\\Storage\\"
    root=pathX
    imageName = 'assetManager.png'
    #若不存在存储模型路径，弹出对话框进行路径添加
    if not os.getenv(env):
	    
	if not os.path.exists(pathX):
	    userPath=mc.fileDialog2(caption=u'请选择模型库的网络路径', fileMode=2, okCaption='Select')[0]
	    if userPath!=None:
		root=userPath
	    else:
		return
	#增加系统标注模型路径	
	if mc.about(win=True):
	    command='SETX '+env+' '+root
	elif mc.about(li=True):
	    command = 'setenv ' + env + ' ' + root
	try:
	    os.popen(command)
	except:
	    message = env + ' was NOT succesfully set to: ' + root + '\nError: ' + command
	else:
	    message=env + ' was succesfully set to: ' + root
	    os.environ[env]=root
    name = 'Assert: ' + os.path.basename(root)
    tooltip = "AM: " + root
    iconLabel =u'模型库'# os.path.basename(root)
	#import sys,os\nsys.path.append(os.getenv('ONION_FILES_ROOT'))\n
    command = "import sys,os\nsys.path.append(os.getenv('ONION_FILES_ROOT'))\nimport mycheck5\nmycheck5.start()\n"#ui_snapshot(False, False, False)" #a='123'\nprint a"
    doubleClickCmd = "aa='456'\nprint aa"
    version = mc.about(version=True)
	
    appPath = MAYA_APP_DIR
    iconPath = os.path.join(appPath,'ui\\icon.png')
    try:
	urllib.urlretrieve(url, iconPath)
    except:
	iconPath = os.path.join(appPath,'ui\\icon.png')
    tab_layout=mel.eval('$pytmp = $gShelfTopLevel')
    mc.deleteUI('ONION_TOOLS',layout=True)
    shelf = mc.shelfLayout('ONION_TOOLS', parent=tab_layout)
    mc.setParent('ONION_TOOLS')
    mc.shelfButton(image=iconPath, command=command, dcc=doubleClickCmd, label=name, annotation=tooltip, imageOverlayLabel=iconLabel, overlayLabelColor=(1,1,1), overlayLabelBackColor=(random.random(), random.random(), random.random(), .5))
    
    name = 'XChange ZUp' #+ os.path.basename(root)
    tooltip = "AM: " #+ root
    iconLabel =u'转Z轴'# os.path.basename(root)
	#import sys,os\nsys.path.append(os.getenv('ONION_FILES_ROOT'))\n
    command = "import sys,os\nsys.path.append(os.getenv('ONION_FILES_ROOT'))\nimport mycheck5\nmycheck5.ImportAndExportMesh()\n"#ui_snapshot(False, False, False)" #a='123'\nprint a"
    doubleClickCmd = "aa='789'\nprint aa"
    version = mc.about(version=True)
	
    appPath = MAYA_APP_DIR
    iconPath = os.path.join(appPath,'ui\\icon.png')
    try:
	urllib.urlretrieve(url, iconPath)
    except:
	iconPath = os.path.join(appPath,'ui\\icon.png')
    tab_layout=mel.eval('$pytmp = $gShelfTopLevel')
    mc.deleteUI('ONION_TOOLS',layout=True)
    shelf = mc.shelfLayout('ONION_TOOLS', parent=tab_layout)
    mc.setParent('ONION_TOOLS')
    mc.shelfButton(image=iconPath, command=command, dcc=doubleClickCmd, label=name, annotation=tooltip, imageOverlayLabel=iconLabel, overlayLabelColor=(1,1,1), overlayLabelBackColor=(random.random(), random.random(), random.random(), .5))    
    #channelBoxUseManips.png buttonManip.svg
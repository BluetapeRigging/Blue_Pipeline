from __future__ import absolute_import
'''
version: 1.0.0
date: 21/04/2020

#----------------
content:

#----------------
how to:

try:
    import importlib;from importlib import reload
except:
    import imp;from imp import reload

import Blue_Pipeline
from Blue_Pipeline.UI.FolderName import load_pyname
reload(load_pyname)

try:cBlueUI.close()
except:pass
cBlueUI = load_pyname.BlueUI()
cBlueUI.show()

#----------------
dependencies:

QT FILE
ICONS
JSON FILES

#----------------
author:  Esteban Rodriguez <info@renderdemartes.com>

'''
# -------------------------------------------------------------------
try:
    from shiboken6 import wrapInstance
    from PySide6 import QtGui, QtCore
    from PySide6 import QtUiTools
    from PySide6 import QtWidgets
    from PySide6.QtWidgets import *
except:
    from shiboken2 import wrapInstance
    from PySide2 import QtGui, QtCore
    from PySide2 import QtUiTools
    from PySide2 import QtWidgets
    from PySide2.QtWidgets import *

import maya.OpenMayaUI as omui
from functools import partial
from maya import OpenMaya
import maya.cmds as cmds
import maya.mel as mel

import os
try:
    import importlib;from importlib import reload
except:
    import imp;from imp import reload

import sys
import json
import glob
import pprint
from pathlib import Path
from Blue_Pipeline.Utils.Helpers.decorators import undo


# -------------------------------------------------------------------

# QT WIndow!
FOLDER_NAME = 'Folder Name'
Title = 'Title'
UI_File = 'UI_FILE_NAME.ui'

# QT WIndow!
PATH = os.path.dirname(__file__)
PATH = Path(PATH)
PATH_PARTS = PATH.parts[:-2]
FOLDER=''
for f in PATH_PARTS:
	FOLDER = os.path.join(FOLDER, f)

IconsPath = os.path.join(FOLDER, 'Icons')



# -------------------------------------------------------------------

import Blue_Pipeline
import Blue_Pipeline.UI
from Blue_Pipeline.UI import QtBlueWindow
reload(QtBlueWindow)
Qt_Blue = QtBlueWindow.Qt_Blue()

# -------------------------------------------------------------------


def maya_main_window():
	main_window_ptr = omui.MQtUtil.mainWindow()
	return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class BlueUI(QtBlueWindow.Qt_Blue):

	def __init__(self):
		super(BlueUI, self).__init__()

		self.setWindowTitle(Title)

		self.designer_loader_child(path=os.path.join(FOLDER, 'UI', FOLDER_NAME), ui_file=UI_File)
		self.set_title(Title)

		self.create_layout()
		self.create_connections()

	# -------------------------------------------------------------------

	def create_layout(self):
		"""

		Returns:

		"""


	def create_connections(self):
		"""

		Returns:

		"""

		#self.ui.button.clicked.connect(self.create_block)

	# -------------------------------------------------------------------

	# CLOSE EVENTS _________________________________
	def closeEvent(self, event):
		''


# -------------------------------------------------------------------

if __name__ == "__main__":

	try:
		cBlueUI.close()  # pylint: disable=E0601
		cBlueUI.deleteLater()
	except:
		pass
	cBlueUI = BlueUI()
	cBlueUI.show()

# -------------------------------------------------------------------

'''
#Notes






'''
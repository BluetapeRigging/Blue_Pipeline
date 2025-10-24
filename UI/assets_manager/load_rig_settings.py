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
from Blue_Pipeline.UI.assets_manager import load_rig_settings
reload(load_rig_settings)

try:cRigSettingsUI.close()
except:pass
cRigSettingsUI = load_rig_settings.RigSettingsUI()
cRigSettingsUI.show()

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
import re
import subprocess
import tempfile

try:
    import importlib;from importlib import reload
except:
    import imp;from imp import reload

import sys
import json
import glob
import pprint
from pathlib import Path


# -------------------------------------------------------------------

# QT WIndow!
FOLDER_NAME = 'assets_manager'
Title = 'Rig Settings'
UI_File = 'rig_settings.ui'

# QT Window!
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


class RigSettingsUI(QtBlueWindow.Qt_Blue):

    def __init__(self, file_path=None):
        super(RigSettingsUI, self).__init__()

        self.setWindowTitle(Title)

        self.designer_loader_child(path=os.path.join(FOLDER, 'UI', FOLDER_NAME), ui_file=UI_File)
        self.set_title(Title)

        self.file_path = file_path
        if not self.file_path:
            return
        self.current_file = os.path.basename(self.file_path)
        self.main_path = self.get_main_path()

        self.create_layout()
        self.create_connections()

    # -------------------------------------------------------------------

    def get_main_path(self):
        return os.path.dirname(self.file_path)

    def set_blue_buttons(self):
        buttons = [
            self.ui.save_skins_button,
            self.ui.save_ctrls_button,
            self.ui.save_guide_button,
            self.ui.load_skins_button,
            self.ui.load_ctrls_button,
            self.ui.load_guide_button
        ]

        for btn in buttons:
            btn.setObjectName("BlueButton")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def create_layout(self):
        self.set_blue_buttons()
        self.populate_files_combo()

    def create_connections(self):
        """

        Returns:

        """

        #self.ui.button.clicked.connect(self.create_block)

    def populate_files_combo(self):
        # Get all files in the folder
        files = glob.glob(os.path.join(self.main_path, '*'))

        # Filter only .ma and .mb files
        maya_files = [f for f in files if f.endswith(('.ma', '.mb'))]

        # Sort by modification time (newest first)
        maya_files.sort(key=os.path.getmtime, reverse=True)

        # Clear combo box
        self.ui.files_combo_box.clear()

        # Add basenames but store full paths as item data
        for f in maya_files:
            basename = os.path.basename(f)
            self.ui.files_combo_box.addItem(basename, userData=f)

        #Set Current
        index = self.ui.files_combo_box.findText(self.current_file)
        if index != -1:
            self.ui.files_combo_box.setCurrentIndex(index)

    # -------------------------------------------------------------------

    # CLOSE EVENTS _________________________________
    def closeEvent(self, event):
        ''


# -------------------------------------------------------------------

if __name__ == "__main__":

    try:
        cRigSettingsUI.close()  # pylint: disable=E0601
        cRigSettingsUI.deleteLater()
    except:
        pass
    cRigSettingsUI = RigSettingsUI()
    cRigSettingsUI.show()

# -------------------------------------------------------------------

'''
#Notes






'''
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
from Blue_Pipeline.UI.assets_manager import load_save_wip
reload(load_save_wip)

cSaveWIP = load_save_wip.SaveWIP()
cSaveWIP = SaveWIP(save_path=wip_save_path, asset_name="Cube")
cSaveWIP.setWindowModality(QtCore.Qt.ApplicationModal)
cSaveWIP.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint | QtCore.Qt.CustomizeWindowHint)
cSaveWIP.show()

#----------------
dependencies:

QT FILE
ICONS
JSON FILES

#----------------
author:  Esteban Rodriguez <info@renderdemartes.com>

'''
# -------------------------------------------------------------------
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

import re
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
FOLDER_NAME = 'assets_manager'
Title = 'Save WIP'
UI_File = 'save_wip.ui'

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


class SaveWIP(QtBlueWindow.Qt_Blue):
    def __init__(self, save_path, asset_name="Cube", mode="WIP"):
        super(SaveWIP, self).__init__()
        self.save_path = save_path
        self.asset_name = asset_name  # e.g., 'Cube'
        self.mode = mode
        self.task_name = os.path.basename(save_path)  # e.g., 'Model'
        self.setWindowTitle(Title)

        self.setFixedSize(400, 200)
        self.designer_loader_child(path=os.path.join(FOLDER, 'UI', FOLDER_NAME), ui_file=UI_File)
        self.set_title(Title)

        self.create_layout()
        self.create_connections()

    # -------------------------------------------------------------------

    def create_layout(self):
        """

        Returns:

        """
        self.set_blue_buttons()


    def create_connections(self):
        """

        Returns:

        """
        self.ui.save_wip.clicked.connect(self.save_current_scene_as_wip)

        #self.ui.button.clicked.connect(self.create_block)

    def set_blue_buttons(self):
        buttons = [
            self.ui.save_wip
        ]

        for btn in buttons:
            btn.setObjectName("BlueButton")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    # -------------------------------------------------------------------


    def get_next_version_number(self):
        pattern = f"{self.asset_name}_{self.task_name}_"
        print(self.save_path)
        search_path = os.path.join(self.save_path, self.mode)
        existing_files = [f for f in os.listdir(search_path) if f.endswith(".ma")]
        print(existing_files)
        versions = []
        for f in existing_files:
            match = re.search(r'_(\d{4})_', f)
            if match:
                versions.append(int(match.group(1)))
        next_version = max(versions) + 1 if versions else 1
        return f"{next_version:04d}"

    def clean_comment(self, text):
        first_line = text.strip().split('\n')[0]
        cleaned = ''.join(c if c.isalnum() else '_' for c in first_line)
        return cleaned[:30]  # limit length if needed

    def save_current_scene_as_wip(self):
        import getpass
        import datetime

        details = self.ui.details_plain_text.toPlainText()
        user = getpass.getuser()
        time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        version_str = self.get_next_version_number()
        comment_str = self.clean_comment(details)

        # Remove b0001_ prefix if present in asset_name or task_name
        clean_asset = self.asset_name.split('_', 1)[-1] if '_' in self.asset_name else self.asset_name
        clean_task = self.task_name.split('_', 1)[-1] if '_' in self.task_name else self.task_name

        filename = f"{clean_asset}_{clean_task}_{version_str}_{comment_str}.ma"
        full_path = os.path.join(self.save_path, self.mode, filename)

        # Save current scene
        try:
            cmds.file(rename=full_path)
            cmds.file(save=True, type="mayaAscii")
        except Exception as e:
            cmds.warning(f"Failed to save Maya file: {e}")
            return

        # Save accompanying .json log
        json_data = {
            "user": user,
            "datetime": time_str,
            "details": details,
            "filename": filename
        }
        json_path = full_path.replace(".ma", ".json")
        try:
            with open(json_path, "w") as f:
                json.dump(json_data, f, indent=4)
            cmds.inViewMessage(amg=f"Saved: <hl>{filename}</hl>", pos='topCenter', fade=True)
        except Exception as e:
            cmds.warning(f"Failed to save WIP JSON: {e}")

        self.close()

    # CLOSE EVENTS _________________________________
    def closeEvent(self, event):
        ''


# -------------------------------------------------------------------

if __name__ == "__main__":

    try:
        cSaveWIP.close()  # pylint: disable=E0601
        cSaveWIP.deleteLater()
    except:
        pass
    cSaveWIP = SaveWIP()
    cSaveWIP.show()

# -------------------------------------------------------------------

'''
#Notes






'''
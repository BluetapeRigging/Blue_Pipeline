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
from Blue_Pipeline.UI.assets_manager import load_publish_asset
reload(load_publish_asset)

cPublishAsset = load_publish_asset.PublishAsset(save_path=wip_save_path, asset_name="Cube")
cPublishAsset.setWindowModality(QtCore.Qt.ApplicationModal)
cPublishAsset.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint | QtCore.Qt.CustomizeWindowHint)
cPublishAsset.show()

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
Title = 'Publish Asset'
UI_File = 'publish_asset.ui'

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


class PublishAsset(QtBlueWindow.Qt_Blue):
    def __init__(self, save_path, asset_name="Cube", mode="Publish"):
        super(PublishAsset, self).__init__()
        self.save_path = save_path
        self.asset_name = asset_name  # e.g., 'Cube'
        self.mode = mode
        self.task_name = os.path.basename(save_path)  # e.g., 'Model'
        self.setWindowTitle(Title)

        self.setFixedSize(400, 600)
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
        self.ui.export_name_line.setText(self.get_versioning_name())

    def create_connections(self):
        """

        Returns:

        """
        self.ui.publish_asset_button.clicked.connect(self.publish_asset)
        self.ui.publish_preset_combo.currentIndexChanged.connect(self.update_export_name)


    def set_blue_buttons(self):
        buttons = [
            self.ui.publish_asset_button
        ]

        for btn in buttons:
            btn.setObjectName("BlueButton")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    # -------------------------------------------------------------------
    def get_next_version_number(self, folder_path, name, task, padding=4):
        pattern = re.compile(rf"^{re.escape(name)}_{re.escape(task)}_(\d+)\.ma$")
        versions = []

        for f in os.listdir(folder_path):
            if f.endswith(".ma"):
                match = pattern.match(f)
                if match:
                    versions.append(int(match.group(1)))

        if versions:
            next_version = max(versions) + 1
        else:
            next_version = 1

        return str(next_version).zfill(padding)

    def publish_asset(self):

        import getpass
        import datetime

        # Remove b0001_ prefix if present in asset_name or task_name
        clean_asset = self.asset_name.split('_', 1)[-1] if '_' in self.asset_name else self.asset_name
        clean_task = self.task_name.split('_', 1)[-1] if '_' in self.task_name else self.task_name

        version_str = self.get_next_version_number(folder_path=os.path.join(self.save_path, self.mode),
                                                   name=clean_asset,
                                                   task=clean_task)
        user = getpass.getuser()
        time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self.ui.publish_preset_combo.currentText() == 'Versioning':
            filename = self.get_versioning_name()
        elif self.ui.publish_preset_combo.currentText() == 'Single File':
            filename  = f"{clean_asset}_{clean_task}.ma"
        elif self.ui.publish_preset_combo.currentText() == 'Selected as FBX':
            #FBX will stop after export here
            filename = f"{clean_asset}_{clean_task}.fbx"
            full_path = os.path.join(self.save_path, self.mode, filename)
            if not cmds.pluginInfo("fbxmaya", q=True, loaded=True):
                cmds.loadPlugin("fbxmaya")
            cmds.file(full_path, force=True, options="v = 0", type="FBX export", exportSelected=True)
            self.in_view_message(full_path)
            self.close()
            return
        elif self.ui.publish_preset_combo.currentText() == 'Selected Asset as Alembic':
            filename = self.get_versioning_name('.abc')
            full_path = os.path.join(self.save_path, self.mode, filename)
            full_path = os.path.normpath(full_path)
            print(full_path)
            if not cmds.pluginInfo("AbcExport", q=True, loaded=True):
                cmds.loadPlugin("AbcExport")
            self.export_alembic_static(full_path)
            self.in_view_message(full_path)
            self.close()
            return
        elif self.ui.publish_preset_combo.currentText() == 'Selected Animation as Alembic':
            filename = self.get_versioning_name('.abc')
            full_path = os.path.join(self.save_path, self.mode, filename)
            full_path = os.path.normpath(full_path)
            if not cmds.pluginInfo("AbcExport", q=True, loaded=True):
                cmds.loadPlugin("AbcExport")
            self.export_alembic_animation(full_path)
            self.in_view_message(full_path)
            self.close()
            return

        #Versioning and single file continue
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
            "filename": filename
        }
        json_path = full_path.replace(".ma", ".json")
        try:
            with open(json_path, "w") as f:
                json.dump(json_data, f, indent=4)
            cmds.inViewMessage(amg=f"Saved: <hl>{filename}</hl>", pos='topCenter', fade=True)
        except Exception as e:
            cmds.warning(f"Failed to save WIP JSON: {e}")
        self.in_view_message(full_path)
        self.close()

    def in_view_message(self, full_path):
        cmds.inViewMessage(
            amg=f"<span style='color:yellow;'>Alembic Exported:</span> {full_path}",
            pos="topCenter",
            fade=True
        )

    def export_alembic_static(self, full_path, selection=None):
        # Normalize path for Alembic
        full_path = os.path.normpath(full_path).replace("\\", "/")

        # Ensure directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Get proper selection (transforms only)
        if selection is None:
            selection = cmds.ls(sl=True, long=True)

        selection = cmds.ls(selection, dag=True, type="transform", long=True)

        if not selection:
            cmds.warning("Nothing selected for Alembic export.")
            return

        # Build roots
        root_flags = " ".join([f'-root "{obj}"' for obj in selection])

        # Build job
        job = f'-frameRange 1 1 -writeVisibility -worldSpace {root_flags} -file "{full_path}"'

        # Run export
        cmds.AbcExport(j=job)
        print(f"[OK] Static Alembic exported → {full_path}")

    def export_alembic_animation(self, full_path, selection=None, start=None, end=None):
        full_path = os.path.normpath(full_path).replace("\\", "/")
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        if selection is None:
            selection = cmds.ls(sl=True, long=True)

        selection = cmds.ls(selection, dag=True, type="transform", long=True)

        if not selection:
            cmds.warning("Nothing selected for Alembic animation export.")
            return

        if start is None:
            start = cmds.playbackOptions(q=True, min=True)
        if end is None:
            end = cmds.playbackOptions(q=True, max=True)

        root_flags = " ".join([f'-root "{obj}"' for obj in selection])

        job = (
            f'-frameRange {start} {end} '
            f'-uvWrite -writeVisibility -worldSpace {root_flags} '
            f'-file "{full_path}"'
        )

        cmds.AbcExport(j=job)
        print(f"[OK] Animated Alembic exported → {full_path}")

    def get_versioning_name(self, ext='.ma'):
        """
        Returns the full export filename that will be used on publish,
        without actually saving.
        """
        # Clean asset and task (same as in publish_asset)
        clean_asset = self.asset_name.split('_', 1)[-1] if '_' in self.asset_name else self.asset_name
        clean_task = self.task_name.split('_', 1)[-1] if '_' in self.task_name else self.task_name

        # Compute next version string
        version_str = self.get_next_version_number(
            folder_path=os.path.join(self.save_path, self.mode),
            name=clean_asset,
            task=clean_task
        )

        # Build filename
        filename = f"{clean_asset}_{clean_task}_{version_str}{ext}"
        return filename

    def update_export_name(self, index):
        """
        Update the export line edit based on combobox selection
        """
        preset = self.ui.publish_preset_combo.currentText()

        clean_asset = self.asset_name.split('_', 1)[-1] if '_' in self.asset_name else self.asset_name
        clean_task = self.task_name.split('_', 1)[-1] if '_' in self.task_name else self.task_name

        if preset == 'Versioning':
            filename = self.get_versioning_name()
        elif preset == 'Single File':
            filename = f"{clean_asset}_{clean_task}.ma"
        elif preset == 'Selected as FBX':
            filename = f"{clean_asset}_{clean_task}.fbx"
        elif preset == 'Selected Asset as Alembic':
            filename = self.get_versioning_name('.abc')
        elif preset == 'Selected Animation as Alembic':
            filename = self.get_versioning_name('.abc')
        else:
            filename = f"{clean_asset}_{clean_task}"

        self.ui.export_name_line.setText(filename)


    # CLOSE EVENTS _________________________________
    def closeEvent(self, event):
        ''


# -------------------------------------------------------------------

if __name__ == "__main__":

    try:
        cPublishAsset.close()  # pylint: disable=E0601
        cPublishAsset.deleteLater()
    except:
        pass
    cPublishAsset = PublishAsset()
    cPublishAsset.show()

# -------------------------------------------------------------------

'''
#Notes






'''
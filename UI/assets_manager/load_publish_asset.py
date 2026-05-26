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

from Blue_Pipeline.Checks.base_check import BaseCheck

# Maps the comboBox display name to the checks sub-folder name
DEPT_MAP = {
    'Rig':   'rigging',
    'Model': 'modeling',
}

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
        self._check_rows = []
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
        self._set_smart_department()
        self._build_check_rows()

    def create_connections(self):
        """

        Returns:

        """
        self.ui.publish_asset_button.clicked.connect(self.publish_asset)
        self.ui.publish_preset_combo.currentIndexChanged.connect(self.update_export_name)
        self.ui.run_checks_button.clicked.connect(self._run_checks)
        self.ui.comboBox.currentIndexChanged.connect(self._build_check_rows)


    # ------------------------------------------------------------------ check system

    def _log_message(self, message):
        """Append a message to the check log."""
        self.ui.check_log.appendPlainText(message)

    def _clear_log(self):
        """Clear the check log."""
        self.ui.check_log.clear()

    def _set_smart_department(self):
        """Try to match the task_name to a combo box option."""
        task_lower = self.task_name.lower()
        for i in range(self.ui.comboBox.count()):
            item_text = self.ui.comboBox.itemText(i).lower()
            if task_lower == item_text:
                self.ui.comboBox.setCurrentIndex(i)
                return
        # If no match, default to first item (usually Model)
        self.ui.comboBox.setCurrentIndex(0)

    def _load_checks_from_folder(self, folder_name):
        """Load checks from a specific folder.
        
        Parameters
        ----------
        folder_name : str
            The folder name under Blue_Pipeline/Checks/ (e.g., 'modeling', 'general')
        
        Returns
        -------
        list : List of BaseCheck instances
        """
        checks_dir = os.path.join(FOLDER, 'Checks', folder_name)
        instances = []

        if not os.path.isdir(checks_dir):
            return instances

        for filename in sorted(os.listdir(checks_dir)):
            if filename.startswith('_') or not filename.endswith('.py'):
                continue
            module_name = 'Blue_Pipeline.Checks.{}.{}'.format(folder_name, filename[:-3])
            try:
                module = importlib.import_module(module_name)
                reload(module)
                for attr_name in dir(module):
                    cls = getattr(module, attr_name)
                    if (
                        isinstance(cls, type)
                        and issubclass(cls, BaseCheck)
                        and cls is not BaseCheck
                    ):
                        instances.append(cls())
            except Exception as e:
                cmds.warning('Failed to load check {}: {}'.format(module_name, e))

        return instances

    def _discover_checks(self, department):
        """Import and instantiate every BaseCheck subclass found in
        Blue_Pipeline/Checks/<dept_folder>/ and Blue_Pipeline/Checks/general/.
        Returns a list of instances."""
        dept_folder = DEPT_MAP.get(department, department.lower())
        instances = []

        # Load department-specific checks
        instances.extend(self._load_checks_from_folder(dept_folder))

        # Load general checks (available for all departments)
        instances.extend(self._load_checks_from_folder('general'))

        return instances

    def _build_check_rows(self):
        """Clear check_layout and rebuild rows for the selected department."""
        layout = self.ui.check_layout
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._clear_log()
        self._check_rows = []
        dept   = self.ui.comboBox.currentText()
        checks = self._discover_checks(dept)

        for check in checks:
            row = self._create_check_row(check)
            layout.addWidget(row)
            self._check_rows.append(row)

    def _create_check_row(self, check_instance):
        """Build and return a single check-row QWidget."""
        row    = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(row)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(6)

        name_lbl = QtWidgets.QLabel(check_instance.name)
        name_lbl.setMinimumWidth(150)

        status_btn = QtWidgets.QPushButton('Pending')
        status_btn.setFixedWidth(70)
        status_btn.setEnabled(False)
        status_btn.setStyleSheet('background-color: #555555; color: #aaaaaa;')

        fix_btn = QtWidgets.QPushButton('Auto Fix')
        fix_btn.setFixedWidth(70)
        fix_btn.setVisible(False)
        if check_instance.can_fix:
            fix_btn.clicked.connect(partial(self._run_autofix, row))

        layout.addWidget(name_lbl)
        layout.addStretch()
        layout.addWidget(status_btn)
        layout.addWidget(fix_btn)

        # stash references on the widget for later updates
        row._check      = check_instance
        row._status_btn = status_btn
        row._fix_btn    = fix_btn

        return row

    def _run_checks(self):
        """Run every check and update its row's status button."""
        self._clear_log()
        self._log_message('Running checks for {}...'.format(self.ui.comboBox.currentText()))
        self._log_message('')
        
        for row in self._check_rows:
            try:
                passed = row._check.check()
            except Exception as e:
                cmds.warning('Check "{}" raised an error: {}'.format(row._check.name, e))
                passed = False

            row._status_btn.setEnabled(True)
            if passed:
                row._status_btn.setText('OK')
                row._status_btn.setStyleSheet('background-color: #4CAF50; color: white;')
                row._fix_btn.setVisible(False)
                self._log_message('[OK] {}'.format(row._check.name))
            else:
                row._status_btn.setText('Error')
                row._status_btn.setStyleSheet('background-color: #F44336; color: white;')
                if row._check.can_fix:
                    row._fix_btn.setVisible(True)
                    self._log_message('[ERROR] {} [FIXABLE]'.format(row._check.name))
                else:
                    self._log_message('[ERROR] {}'.format(row._check.name))
                
                # Log detailed failure info if available
                if hasattr(row._check, 'failures') and row._check.failures:
                    self._log_failure_details(row._check)
        
        self._log_message('')
        self._log_message('Checks complete.')

    def _log_failure_details(self, check_instance):
        """Log detailed information about a check's failures."""
        check_name = check_instance.name
        
        if check_name == "Controls at Default Values" and hasattr(check_instance, 'failures'):
            # Group failures by control
            by_ctrl = {}
            for ctrl, attr, current, expected in check_instance.failures:
                if ctrl not in by_ctrl:
                    by_ctrl[ctrl] = []
                by_ctrl[ctrl].append((attr, current, expected))
            
            for ctrl, attrs in sorted(by_ctrl.items()):
                ctrl_short = ctrl.split('|')[-1]  # Just the short name
                attr_list = ', '.join(['{}: {} (expect {})'.format(a, round(c, 3), round(e, 3)) 
                                       for a, c, e in attrs])
                self._log_message('  > {}: {}'.format(ctrl_short, attr_list))
        
        elif check_name == "No Unused Influences" and hasattr(check_instance, 'failures'):
            # Group by geometry
            by_geo = {}
            for sc, geo, inf in check_instance.failures:
                if geo not in by_geo:
                    by_geo[geo] = []
                by_geo[geo].append(inf)
            
            for geo, infs in sorted(by_geo.items()):
                geo_short = geo.split('|')[-1]  # Just the short name
                inf_names = ', '.join([i.split('|')[-1] for i in infs])
                self._log_message('  > {}: {}'.format(geo_short, inf_names))

    def _run_autofix(self, row):
        """Run the autofix for a row, then re-evaluate the check."""
        self._log_message('')
        self._log_message('Applying autofix for: {}'.format(row._check.name))
        
        try:
            row._check.autofix()
        except Exception as e:
            cmds.warning('Autofix "{}" raised an error: {}'.format(row._check.name, e))
            self._log_message('[AUTOFIX FAILED] {}'.format(row._check.name))

        # Re-run the check so the button reflects the new state
        try:
            passed = row._check.check()
        except Exception:
            passed = False

        if passed:
            row._status_btn.setText('OK')
            row._status_btn.setStyleSheet('background-color: #4CAF50; color: white;')
            row._fix_btn.setVisible(False)
            self._log_message('[OK] {} (fixed)'.format(row._check.name))
        else:
            row._status_btn.setText('Error')
            row._status_btn.setStyleSheet('background-color: #F44336; color: white;')
            self._log_message('[ERROR] {} (fix did not resolve)'.format(row._check.name))
            if hasattr(row._check, 'failures') and row._check.failures:
                self._log_failure_details(row._check)

    # ------------------------------------------------------------------ buttons

    def set_blue_buttons(self):
        buttons = [
            self.ui.publish_asset_button
        ]

        blue_style = """
            QPushButton {
                background-color: #3b5998;
                color: #f0f0f0;
                border-radius: 6px;
                font-weight: bold;
                padding: 6px;
                border: 1px solid #2e3e5c;
            }
            QPushButton:hover {
                background-color: #4a69ad;
                border: 1px solid #3c4d6e;
            }
            QPushButton:pressed {
                background-color: #2d4474;
            }
        """
        
        for btn in buttons:
            btn.setStyleSheet(blue_style)
            btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            btn.customContextMenuRequested.connect(self._open_publish_path_from_context)

    def _open_publish_path_from_context(self, _point):
        target_path = os.path.normpath(os.path.join(self.save_path, self.mode))
        if not os.path.exists(target_path):
            return

        if os.name == "nt":
            os.startfile(target_path)
        elif os.name == "posix":
            QtCore.QProcess.startDetached("open", [target_path])

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
try:
    from shiboken6 import wrapInstance
    from PySide6 import QtGui, QtCore
    from PySide6 import QtUiTools
    from PySide6 import QtWidgets
    from PySide6.QtWidgets import *
except:
    from shiboken2 import wrapInstance #Compatibility pre 2026
    from shiboken2 import wrapInstance
    from PySide2 import QtGui, QtCore
    from PySide2 import QtUiTools
    from PySide2 import QtWidgets
    from PySide2.QtWidgets import *

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya import cmds
import maya.OpenMayaUI as omui

from pathlib import Path
import os
try:
    import importlib;from importlib import reload
except:
    import imp;from imp import reload

import sys
import json
import re

try:from urllib.request import Request, urlopen
except:pass

# -------------------------------------------------------------------

#QT WIndow!
PATH = os.path.dirname(__file__)
PATH = Path(PATH)
PATH_PARTS = PATH.parts[:-2]
FOLDER=''
for p in PATH_PARTS:
    FOLDER = os.path.join(FOLDER, p)
PATH = os.path.join(FOLDER, 'UI')

ICONS_FOLDER = os.path.join(FOLDER,'Icons')

Title = 'Menu'
UI_File = 'menu.ui'



# -------------------------------------------------------------------

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class Menu(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window(), owner=None):
        super(Menu, self).__init__(parent)
        self.owner = owner

        self.setWindowTitle(Title)
        self.setFixedHeight(20)

        self.init_ui()
        self.create_layout()
        self.create_connections()

    def init_ui(self):
        UIPath = os.path.join(FOLDER,'UI','menu')
        f = QtCore.QFile(os.path.join(UIPath, UI_File))
        f.open(QtCore.QFile.ReadOnly)

        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(f, parentWidget=self)

        f.close()

    # -------------------------------------------------------------------

    def create_layout(self):

        #Create Menu Bar
        self.menuBar = QtWidgets.QMenuBar()  # requires parent

        # -------------------------------------------------------------------
        #File Menu
        self.fileMenu = QtWidgets.QMenu(self)
        self.fileMenu.setTitle("File")

        #Create Menu Actions on File Section
        self.nda_mode = self.fileMenu.addAction('NDA Mode')
        self.version_delete = self.fileMenu.addAction('Version Delete')
        self.fileMenu.addSeparator()
        self.download_latest = self.fileMenu.addAction('Download Latest')
        self.fileMenu.addSeparator()

        # -------------------------------------------------------------------
        #Rig Menu
        self.rigMenu = QtWidgets.QMenu(self)
        self.rigMenu.setTitle("Rig")
        self.generate_build_data = self.rigMenu.addAction('Query Build Data')
        self.rigMenu.addSeparator()

        self.save_component_ctrls = self.rigMenu.addAction('Save Controllers')
        self.save_component_skin = self.rigMenu.addAction('Save Skin')
        self.rigMenu.addSeparator()

        self.load_component_ctrls = self.rigMenu.addAction('Load Controllers')
        self.load_component_skin = self.rigMenu.addAction('Load Skin')
        self.rigMenu.addSeparator()

        self.show_mutant_build_color = self.rigMenu.addAction('Show Mutant Build Color')
        self.show_mutant_build_color.setCheckable(True)
        self.show_mutant_build_color.setChecked(False)

        #Add actions to file menu
        self.menuBar.addMenu(self.fileMenu)
        self.menuBar.addMenu(self.rigMenu)

        #Add to menu UI
        self.ui.menuLayout.insertWidget(0, self.menuBar)

    # -------------------------------------------------------------------

    def create_connections(self):
        #FILE MENU
        self.nda_mode.triggered.connect(self.toggle_nda_mode)
        self.download_latest.triggered.connect(self.open_link_donwload_latest)
        self.version_delete.triggered.connect(self.open_version_delete)
        self.generate_build_data.triggered.connect(self.query_build_data_json)
        self.save_component_ctrls.triggered.connect(self.save_component_controllers)
        self.save_component_skin.triggered.connect(self.save_component_skinning)
        self.load_component_ctrls.triggered.connect(self.load_component_controllers_from_version)
        self.load_component_skin.triggered.connect(self.load_component_skinning_from_version)
        self.show_mutant_build_color.toggled.connect(self.toggle_mutant_build_color)

    # -------------------------------------------------------------------

    def toggle_nda_mode(self):
        print('NDA Mode')

    def get_default_json_path(self):
        """
        Get the default path to the blue_pipeline JSON configuration file.

        Returns:
            str: The full path to the "blue_pipeline.json" file located in the user's Maya scripts directory.
        """
        scripts_folder = cmds.internalVar(userScriptDir=True)
        return os.path.join(scripts_folder, "blue_pipeline.json")

    def toggle_nda_mode(self):

        json_path = self.get_default_json_path()

        # Load or initialize settings
        with open(json_path, "r") as f:
            settings = json.load(f)

        # Ensure key exists
        if "nda_mode" not in settings:
            settings["nda_mode"] = False

        # Toggle value
        settings["nda_mode"] = not settings["nda_mode"]

        # Save back
        with open(json_path, "w") as f:
            json.dump(settings, f, indent=4)

        print(f"NDA Mode set to: {settings['nda_mode']}")
        return settings["nda_mode"]

    def open_link_donwload_latest(self):
        import webbrowser
        webbrowser.open("https://github.com/BluetapeRigging/Blue_Pipeline/archive/refs/heads/main.zip")
        webbrowser.open("https://github.com/BluetapeRigging/Blue_Pipeline")

    def open_version_delete(self):
        if self.owner and hasattr(self.owner, "open_version_delete_dialog"):
            self.owner.open_version_delete_dialog()

    def _extract_version_number(self, name):
        match = re.match(r"^v(\d+)$", str(name), re.IGNORECASE)
        if not match:
            return None
        try:
            return int(match.group(1))
        except Exception:
            return None

    def _next_version_name_from_paths(self, base_path, extension=None, folders=False, prefix=''):
        if not os.path.isdir(base_path):
            return "{}V1".format(prefix)

        highest = 0
        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)

            if folders and not os.path.isdir(item_path):
                continue
            if not folders and os.path.isdir(item_path):
                continue

            stem = item
            if extension:
                if not item.lower().endswith(extension.lower()):
                    continue
                stem = os.path.splitext(item)[0]

            if prefix and not stem.lower().startswith(prefix.lower()):
                continue

            version_stem = stem[len(prefix):] if prefix else stem

            version_num = self._extract_version_number(version_stem)
            if version_num is not None:
                highest = max(highest, version_num)

        return "{}V{}".format(prefix, highest + 1)

    def _latest_version_name_from_paths(self, base_path, extension=None, folders=False, prefix=''):
        if not os.path.isdir(base_path):
            return None

        latest_name = None
        highest = -1

        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)

            if folders and not os.path.isdir(item_path):
                continue
            if not folders and os.path.isdir(item_path):
                continue

            stem = item
            if extension:
                if not item.lower().endswith(extension.lower()):
                    continue
                stem = os.path.splitext(item)[0]

            if prefix and not stem.lower().startswith(prefix.lower()):
                continue

            version_stem = stem[len(prefix):] if prefix else stem
            version_num = self._extract_version_number(version_stem)
            if version_num is None:
                continue

            if version_num > highest:
                highest = version_num
                latest_name = stem

        return latest_name

    def _all_version_names_from_paths(self, base_path, extension=None, folders=False, prefix=''):
        if not os.path.isdir(base_path):
            return []

        version_map = {}

        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)

            if folders and not os.path.isdir(item_path):
                continue
            if not folders and os.path.isdir(item_path):
                continue

            stem = item
            if extension:
                if not item.lower().endswith(extension.lower()):
                    continue
                stem = os.path.splitext(item)[0]

            if prefix and not stem.lower().startswith(prefix.lower()):
                continue

            version_stem = stem[len(prefix):] if prefix else stem
            version_num = self._extract_version_number(version_stem)
            if version_num is None:
                continue

            version_map[version_num] = stem

        return [version_map[k] for k in sorted(version_map.keys(), reverse=True)]

    def _get_components_base_paths(self):
        if not self.owner:
            cmds.warning("Assets Manager context not available.")
            return None

        project_folder = getattr(self.owner, "project_folder", None)
        show_name = getattr(self.owner, "current_show", None)
        asset_name = getattr(self.owner, "current_asset", None)

        if not project_folder or not show_name or not asset_name:
            cmds.warning("Select a show and asset first in Assets Manager.")
            return None

        asset_path = os.path.join(project_folder, show_name, asset_name)
        if not os.path.isdir(asset_path):
            cmds.warning("Asset path does not exist: {}".format(asset_path))
            return None

        components_path = os.path.join(asset_path, "Components")
        controllers_path = os.path.join(components_path, "Controllers")
        skin_path = os.path.join(components_path, "Skin")

        for path in [components_path, controllers_path, skin_path]:
            if not os.path.isdir(path):
                os.makedirs(path)

        return {
            "asset_path": asset_path,
            "components_path": components_path,
            "controllers_path": controllers_path,
            "skin_path": skin_path,
            "show_name": show_name,
            "asset_name": asset_name,
        }

    def _get_clean_asset_name(self, asset_name):
        match = re.match(r"^b\d{4}_(.+)$", str(asset_name), re.IGNORECASE)
        if match:
            return match.group(1)
        return str(asset_name)

    def save_component_controllers(self):
        try:
            paths = self._get_components_base_paths()
            if not paths:
                return

            from Mutant_Tools.Utils.IO import CtrlUtils
            reload(CtrlUtils)
            ctrls = CtrlUtils.Ctrls()

            clean_asset_name = self._get_clean_asset_name(paths["asset_name"])
            version_prefix = "{}_Ctrls_".format(clean_asset_name)
            version_name = self._next_version_name_from_paths(
                paths["controllers_path"],
                extension=".json",
                folders=False,
                prefix=version_prefix,
            )
            json_path = os.path.join(paths["controllers_path"], "{}.json".format(version_name))

            ctrls.save_all(folder_path=json_path, force_validate=True)

            if self.owner and hasattr(self.owner, "populate_tasks"):
                self.owner.populate_tasks(paths["show_name"], paths["asset_name"])

            cmds.inViewMessage(
                amg="Controllers saved: <hl>{}</hl>".format(version_name),
                pos="botCenter",
                fade=True,
                fadeStayTime=2500,
            )
        except Exception as e:
            cmds.warning("Failed to save component controllers: {}".format(e))

    def save_component_skinning(self):
        try:
            paths = self._get_components_base_paths()
            if not paths:
                return

            from Mutant_Tools.Utils.IO import EasySkin
            reload(EasySkin)

            clean_asset_name = self._get_clean_asset_name(paths["asset_name"])
            version_prefix = "{}_Skin_".format(clean_asset_name)
            version_name = self._next_version_name_from_paths(
                paths["skin_path"],
                folders=True,
                prefix=version_prefix,
            )
            skin_version_folder = os.path.join(paths["skin_path"], version_name)

            if not os.path.isdir(skin_version_folder):
                os.makedirs(skin_version_folder)

            EasySkin.save_all_skins_to(folder_path=skin_version_folder)

            if self.owner and hasattr(self.owner, "populate_tasks"):
                self.owner.populate_tasks(paths["show_name"], paths["asset_name"])

            cmds.inViewMessage(
                amg="Skin saved: <hl>{}</hl>".format(version_name),
                pos="botCenter",
                fade=True,
                fadeStayTime=2500,
            )
        except Exception as e:
            cmds.warning("Failed to save component skin: {}".format(e))

    def load_component_controllers_latest(self):
        try:
            paths = self._get_components_base_paths()
            if not paths:
                return

            from Mutant_Tools.Utils.IO import CtrlUtils
            reload(CtrlUtils)
            ctrls = CtrlUtils.Ctrls()

            clean_asset_name = self._get_clean_asset_name(paths["asset_name"])
            version_prefix = "{}_Ctrls_".format(clean_asset_name)
            latest_name = self._latest_version_name_from_paths(
                paths["controllers_path"],
                extension=".json",
                folders=False,
                prefix=version_prefix,
            )

            if not latest_name:
                cmds.warning("No controller component versions found in: {}".format(paths["controllers_path"]))
                return

            json_path = os.path.join(paths["controllers_path"], "{}.json".format(latest_name))
            if not os.path.isfile(json_path):
                cmds.warning("Controller version file not found: {}".format(json_path))
                return

            ctrls.load_all(path=json_path)

            cmds.inViewMessage(
                amg="Controllers loaded: <hl>{}</hl>".format(latest_name),
                pos="botCenter",
                fade=True,
                fadeStayTime=2500,
            )
        except Exception as e:
            cmds.warning("Failed to load latest component controllers: {}".format(e))

    def load_component_skinning_latest(self):
        try:
            paths = self._get_components_base_paths()
            if not paths:
                return

            from Mutant_Tools.Utils.IO import EasySkin
            reload(EasySkin)

            clean_asset_name = self._get_clean_asset_name(paths["asset_name"])
            version_prefix = "{}_Skin_".format(clean_asset_name)
            latest_name = self._latest_version_name_from_paths(
                paths["skin_path"],
                folders=True,
                prefix=version_prefix,
            )

            if not latest_name:
                cmds.warning("No skin component versions found in: {}".format(paths["skin_path"]))
                return

            skin_version_folder = os.path.join(paths["skin_path"], latest_name)
            if not os.path.isdir(skin_version_folder):
                cmds.warning("Skin version folder not found: {}".format(skin_version_folder))
                return

            EasySkin.load_all_skins_from(folder_path=skin_version_folder)

            cmds.inViewMessage(
                amg="Skin loaded: <hl>{}</hl>".format(latest_name),
                pos="botCenter",
                fade=True,
                fadeStayTime=2500,
            )
        except Exception as e:
            cmds.warning("Failed to load latest component skin: {}".format(e))

    def load_component_controllers_from_version(self):
        try:
            paths = self._get_components_base_paths()
            if not paths:
                return

            from Mutant_Tools.Utils.IO import CtrlUtils
            reload(CtrlUtils)
            ctrls = CtrlUtils.Ctrls()

            clean_asset_name = self._get_clean_asset_name(paths["asset_name"])
            version_prefix = "{}_Ctrls_".format(clean_asset_name)
            versions = self._all_version_names_from_paths(
                paths["controllers_path"],
                extension=".json",
                folders=False,
                prefix=version_prefix,
            )

            if not versions:
                cmds.warning("No controller component versions found in: {}".format(paths["controllers_path"]))
                return

            selected_version, ok = QtWidgets.QInputDialog.getItem(
                self,
                "Load Controller Version",
                "Select controller version:",
                versions,
                0,
                False,
            )
            if not ok or not selected_version:
                return

            json_path = os.path.join(paths["controllers_path"], "{}.json".format(selected_version))
            if not os.path.isfile(json_path):
                cmds.warning("Controller version file not found: {}".format(json_path))
                return

            ctrls.load_all(path=json_path)

            cmds.inViewMessage(
                amg="Controllers loaded: <hl>{}</hl>".format(selected_version),
                pos="botCenter",
                fade=True,
                fadeStayTime=2500,
            )
        except Exception as e:
            cmds.warning("Failed to load selected component controllers version: {}".format(e))

    def load_component_skinning_from_version(self):
        try:
            paths = self._get_components_base_paths()
            if not paths:
                return

            from Mutant_Tools.Utils.IO import EasySkin
            reload(EasySkin)

            clean_asset_name = self._get_clean_asset_name(paths["asset_name"])
            version_prefix = "{}_Skin_".format(clean_asset_name)
            versions = self._all_version_names_from_paths(
                paths["skin_path"],
                folders=True,
                prefix=version_prefix,
            )

            if not versions:
                cmds.warning("No skin component versions found in: {}".format(paths["skin_path"]))
                return

            selected_version, ok = QtWidgets.QInputDialog.getItem(
                self,
                "Load Skin Version",
                "Select skin version:",
                versions,
                0,
                False,
            )
            if not ok or not selected_version:
                return

            skin_version_folder = os.path.join(paths["skin_path"], selected_version)
            if not os.path.isdir(skin_version_folder):
                cmds.warning("Skin version folder not found: {}".format(skin_version_folder))
                return

            EasySkin.load_all_skins_from(folder_path=skin_version_folder)

            cmds.inViewMessage(
                amg="Skin loaded: <hl>{}</hl>".format(selected_version),
                pos="botCenter",
                fade=True,
                fadeStayTime=2500,
            )
        except Exception as e:
            cmds.warning("Failed to load selected component skin version: {}".format(e))

    def query_build_data_json(self):
        try:
            from Blue_Pipeline.UI.assets_manager import load_asset_manager
            report = load_asset_manager.build_mutant_build_data(root_path="E:/BlueTape", keyword="mutant_build")
            if not report:
                return

            load_asset_manager.load_mutant_build_query_data(query_json_path="E:/BlueTape/Build_Data.json")

            if self.owner and hasattr(self.owner, "populate_files"):
                show_name = getattr(self.owner, "current_show", None)
                asset_name = getattr(self.owner, "current_asset", None)
                task_name = getattr(self.owner, "current_task", None)
                if show_name and asset_name and task_name:
                    self.owner.populate_files(show_name, asset_name, task_name)

            summary = report.get("summary", {})
            cmds.inViewMessage(
                amg=(
                    f"Build_Data.json updated: "
                    f"<hl>{summary.get('with_mutant_build', 0)}</hl> with build / "
                    f"<hl>{summary.get('without_mutant_build', 0)}</hl> without build"
                ),
                pos="botCenter",
                fade=True,
                fadeStayTime=2500,
            )
        except Exception as e:
            cmds.warning(f"Failed to generate Build_Data.json: {e}")

    def toggle_mutant_build_color(self, enabled):
        try:
            from Blue_Pipeline.UI.assets_manager import load_asset_manager
            load_asset_manager.set_mutant_build_color_enabled(enabled)

            if self.owner and hasattr(self.owner, "populate_files"):
                show_name = getattr(self.owner, "current_show", None)
                asset_name = getattr(self.owner, "current_asset", None)
                task_name = getattr(self.owner, "current_task", None)
                if show_name and asset_name and task_name:
                    self.owner.populate_files(show_name, asset_name, task_name)
        except Exception as e:
            cmds.warning(f"Failed to toggle Mutant Build color: {e}")

    # CLOSE EVENTS _________________________________
    def closeEvent(self, event):
        ''


# -------------------------------------------------------------------

if __name__ == "__main__":

    try:
        AutoRiggerMenu.close()  # pylint: disable=E0601
        AutoRiggerMenu.deleteLater()
    except:
        pass
    menu_ui = AutoRiggerMenu()
    menu_ui.show()

# -------------------------------------------------------------------


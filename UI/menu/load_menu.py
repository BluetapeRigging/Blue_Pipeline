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

    def __init__(self, parent=maya_main_window()):
        super(Menu, self).__init__(parent)

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
        self.fileMenu.addSeparator()

        #Add actions to file menu
        self.menuBar.addMenu(self.fileMenu)

        #Add to menu UI
        self.ui.menuLayout.insertWidget(0, self.menuBar)

    # -------------------------------------------------------------------

    def create_connections(self):
        #FILE MENU
        self.nda_mode.triggered.connect(self.toggle_nda_mode)

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


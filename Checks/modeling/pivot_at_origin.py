import maya.cmds as cmds
from Blue_Pipeline.Checks.base_check import BaseCheck


class PivotAtOrigin(BaseCheck):
    """All meshes inside the 'geo' group must have their rotate/scale pivot at (0, 0, 0)."""

    name        = "Geo Pivots at Origin"
    description = "Rotate and scale pivots of every mesh in the 'geo' group must be at (0, 0, 0)."
    can_fix     = True

    # ------------------------------------------------------------------ helpers

    def _get_transforms(self):
        if not cmds.objExists('geo'):
            return []
        meshes = cmds.listRelatives('geo', allDescendents=True, type='mesh', fullPath=True) or []
        transforms = []
        for mesh in meshes:
            parent = cmds.listRelatives(mesh, parent=True, fullPath=True)
            if parent:
                transforms.append(parent[0])
        return transforms

    # ------------------------------------------------------------------ api

    def check(self):
        for xf in self._get_transforms():
            rp = cmds.xform(xf, q=True, worldSpace=True, rotatePivot=True)
            sp = cmds.xform(xf, q=True, worldSpace=True, scalePivot=True)
            if any(abs(v) > 0.001 for v in rp + sp):
                return False
        return True

    def autofix(self):
        for xf in self._get_transforms():
            cmds.xform(xf, worldSpace=True, rotatePivot=[0, 0, 0])
            cmds.xform(xf, worldSpace=True, scalePivot=[0, 0, 0])

import maya.cmds as cmds
from Blue_Pipeline.Checks.base_check import BaseCheck


class NoHistory(BaseCheck):
    """All meshes inside the 'geo' group must have no construction history."""

    name        = "No Construction History"
    description = "Every mesh in the 'geo' group must have its construction history deleted."
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

    def _has_history(self, transform):
        history = cmds.listHistory(transform, pruneDagObjects=True) or []
        return len(history) > 0

    # ------------------------------------------------------------------ api

    def check(self):
        return not any(self._has_history(xf) for xf in self._get_transforms())

    def autofix(self):
        for xf in self._get_transforms():
            if self._has_history(xf):
                cmds.delete(xf, constructionHistory=True)

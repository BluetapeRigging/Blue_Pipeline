import maya.cmds as cmds
from Blue_Pipeline.Checks.base_check import BaseCheck


class UnusedInfluences(BaseCheck):
    """Every skin cluster must have no influences with zero total weight."""

    name        = "No Unused Influences"
    description = "All skin clusters must not contain influences that contribute zero weight."
    can_fix     = True

    def __init__(self):
        super(UnusedInfluences, self).__init__()
        self.failures = []  # List of (skinCluster, geometry, influence)

    # ------------------------------------------------------------------ helpers

    def _get_unused(self):
        """Returns a list of (skinCluster, influence, geometry) tuples that have zero weight."""
        unused = []
        for sc in cmds.ls(type='skinCluster'):
            # Get the geometry that this skin cluster is attached to
            geometry = cmds.skinCluster(sc, q=True, geometry=True)
            if not geometry:
                geometry = ['Unknown']
            geo_name = geometry[0]
            
            all_infs     = set(cmds.skinCluster(sc, q=True, influence=True)         or [])
            weighted_infs = set(cmds.skinCluster(sc, q=True, weightedInfluence=True) or [])
            for inf in sorted(all_infs - weighted_infs):
                unused.append((sc, geo_name, inf))
        return unused

    # ------------------------------------------------------------------ api

    def check(self):
        self.failures = self._get_unused()
        return len(self.failures) == 0

    def autofix(self):
        for sc, geo, inf in self.failures:
            try:
                cmds.skinCluster(sc, e=True, removeInfluence=inf)
            except Exception:
                pass


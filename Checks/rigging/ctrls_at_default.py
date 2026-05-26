import maya.cmds as cmds
from Blue_Pipeline.Checks.base_check import BaseCheck


class CtrlsAtDefault(BaseCheck):
    """All *_Ctrl transforms must be at T(0,0,0) R(0,0,0) S(1,1,1)."""

    name        = "Controls at Default Values"
    description = "Every *_Ctrl must have translate (0,0,0), rotate (0,0,0), scale (1,1,1)."
    can_fix     = True

    _TOLERANCE = 0.0001

    def __init__(self):
        super(CtrlsAtDefault, self).__init__()
        self.failures = []  # List of (ctrl, attr, current_value, expected_value)

    # ------------------------------------------------------------------ helpers

    def _get_ctrls(self):
        return cmds.ls('*_Ctrl', type='transform') or []

    def _is_default(self, ctrl):
        tol = self._TOLERANCE
        t = cmds.getAttr('{}.translate'.format(ctrl))[0]
        r = cmds.getAttr('{}.rotate'.format(ctrl))[0]
        s = cmds.getAttr('{}.scale'.format(ctrl))[0]
        return (
            all(abs(v)       < tol for v in t) and
            all(abs(v)       < tol for v in r) and
            all(abs(v - 1.0) < tol for v in s)
        )

    def _collect_failures(self):
        """Gather detailed failure info."""
        self.failures = []
        for ctrl in self._get_ctrls():
            if self._is_default(ctrl):
                continue
            # Check each channel
            for attr, expected in [
                ('translateX', 0), ('translateY', 0), ('translateZ', 0),
                ('rotateX', 0),    ('rotateY', 0),    ('rotateZ', 0),
                ('scaleX', 1),     ('scaleY', 1),     ('scaleZ', 1),
            ]:
                current = cmds.getAttr('{}.{}'.format(ctrl, attr))
                if abs(current - expected) > self._TOLERANCE:
                    self.failures.append((ctrl, attr, current, expected))

    # ------------------------------------------------------------------ api

    def check(self):
        self._collect_failures()
        return len(self.failures) == 0

    def autofix(self):
        for ctrl in self._get_ctrls():
            if self._is_default(ctrl):
                continue
            for attr in ('translateX', 'translateY', 'translateZ',
                         'rotateX',    'rotateY',    'rotateZ'):
                if not cmds.getAttr('{}.{}'.format(ctrl, attr), lock=True):
                    try:
                        cmds.setAttr('{}.{}'.format(ctrl, attr), 0)
                    except Exception:
                        pass
            for attr in ('scaleX', 'scaleY', 'scaleZ'):
                if not cmds.getAttr('{}.{}'.format(ctrl, attr), lock=True):
                    try:
                        cmds.setAttr('{}.{}'.format(ctrl, attr), 1)
                    except Exception:
                        pass


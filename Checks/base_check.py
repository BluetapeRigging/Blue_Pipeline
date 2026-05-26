class BaseCheck(object):
    """
    Base class for all pipeline checks.

    Subclass this, override `name`, `description`, `can_fix`,
    and implement `check()` (and optionally `autofix()`).

    Example
    -------
    class MyCheck(BaseCheck):
        name     = "My Check"
        can_fix  = True

        def check(self):
            return True  # True = pass, False = fail

        def autofix(self):
            pass  # fix the issue
    """

    name        = "Base Check"
    description = ""
    can_fix     = False

    def check(self):
        """Run the check.  Returns True (pass) or False (fail)."""
        raise NotImplementedError

    def autofix(self):
        """Attempt to auto-fix the issue.  Only called when can_fix is True."""
        raise NotImplementedError

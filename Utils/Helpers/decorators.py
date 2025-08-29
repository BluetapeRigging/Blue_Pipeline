from functools import wraps
from maya import cmds

def undo(func):
    '''Enable undo within Maya after function is run'''

    @wraps(func)
    def wrap(*args, **kwargs):
        result = None
        try:
            cmds.undoInfo(openChunk=True, chunkName=func.__name__)
            result = func(*args, **kwargs)
        except Exception:
            raise
        finally:
            cmds.undoInfo(closeChunk=True)
        return result
    return wrap


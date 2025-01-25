from .base import *

DEBUG = False if os.getenv('MODE') == 'production' else True

try:
    from .local import *
except ImportError:
    pass

"""
Platform detection and web compatibility utilities.
"""

import sys

# Check if running in web environment (pygbag/pygame-web)
IS_WEB = False

# Method 1: Check for emscripten/wasi platform
if hasattr(sys, 'platform'):
    IS_WEB = sys.platform in ('emscripten', 'wasi')

# Method 2: Check for browser globals (pygbag environment)
if not IS_WEB:
    try:
        # In pygbag/web environment, __javascript__ module is available
        import __javascript__
        IS_WEB = True
    except (ImportError, ModuleNotFoundError):
        pass

# Method 3: Check for window object (browser)
if not IS_WEB:
    try:
        # In browser, window object exists
        import __javascript__
        if hasattr(__javascript__, 'window'):
            IS_WEB = True
    except (ImportError, ModuleNotFoundError):
        pass

def is_web():
    """Check if running in web/browser environment"""
    return IS_WEB

def get_storage():
    """Get storage interface (localStorage for web, file for desktop)"""
    if is_web():
        try:
            import __javascript__
            return __javascript__.localStorage
        except (ImportError, ModuleNotFoundError):
            return None
    return None


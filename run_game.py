import sys

# Using X|Y union type hints.
# requires Python 3.10+.
MIN_PYTHON = (3, 10)
MAX_PYTHON = (3, 13) # pygame does not build on Python 3.14+

if sys.version_info[:2] < MIN_PYTHON:
    sys.exit(
        "Python {}.{} or later is required (you have {}.{}).".format(
            MIN_PYTHON[0], MIN_PYTHON[1],
            sys.version_info[0], sys.version_info[1],
        )
    )

if sys.version_info[:2] > MAX_PYTHON:
    sys.exit(
        "This game requires Python 3.10 – 3.13.\n"
        "Python {}.{} is not supported because pygame does not install on it.\n"
        "Please use Python 3.13 or earlier.".format(
            sys.version_info[0], sys.version_info[1],
        )
    )

try:
    import pygame
except ImportError:
    sys.exit(
        "pygame is not installed.\n"
        "Install it with:  pip install pygame"
    )

# pygame.display.get_desktop_sizes() was added in pygame 2.1.0.
# pygame.WINDOWSIZECHANGED was added in pygame 2.0.0.
_ver = tuple(int(x) for x in pygame.version.ver.split(".")[:2])
if _ver < (2, 1):
    sys.exit(
        "pygame 2.1.0 or later is required (you have {}).\n"
        "Upgrade with:  pip install --upgrade pygame".format(pygame.version.ver)
    )

try:
    import pytmx
except ImportError:
    sys.exit(
        "pytmx is not installed.\n"
        "Install it with:  pip install pytmx"
    )

import main
main.main()
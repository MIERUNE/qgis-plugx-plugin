import sys
import os

# to import modules as non-relative
sys.path.append(os.path.dirname(__file__))


def classFactory(iface):
    from qgis2plugx import QGIS2PlugX

    return QGIS2PlugX(iface)

from colorlog import error, info

from jetconf import config

from . import shared_objs as so
from .knot_api import KnotConfig


def jc_startup():
    info("Backend: init")

    # Create global API objects
    so.KNOT = KnotConfig()

    # Initialize Knot control interface
    try:
        so.KNOT.set_socket(config.CFG.root["KNOT"]["SOCKET"])
    except KeyError:
        error("Cannot find KNOT/SOCKET item in jetconf config file")


def jc_end():
    info("Backend: cleaning up")
    so.KNOT = None

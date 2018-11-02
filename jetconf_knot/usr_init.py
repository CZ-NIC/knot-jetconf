from colorlog import error, info

from jetconf import config

from . import shared_objs as so
from .exns_api import NsConfig, NsApiError


def jc_startup():
    info("Backend: init")

    # Create global API objects
    so.NS = NsConfig()

    # Initialize Knot control interface
    try:
        so.NS.set_cfg_file_path(config.CFG.root["NS"]["CONFFILE"])
    except KeyError:
        error("Cannot find NS config file path in JETCONF's config file")


def jc_end():
    info("Backend: cleaning up")
    so.NS = None

from colorlog import error, info

from jetconf import config

from . import shared_objs as so
from .knot_api import KnotConfig


def jc_startup():
    info("Backend: init")


def jc_end():
    info("Backend: cleaning up")
    so.KNOT = None

from colorlog import error

from yangson.instance import InstanceRoute
from jetconf.helpers import JsonNodeT
from jetconf.handler_base import StateDataContainerHandler, StateDataListHandler
from jetconf.data import BaseDatastore

from . import shared_objs as so


# ---------- User-defined handlers follow ----------


# Instantiate state data handlers
def register_state_handlers(ds: BaseDatastore):
    pass

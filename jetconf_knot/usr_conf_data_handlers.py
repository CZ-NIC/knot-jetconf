from typing import List, Dict, Union, Any

from yangson.instance import InstanceRoute

from jetconf.data import BaseDatastore, DataChange
from jetconf.helpers import LogHelpers
from jetconf.handler_base import ConfDataObjectHandler, ConfDataListHandler

from . import shared_objs as so
JsonNodeT = Union[Dict[str, Any], List]
debug_confh = LogHelpers.create_module_dbg_logger(__name__)


# ---------- User-defined handlers follow ----------


# Config handler for "server" section
class KnotConfListener(ConfDataObjectHandler):
    def replace(self, ii: InstanceRoute, ch: DataChange):
        debug_confh(self.__class__.__name__ + " replace triggered")
        base_ii = ii[0:1]
        base_nv = self.ds.get_data_root().goto(base_ii).raw_value()
        so.NS.config_write(base_nv)

    def delete(self, ii: InstanceRoute, ch: DataChange):
        debug_confh(self.__class__.__name__ + " delete triggered")
        base_ii = ii[0:1]
        base_nv = self.ds.get_data_root().goto(base_ii).raw_value()
        so.NS.config_write(base_nv)


# Connects to Knot control socket and begins a new transaction (config or zone)
def commit_begin():
    debug_confh("Beginning transaction commit")


# Commits current Knot internal transaction and disconnects from control socket
def commit_end(failed: bool=False):
    if failed:
        debug_confh("Aborting transaction")
    else:
        debug_confh("Commiting transaction OK")


def register_conf_handlers(ds: BaseDatastore):
    ds.handlers.conf.register(KnotConfListener(ds, "/dns-server:dns-server"))
    # Set datastore commit callbacks
    ds.handlers.commit_begin = commit_begin
    ds.handlers.commit_end = commit_end

from yangson.instance import InstanceRoute, EntryKeys
from jetconf.data import BaseDatastore, ChangeType, DataChange
from jetconf.helpers import LogHelpers
from jetconf.handler_base import ConfDataListHandler, ConfDataObjectHandler

from . import shared_objs as so

debug_confh = LogHelpers.create_module_dbg_logger(__name__)


# ---------- User-defined handlers follow ----------

class RootHandler(ConfDataObjectHandler):
    def create(self, ii: InstanceRoute, ch: DataChange):
        debug_confh(self.__class__.__name__ + " create triggered")

        root_nv = self.ds.get_data_root().add_defaults().value
        so.KNOT.config_set(root_nv)

    def replace(self, ii: InstanceRoute, ch: DataChange):
        debug_confh(self.__class__.__name__ + " replace triggered")

        root_nv = self.ds.get_data_root().add_defaults().value
        so.KNOT.config_set(root_nv)

    def delete(self, ii: InstanceRoute, ch: DataChange):
        debug_confh(self.__class__.__name__ + " delete triggered")

        root_nv = self.ds.get_data_root().add_defaults().value
        so.KNOT.config_set(root_nv)


def commit_begin():
    debug_confh("Connecting to KNOT socket")
    so.KNOT.knot_connect()

    debug_confh("Starting new KNOT config transaction")
    so.KNOT.begin()


def commit_end(failed: bool = False):
    so.KNOT.flush_socket()

    if failed:
        debug_confh("Aborting KNOT transaction")
        so.KNOT.abort()
    else:
        debug_confh("Commiting KNOT transaction")
        so.KNOT.commit()

    debug_confh("Disconnecting from KNOT socket")
    so.KNOT.knot_disconnect()


def register_conf_handlers(ds: BaseDatastore):
    ds.handlers.conf.register(RootHandler(ds, "/"))

    # Set datastore commit callbacks
    ds.handlers.commit_begin = commit_begin
    ds.handlers.commit_end = commit_end

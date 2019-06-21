from yangson.instance import InstanceRoute, EntryKeys
from jetconf.data import BaseDatastore, ChangeType, DataChange
from jetconf.helpers import LogHelpers
from jetconf.handler_base import ConfDataListHandler, ConfDataObjectHandler
from jetconf.nacm import NacmRuleList, NacmRule, NacmRuleType, Action, Permission, NacmGroup
from typing import Set

from . import shared_objs as so

debug_confh = LogHelpers.create_module_dbg_logger(__name__)


# ---------- User-defined handlers follow ----------

class RootHandler(ConfDataObjectHandler):
    def replace(self, ii: InstanceRoute, ch: DataChange):
        debug_confh(self.__class__.__name__ + " replace triggered")

        root_nv = self.ds.get_data_root().add_defaults().value

        so.KNOT.config_set(root_nv)


class RemoteHandler(ConfDataListHandler):

    def create_item(self, ii: InstanceRoute, ch: DataChange):
        debug_confh(self.__class__.__name__ + " create item triggered")

        # Create new remote-server
        name = ch.input_data["cznic-dns-server-simple:remote-server"]["name"]
        remote_nv = ch.input_data["cznic-dns-server-simple:remote-server"]
        debug_confh("Creating new remote-server \"{}\"".format(name))

        so.KNOT.remote_server_set(remote_nv)

    def create_list(self, ii: InstanceRoute, ch: DataChange):
        debug_confh(self.__class__.__name__ + " create list triggered")

    def replace_item(self, ii: InstanceRoute, ch: DataChange):
        debug_confh(self.__class__.__name__ + " replace item triggered")

        # Edit particular remote-server
        name = ii[2].keys[("name", None)]
        debug_confh("Editing config of remote-server \"{}\"".format(name))

        # Write whole remote-server config to Knot
        remote_nv = self.ds.get_data_root().add_defaults().goto(ii[0:3]).value

        # clear specific remote-server
        so.KNOT.unset_section(section="remote", identifier=name)
        # set new updated remote-server
        so.KNOT.remote_server_set(remote_nv)

    def replace_list(self, ii: InstanceRoute, ch: DataChange):
        debug_confh(self.__class__.__name__ + " replace list triggered")

    def delete_item(self, ii: InstanceRoute, ch: DataChange):
        debug_confh(self.__class__.__name__ + " delete item triggered")

        # Delete remote-server
        if (len(ii) == 4) and isinstance(ii[3], EntryKeys) and (ch.change_type == ChangeType.DELETE):
            name = ii[2].keys[("name", None)]
            debug_confh("Deleting remote-server \"{}\"".format(name))
            so.KNOT.remote_server_remove(name, False)

    def delete_list(self, ii: InstanceRoute, ch: DataChange):
        debug_confh(self.__class__.__name__ + " delete list triggered")


class KnotZoneHandler(ConfDataListHandler):

    def create_item(self, ii: InstanceRoute, ch: DataChange):
        debug_confh(self.__class__.__name__ + " create item triggered")

        # Create new zone
        domain = ch.input_data["cznic-dns-server-simple:zone"]["domain"]
        zone_nv = ch.input_data["cznic-dns-server-simple:zone"]
        debug_confh("Creating new zone \"{}\"".format(domain))

        so.KNOT.zone_set(zone_nv)

    def create_list(self, ii: InstanceRoute, ch: DataChange):
        debug_confh(self.__class__.__name__ + " create list triggered")

    def replace_item(self, ii: InstanceRoute, ch: DataChange):
        debug_confh(self.__class__.__name__ + " replace item triggered")

        # Edit particular zone
        domain = ii[3].keys[("domain", None)]
        debug_confh("Editing config of zone \"{}\"".format(domain))

        # Write whole zone config to Knot
        zone_nv = self.ds.get_data_root().add_defaults().goto(ii[0:4]).value

        # clear zone
        so.KNOT.unset_section(section="zone", identifier=domain)
        # set new updated zone
        so.KNOT.zone_set(zone_nv)

    def replace_list(self, ii: InstanceRoute, ch: DataChange):
        debug_confh(self.__class__.__name__ + " replace list triggered")

    def delete_item(self, ii: InstanceRoute, ch: DataChange):
        debug_confh(self.__class__.__name__ + " delete item triggered")

        # Delete zone
        if (len(ii) == 4) and isinstance(ii[3], EntryKeys) and (ch.change_type == ChangeType.DELETE):
            domain = ii[3].keys[("domain", None)]
            debug_confh("Deleting zone \"{}\"".format(domain))
            so.KNOT.zone_remove(domain, False)

    def delete_list(self, ii: InstanceRoute, ch: DataChange):
        debug_confh(self.__class__.__name__ + " delete list triggered")


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

    debug_confh("Disonnecting from KNOT socket")
    so.KNOT.knot_disconnect()


def register_conf_handlers(ds: BaseDatastore):
    ds.handlers.conf.register(RootHandler(ds, "/"))
    ds.handlers.conf.register(RemoteHandler(ds, "/cznic-dns-server-simple:dns-server/remote-server"))
    ds.handlers.conf.register(KnotZoneHandler(ds, "/cznic-dns-server-simple:dns-server/zones/zone"))

    # Set datastore commit callbacks
    ds.handlers.commit_begin = commit_begin
    ds.handlers.commit_end = commit_end

from typing import List, Dict, Union, Any

from yangson.instance import InstanceRoute, ObjectValue, EntryKeys, MemberName
from .data import BaseDatastore, SchemaNode, ChangeType, DataChange
from .helpers import PathFormat, ErrorHelpers, LogHelpers, DataHelpers
from .knot_api import KNOT, RRecordBase, SOARecord, ARecord, AAAARecord, NSRecord, MXRecord
from .handler_list import ConfDataObjectHandler, ConfDataListHandler, CONF_DATA_HANDLES

JsonNodeT = Union[Dict[str, Any], List]
epretty = ErrorHelpers.epretty
debug_confh = LogHelpers.create_module_dbg_logger(__name__)


# Config handler for "server" section
class KnotConfServerListener(ConfDataObjectHandler):
    def replace(self, ii: InstanceRoute, ch: DataChange):
        debug_confh(self.__class__.__name__ + " replace triggered")

        base_ii = ii[0:2]
        base_nv = self.ds.get_data_root().goto(base_ii).value

        KNOT.unset_section(section="server")

        KNOT.set_item(
            section="server",
            identifier=None,
            item="comment",
            value=base_nv.get("description")
        )
        KNOT.set_item(
            section="server",
            identifier=None,
            item="async-start",
            value=base_nv.get("knot-dns:async-start")
        )
        KNOT.set_item(
            section="server",
            identifier=None,
            item="nsid",
            value=base_nv.get("nsid-identity", {}).get("nsid")
        )

        listen_endpoints = base_nv.get("listen-endpoint", [])

        ep_str_list = []
        for ep in listen_endpoints:
            ep_str = ep["ip-address"]
            if ep.get("port"):
                ep_str += "@" + str(ep["port"])
            ep_str_list.append(ep_str)

        KNOT.set_item_list(
            section="server",
            identifier=None,
            item="listen",
            value=ep_str_list
        )

        KNOT.set_item(
            section="server",
            identifier=None,
            item="rundir",
            value=base_nv.get("filesystem-paths", {}).get("run-time-dir")
        )
        KNOT.set_item(
            section="server",
            identifier=None,
            item="pidfile",
            value=base_nv.get("filesystem-paths", {}).get("pid-file")
        )
        KNOT.set_item(
            section="server",
            identifier=None,
            item="tcp-workers",
            value=base_nv.get("resources", {}).get("knot-dns:tcp-workers")
        )
        KNOT.set_item(
            section="server",
            identifier=None,
            item="udp-workers",
            value=base_nv.get("resources", {}).get("knot-dns:udp-workers")
        )
        KNOT.set_item(
            section="server",
            identifier=None,
            item="rate-limit-table-size",
            value=base_nv.get("response-rate-limiting", {}).get("table-size")
        )

    def delete(self, ii: InstanceRoute, ch: DataChange):
        debug_confh(self.__class__.__name__ + " delete triggered")
        KNOT.unset_section(section="server")


# Config handler for "log" section
class KnotConfLogListener(ConfDataListHandler):
    def replace_item(self, ii: InstanceRoute, ch: "DataChange"):
        # No big data expected, can rewrite whole list
        self.replace_list(ii, ch)

    def replace_list(self, ii: InstanceRoute, ch: DataChange):
        debug_confh(self.__class__.__name__ + " replace_list triggered")

        base_ii = ii[0:2]
        base_nv = self.ds.get_data_root().goto(base_ii).value

        KNOT.unset_section(section="log")

        for logitem in base_nv:
            tgt = logitem.get("target")
            if tgt is None:
                continue

            KNOT.set_item(section="log", identifier=None, item="target", value=tgt)
            KNOT.set_item(section="log", identifier=tgt, item="comment", value=logitem.get("description"))
            KNOT.set_item(section="log", identifier=tgt, item="server", value=logitem.get("server"))
            KNOT.set_item(section="log", identifier=tgt, item="zone", value=logitem.get("zone"))
            KNOT.set_item(section="log", identifier=tgt, item="any", value=logitem.get("any"))

    def delete_list(self, ii: InstanceRoute, ch: DataChange):
        debug_confh(self.__class__.__name__ + " delete_list triggered")
        KNOT.unset_section(section="log")


# Config handler for "zone" section
class KnotConfZoneListener(ConfDataListHandler):
    def create_item(self, ii: InstanceRoute, ch: "DataChange"):
        debug_confh(self.__class__.__name__ + " create triggered")

        # Create new zone
        domain = ch.data["dns-server:zone"]["domain"]
        debug_confh("Creating new zone \"{}\"".format(domain))
        KNOT.zone_new(domain)

    def replace_item(self, ii: InstanceRoute, ch: "DataChange"):
        debug_confh(self.__class__.__name__ + " replace triggered")
        print(ii)
        # Edit particular zone
        domain = ii[3].keys["domain"]
        debug_confh("Editing config of zone \"{}\"".format(domain))

        # Write whole zone config to Knot
        zone_nv = self.ds.get_data_root().goto(ii[0:4]).value
        KNOT.unset_section(section="zone", identifier=domain)
        KNOT.set_item(
            section="zone",
            identifier=None,
            item="domain",
            value=domain
        )
        KNOT.set_item(
            section="zone",
            identifier=domain,
            item="comment",
            value=zone_nv.get("description")
        )
        KNOT.set_item(
            section="zone",
            identifier=domain,
            item="file",
            value=zone_nv.get("file")
        )
        KNOT.set_item_list(
            section="zone",
            identifier=domain,
            item="master",
            value=zone_nv.get("master", [])
        )
        KNOT.set_item_list(
            section="zone",
            identifier=domain,
            item="notify",
            value=zone_nv.get("notify", {}).get("recipient", [])
        )
        KNOT.set_item_list(
            section="zone",
            identifier=domain,
            item="acl",
            value=zone_nv.get("access-control-list", [])
        )
        KNOT.set_item(
            section="zone",
            identifier=domain,
            item="serial-policy",
            value=zone_nv.get("serial-update-method")
        )

        anytotcp = zone_nv.get("any-to-tcp")
        KNOT.set_item(
            section="zone",
            identifier=domain,
            item="disable-any",
            value=str(not anytotcp) if isinstance(anytotcp, bool) else None
        )
        KNOT.set_item(
            section="zone",
            identifier=domain,
            item="max-journal-size",
            value=zone_nv.get("journal", {}).get("maximum-journal-size")
        )
        KNOT.set_item(
            section="zone",
            identifier=domain,
            item="zonefile-sync",
            value=zone_nv.get("journal", {}).get("zone-file-sync-delay")
        )
        KNOT.set_item(
            section="zone",
            identifier=domain,
            item="ixfr-from-differences",
            value=zone_nv.get("journal", {}).get("from-differences")
        )

        qm_list = zone_nv.get("query-module", [])
        KNOT.set_item_list(
            section="zone",
            identifier=domain,
            item="module",
            value=list(map(lambda n: n["name"] + "/" + n["type"][0], qm_list))
        )
        KNOT.set_item(
            section="zone",
            identifier=domain,
            item="semantic-checks",
            value=zone_nv.get("knot-dns:semantic-checks")
        )

    def delete_item(self, ii: InstanceRoute, ch: "DataChange"):
        debug_confh(self.__class__.__name__ + " delete triggered")

        # Delete zone
        if (len(ii) == 4) and isinstance(ii[3], EntryKeys) and (ch.change_type == ChangeType.DELETE):
            domain = ii[3].keys["domain"]
            debug_confh("Deleting zone \"{}\"".format(domain))
            KNOT.zone_remove(domain, False)


# Config handler for "control" section
class KnotConfControlListener(ConfDataObjectHandler):
    def replace(self, ii: InstanceRoute, ch: DataChange):
        debug_confh(self.__class__.__name__ + " replace triggered")

        base_ii = ii[0:2]
        base_nv = self.ds.get_data_root().goto(base_ii).value

        KNOT.unset_section(section="control")
        KNOT.set_item(
            section="control",
            identifier=None,
            item="listen",
            value=base_nv.get("unix")
        )

    def delete(self, ii: InstanceRoute, ch: DataChange):
        debug_confh(self.__class__.__name__ + " delete triggered")
        KNOT.unset_section(section="control")


# Config handler for "acl" section
class KnotConfAclListener(ConfDataListHandler):
    @staticmethod
    def _write_list_item(acl_nv: ObjectValue):
        name = acl_nv["name"]
        debug_confh("ACL name={}".format(name))

        KNOT.set_item(
            section="acl",
            identifier=None,
            item="id",
            value=name
        )
        KNOT.set_item(
            section="acl",
            identifier=name,
            item="comment",
            value=acl_nv.get("description")
        )
        KNOT.set_item_list(
            section="acl",
            identifier=name,
            item="key",
            value=acl_nv.get("key", [])
        )
        KNOT.set_item_list(
            section="acl",
            identifier=name,
            item="action",
            value=acl_nv.get("operation", [])
        )

        netws = acl_nv.get("network", [])
        KNOT.set_item_list(
            section="acl",
            identifier=name,
            item="address",
            value=list(map(lambda n: n["ip-prefix"], netws))
        )

        action = acl_nv.get("action")
        KNOT.set_item(
            section="acl",
            identifier=name,
            item="deny",
            value={"deny": "true", "allow": "false"}.get(action)
        )

    def replace_item(self, ii: InstanceRoute, ch: "DataChange"):
        debug_confh(self.__class__.__name__ + " replace triggered")

        base_ii = ii[0:3]   # type: InstanceRoute
        base_nv = self.ds.get_data_root().goto(base_ii).value   # type: ObjectValue

        acl_name = base_nv["name"]
        KNOT.unset_section(section="acl", identifier=acl_name)
        self._write_list_item(base_nv)

    def replace_list(self, ii: InstanceRoute, ch: DataChange):
        debug_confh(self.__class__.__name__ + " replace triggered")

        base_ii = ii[0:2]
        base_nv = self.ds.get_data_root().goto(base_ii).value

        KNOT.unset_section(section="acl")
        for acl_nv in base_nv:
            self._write_list_item(acl_nv)

    def delete_list(self, ii: InstanceRoute, ch: DataChange):
        debug_confh(self.__class__.__name__ + " delete triggered")
        KNOT.unset_section(section="acl")


class RRHelpers:
    # Create RR object from "rdata" json node
    @staticmethod
    def rr_from_rdata_item(domain_name: str, rr_owner: str, rr_ttl: int, rr_type: str, rdata_item: JsonNodeT) -> RRecordBase:
        try:
            if rr_type == "A":
                new_rr = ARecord(domain_name, rr_ttl)
                new_rr.owner = rr_owner
                new_rr.address = rdata_item["A"]["address"]
            elif rr_type == "AAAA":
                new_rr = AAAARecord(domain_name, rr_ttl)
                new_rr.owner = rr_owner
                new_rr.address = rdata_item["AAAA"]["address"]
            elif rr_type == "NS":
                new_rr = NSRecord(domain_name, rr_ttl)
                new_rr.owner = rr_owner
                new_rr.nsdname = rdata_item["NS"]["nsdname"]
            elif rr_type == "MX":
                new_rr = MXRecord(domain_name, rr_ttl)
                new_rr.owner = rr_owner
                new_rr.exchange = rdata_item["MX"]["exchange"]
            else:
                new_rr = None
        except KeyError:
            new_rr = None

        return new_rr


def register_conf_handlers(ds: BaseDatastore):
    CONF_DATA_HANDLES.register(KnotConfServerListener(ds, "/dns-server:dns-server/server-options"))
    CONF_DATA_HANDLES.register(KnotConfLogListener(ds, "/dns-server:dns-server/knot-dns:log"))
    CONF_DATA_HANDLES.register(KnotConfZoneListener(ds, "/dns-server:dns-server/zones/zone"))
    CONF_DATA_HANDLES.register(KnotConfControlListener(ds, "/dns-server:dns-server/knot-dns:control-socket"))
    CONF_DATA_HANDLES.register(KnotConfAclListener(ds, "/dns-server:dns-server/access-control-list"))

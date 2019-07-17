from enum import Enum
from typing import List, Union, Dict, Any, Optional
from threading import Lock

from jetconf.helpers import LogHelpers
from jetconf.errors import BackendError

from libknot.control import KnotCtl, KnotCtlType, KnotCtlError
import subprocess
from . import shared_objs as so

JsonNodeT = Union[Dict[str, Any], List[Any], str, int]
debug_knot = LogHelpers.create_module_dbg_logger(__name__)


class KnotError(BackendError):
    pass


class KnotApiStateError(KnotError):
    pass


class KnotInternalError(KnotError):
    pass


class KnotApiError(KnotError):
    pass


class KnotConfState(Enum):
    NONE = 0
    CONF = 1
    ZONE = 2


class Acl:
    id: str
    ip: str
    actions: str

    def __init__(self, id, ip):
        self.id = id
        self.ip = ip
        self.actions = []


class ZoneAcl:
    zone_id: str
    acl: []

    def __init__(self, zone_id, acl):
        self.zone_id = zone_id
        self.acl = acl


class KnotConfig(KnotCtl):

    @staticmethod
    def systemd_knot(command: str):

        try:
            resp = subprocess.check_output(["sudo", "systemctl", command, "knot"], timeout=10).decode("utf-8")
        except subprocess.TimeoutExpired as te:
            resp = str(te)

        return resp

    def __init__(self):
        super().__init__()
        self.sock_path = ""
        self.connected = False
        self.socket_lock = Lock()
        self.conf_state = KnotConfState.NONE

        self.remote_acl = []
        self.zone_acl = []

    def set_socket(self, sock_path: str):
        self.sock_path = sock_path

    def knot_connect(self):
        if self.connected:
            raise KnotApiError("Knot socket already opened")

        if not self.socket_lock.acquire(blocking=True, timeout=5):
            raise KnotApiError("Cannot acquire Knot socket lock")

        try:
            self.connect(self.sock_path)
        except KnotCtlError:
            self.socket_lock.release()
            raise KnotApiError("Cannot connect to Knot socket")
        self.connected = True

    def knot_disconnect(self):
        self.send(KnotCtlType.END)
        self.close()
        self.connected = False
        self.socket_lock.release()

    def flush_socket(self):
        pass

    # Starts a new transaction for configuration data
    def begin(self):
        if self.conf_state == KnotConfState.NONE:
            self.send_block("conf-begin")
            try:
                self.receive_block()
                self.conf_state = KnotConfState.CONF
            except KnotCtlError as e:
                raise KnotInternalError(str(e))

    # Starts a new transaction for zone data
    def begin_zone(self):
        if self.conf_state == KnotConfState.NONE:
            self.send_block("zone-begin")
            try:
                self.receive_block()
                self.conf_state = KnotConfState.ZONE
            except KnotCtlError as e:
                raise KnotInternalError(str(e))

    # Commits the internal KnotDNS transaction
    def commit(self):
        if self.conf_state == KnotConfState.CONF:
            self.send_block("conf-commit")
        elif self.conf_state == KnotConfState.ZONE:
            self.send_block("zone-commit")
        else:
            raise KnotApiStateError()

        try:
            self.receive_block()
            self.conf_state = KnotConfState.NONE
        except KnotCtlError as e:
            raise KnotInternalError(str(e))

    # Aborts the internal KnotDNS transaction
    def abort(self):
        if self.conf_state == KnotConfState.CONF:
            self.send_block("conf-abort")
        elif self.conf_state == KnotConfState.ZONE:
            self.send_block("zone-abort")
        else:
            raise KnotApiStateError()

        try:
            self.receive_block()
            self.conf_state = KnotConfState.NONE
        except KnotCtlError as e:
            raise KnotInternalError(str(e))

    # Deletes a whole section from Knot configuration
    def unset_section(self, section: str, identifier: str = None) -> JsonNodeT:
        if not self.connected:
            raise KnotApiError("Knot socket is closed")

        self.send_block("conf-unset", section=section, identifier=identifier)
        try:
            resp = self.receive_block()
        except KnotCtlError as e:
            resp = {}
            err_str = str(e)
            if err_str != "not exists":
                raise KnotInternalError(err_str)

        return resp

    # Low-level methods for setting and deleting values from Knot configuration
    def set_item(self, section: str, identifier: Optional[str], item: str, value: str) -> JsonNodeT:
        if not self.connected:
            raise KnotApiError("Knot socket is closed")

        if value is not None:
            if isinstance(value, (int, bool)):
                value = str(value).lower()
            self.send_block("conf-set", section=section, identifier=identifier, item=item, data=value)
            try:
                resp = self.receive_block()
            except KnotCtlError as e:
                raise KnotInternalError(str(e))
        else:
            resp = {}

        return resp

    def unset_item(self, section: str, identifier: Optional[str], item: str, zone: str = None) -> JsonNodeT:
        if not self.connected:
            raise KnotApiError("Knot socket is closed")

        self.send_block("conf-unset", section=section, identifier=identifier, item=item, zone=zone)
        try:
            resp = self.receive_block()
        except KnotCtlError as e:
            raise KnotInternalError(str(e))

        return resp

    def set_item_list(self, section: str, identifier: Optional[str], item: str, value: List[str]) -> List[JsonNodeT]:
        if not self.connected:
            raise KnotApiError("Knot socket is closed")

        resp_list = []
        for data_item in value:
            self.send_block("conf-set", section=section, identifier=identifier, item=item, data=data_item)
            try:
                resp = self.receive_block()
                resp_list.append(resp)
            except KnotCtlError as e:
                raise KnotInternalError(str(e))

        return resp_list

    def acl_set(self):

        for racl in self.remote_acl:
            if racl.actions:
                self.set_item(
                    section="acl",
                    identifier=None,
                    item="id",
                    value=racl.id
                )
                self.set_item(
                    section="acl",
                    identifier=racl.id,
                    item="address",
                    value=racl.ip
                )
                self.set_item_list(
                    section="acl",
                    identifier=racl.id,
                    item="action",
                    value=racl.actions
                )

        for zacl in self.zone_acl:
            if zacl.acl:
                self.set_item_list(
                    section="zone",
                    identifier=zacl.zone_id,
                    item="acl",
                    value=zacl.acl
                )

    def zone_set(self, zone) -> JsonNodeT:
        domain = zone.get("domain")

        acl = []

        # set domain
        self.set_item(
            section="zone",
            identifier=None,
            item="domain",
            value=domain
        )

        if 'description' in zone:
            self.set_item(
                section="zone",
                identifier=domain,
                item="comment",
                value=zone.get("description")
            )

        if 'file' in zone:
            path = zone.get("file")
            if path.startswith("/"):
                storage, file = path.rsplit("/", 1)
            else:
                storage = so.ZONES_DIR
                file = path
        else:
            storage = so.ZONES_DIR
            file = domain + "zone"
        self.set_item_list(
            section="zone",
            identifier=domain,
            item="storage",
            value=[storage]
        )

        self.set_item_list(
            section="zone",
            identifier=domain,
            item="file",
            value=[file]
        )

        if 'master' in zone:
            self.set_item_list(
                section="zone",
                identifier=domain,
                item="master",
                value=zone.get("master", [])
            )
            for mas in zone.get("master", []):
                acl.append(mas + "_acl")
                for racl in self.remote_acl:
                    if racl.id == (mas + "_acl"):
                        if "notify" not in racl.actions:
                            racl.actions.append("notify")
            
        if 'allow-update' in zone:

            for up in zone.get("allow-update", []):
                acl.append(up + "_acl")
                for racl in self.remote_acl:
                    if racl.id == (up + "_acl"):
                        if "update" not in racl.actions:
                            racl.actions.append("update")

        if 'notify' in zone:
            # set notify
            self.set_item_list(
                section="zone",
                identifier=domain,
                item="notify",
                value=zone.get("notify", {}).get("recipient", [])
            )
            for rec in zone.get("notify", {}).get("recipient", []):
                acl.append(rec + "_acl")
                for racl in self.remote_acl:
                    if racl.id == (rec + "_acl"):
                        if "transfer" not in racl.actions:
                            racl.actions.append("transfer")

        notin = True
        for zacl in self.zone_acl:
            if zacl.zone_id == domain:
                notin = False
        if notin:
            self.zone_acl.append(ZoneAcl(zone_id=domain, acl=acl))

    def remote_set(self, remote) -> JsonNodeT:
        name = remote.get("name")
        ip_addr = remote.get("remote", {}).get("ip-address")

        # set remote-server
        self.set_item(
            section="remote",
            identifier=None,
            item="id",
            value=name
        )

        # set description
        if 'description' in remote:
            self.set_item(
                section="remote",
                identifier=name,
                item="comment",
                value=remote.get("description")
            )
        if 'port' in remote['remote']:
            address = ip_addr + "@" + str(remote.get("remote", {}).get("port"))
        else:
            address = ip_addr

        # set address
        self.set_item_list(
            section="remote",
            identifier=name,
            item="address",
            value=[address]
        )

        notin = True
        for acl in self.remote_acl:
            if acl.id == (name+"_acl"):
                notin = False
        if notin:
            new = Acl(id=(name+"_acl"), ip=ip_addr)
            self.remote_acl.append(new)

    def config_set(self, config: JsonNodeT):
        if not self.connected:
            raise KnotApiError("Knot socket is closed")

        if 'cznic-dns-server-simple:dns-server' in config:
            conf = config['cznic-dns-server-simple:dns-server']
        else:
            conf = config

        if "zones-dir" in conf:
            so.ZONES_DIR = conf["zones-dir"]

        self.remote_acl = []
        self.zone_acl = []
        self.unset_section(section="zone")
        self.unset_section(section="acl")
        self.unset_section(section="remote")

        if 'remote-server' in conf:
            for rem_server in conf['remote-server']:
                self.remote_set(remote=rem_server)

        if 'zone' in conf['zones']:
            for zone in conf['zones']['zone']:
                self.zone_set(zone=zone)

        self.acl_set()

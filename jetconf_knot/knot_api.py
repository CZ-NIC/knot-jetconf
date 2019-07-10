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

    # ZONE CONFIG

    # Returns a status data of all or one specific DNS zone
    def zone_status(self, domain_name: str = None) -> JsonNodeT:
        if not self.connected:
            raise KnotApiError("Knot socket is closed")

        try:
            self.send_block("zone-status", zone=domain_name)
            resp = self.receive_block()
        except KnotCtlError as e:
            raise KnotInternalError(str(e))
        return resp

    # Purges all zone data
    def zone_purge(self, domain_name: str = None) -> JsonNodeT:
        if not self.connected:
            raise KnotApiError("Knot socket is closed")

        self.send_block("zone-purge", zone=domain_name)
        try:
            resp = self.receive_block()
        except KnotCtlError as e:
            raise KnotInternalError(str(e))

        return resp

    # Adds a new DNS zone to configuration section
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

        if zone['role'] == 'slave':
            # set master
            self.set_item_list(
                section="zone",
                identifier=domain,
                item="master",
                value=zone.get("master", [])
            )
            for mas in zone.get("master", []):
                acl.append(mas + "_acl")

            self.set_item_list(
                section="zone",
                identifier=domain,
                item="storage",
                value=[so.ZONES_DIR]
            )
            file_name = domain + '.zone'
            if file_name == '..zone':
                file_name = "root.zone"
            self.set_item_list(
                section="zone",
                identifier=domain,
                item="file",
                value=[file_name]
            )

        elif zone['role'] == 'master':
            # set zonefile
            path = zone.get("file")
            if path.startswith("/"):
                storage, file = path.rsplit("/", 1)
            else:
                storage = so.ZONES_DIR
                file = path

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

        if acl:
            # this must be done because simple-dns-model dont have acl
            self.set_item_list(
                section="zone",
                identifier=domain,
                item="acl",
                value=acl
            )

    # Removes a DNS zone from configuration section
    def zone_remove(self, domain_name: str, purge_data: bool) -> JsonNodeT:
        resp = self.unset_item(section="zone", identifier=domain_name, item="domain")
        if purge_data:
            self.zone_purge(domain_name)
        return resp

    # Reads zone data and converts them to YANG model compliant data tree
    def zone_read(self, domain_name: str) -> JsonNodeT:
        if not self.connected:
            raise KnotApiError("Knot socket is closed")

        try:
            self.send_block("zone-read", zone=domain_name)
            resp = self.receive_block()
        except KnotCtlError as e:
            raise KnotInternalError(str(e))

        if domain_name[-1] != ".":
            domain_name += "."

        return resp[domain_name]

    # REMOTE-SERVER CONFIG

    # Returns a status data of all or one specific remote-server
    def remote_server_status(self, name: str = None) -> JsonNodeT:
        if not self.connected:
            raise KnotApiError("Knot socket is closed")

        try:
            self.send_block("remote-status", remote=name)
            resp = self.receive_block()
        except KnotCtlError as e:
            raise KnotInternalError(str(e))
        return resp

    # Purges all zone data
    def remote_server_purge(self, name: str = None) -> JsonNodeT:
        if not self.connected:
            raise KnotApiError("Knot socket is closed")

        self.send_block("remote-purge", zone=name)
        try:
            resp = self.receive_block()
        except KnotCtlError as e:
            raise KnotInternalError(str(e))

        return resp

    # Adds a new DNS zone to configuration section
    def remote_server_set(self, remote) -> JsonNodeT:
        name = remote.get("name")

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
            address = remote.get("remote", {}).get("ip-address") + "@" + str(remote.get("remote", {}).get("port"))
        else:
            address = remote.get("remote", {}).get("ip-address")

        # set address
        self.set_item_list(
            section="remote",
            identifier=name,
            item="address",
            value=[address]
        )

        # create acl
        self.set_item(
            section="acl",
            identifier=None,
            item="id",
            value=name + "_acl"
        )
        self.set_item(
            section="acl",
            identifier=name + "_acl",
            item="address",
            value=remote.get("remote", {}).get("ip-address")
        )
        self.set_item(
            section="acl",
            identifier=name + "_acl",
            item="action",
            value="transfer"
        )



    # Removes a DNS zone from configuration section
    def remote_server_remove(self, name: str, purge_data: bool) -> JsonNodeT:
        resp = self.unset_item(section="remote", identifier=name, item="name")
        if purge_data:
            self.zone_purge(name)
        return resp

    def config_set(self, config: JsonNodeT):
        if not self.connected:
            raise KnotApiError("Knot socket is closed")

        if 'cznic-dns-server-simple:dns-server' in config:
            conf = config['cznic-dns-server-simple:dns-server']
        else:
            conf = config

        if "zones-dir" in conf:
            so.ZONES_DIR = conf["zones-dir"]

        self.unset_section(section="acl")

        if 'remote-server' in conf:
            # set remote server configuration
            self.unset_section(section="remote")
            for rem_server in conf['remote-server']:

                self.remote_server_set(remote=rem_server)

        if 'zone' in conf['zones']:
            # set zone configuration
            self.unset_section(section="zone")
            for zone in conf['zones']['zone']:

                self.zone_set(zone=zone)

    # Reads all configuration data and converts them to YANG model compliant data tree
    def config_read(self) -> JsonNodeT:
        if not self.connected:
            raise KnotApiError("Knot socket is closed")

        try:
            self.send_block("conf-read")
            resp = self.receive_block()
        except KnotCtlError as e:
            raise KnotInternalError(str(e))

        remote_servers_dict = []
        if 'remote' in resp:

            for remote in resp['remote']:
                remote_dict = {"name": remote}
                if 'address' in resp['remote'][remote]:
                    if '@' in resp['remote'][remote]['address'][0]:
                        addr, port = resp['remote'][remote]['address'][0].split('@')

                        if int(port) == 53:
                            remote_dict['remote'] = {"ip-address": addr}
                        else:
                            remote_dict['remote'] = {"ip-address": addr,
                                                     "port": int(port)}
                    else:
                        remote_dict['remote'] = {"ip-address": resp['remote'][remote]['address'][0]}
                    remote_servers_dict.append(remote_dict.copy())

        zones_dict = []
        if 'zone' in resp:

            for zone in resp['zone']:
                zone_dict = {'domain': zone, 'role': "master"}

                if 'file' in resp['zone'][zone]:
                    file = str(resp['zone'][zone]['file'])[2:-2]
                    if 'storage' in resp['zone'][zone]:
                        zone_dict['file'] = str(resp['zone'][zone]['storage'])[2:-2] + "/" + file
                    else:
                        zone_dict['file'] = file

                if 'master' in resp['zone'][zone]:
                    zone_dict['master'] = resp['zone'][zone]['master']

                if 'notify' in resp['zone'][zone]:
                    zone_dict['notify'] = {"recipient": resp['zone'][zone]['notify']}
                    zone_dict['role'] = "slave"

                zones_dict.append(zone_dict.copy())

        conf_data = {"remote-server": [], "zones": {"zone": []}}

        if remote_servers_dict:
            conf_data['remote-server'] = remote_servers_dict
        if zones_dict:
            conf_data['zones']['zone'] = zones_dict

        return {"cznic-dns-server-simple:dns-server": conf_data}

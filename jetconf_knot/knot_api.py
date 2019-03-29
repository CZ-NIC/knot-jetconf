from enum import Enum
from typing import List, Union, Dict, Any, Optional
from threading import Lock

from jetconf.helpers import LogHelpers
from jetconf.errors import BackendError

from libknot.control import KnotCtl, KnotCtlType, KnotCtlError
import subprocess

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


class RRecordBase:
    def __init__(self, owner: str, res_type: str, ttl: Optional[int] = None):
        self.owner = owner or "@"
        self.type = res_type
        self.ttl = ttl

    def rrdata_format(self) -> str:
        raise NotImplementedError("Not implemented in base class")

    @property
    def ttl_str(self) -> Optional[str]:
        return str(self.ttl) if self.ttl is not None else None


class SOARecord(RRecordBase):
    def __init__(self):
        super().__init__("@", "SOA")
        self.mname = None  # type: str
        self.rname = None  # type: str
        self.serial = None  # type: str
        self.refresh = None  # type: str
        self.retry = None  # type: str
        self.expire = None  # type: str
        self.minimum = None  # type: str

    def rrdata_format(self) -> str:
        return "{} {} {} {} {} {} {}".format(
            self.mname, self.rname, self.serial, self.refresh, self.retry, self.expire, self.minimum
        )


class CNAMERecord(RRecordBase):
    def __init__(self, owner: str, ttl: Optional[int] = None):
        super().__init__(owner, "CNAME", ttl)
        self.cname = None  # type: str

    def rrdata_format(self) -> str:
        return self.cname


class NSRecord(RRecordBase):
    def __init__(self, owner: str, ttl: Optional[int] = None):
        super().__init__(owner, "NS", ttl)
        self.nsdname = None  # type: str

    def rrdata_format(self) -> str:
        return self.nsdname


class ARecord(RRecordBase):
    def __init__(self, owner: str, ttl: Optional[int] = None):
        super().__init__(owner, "A", ttl)
        self.address = None  # type: str

    def rrdata_format(self) -> str:
        return self.address


class AAAARecord(RRecordBase):
    def __init__(self, owner: str, ttl: Optional[int] = None):
        super().__init__(owner, "AAAA", ttl)
        self.address = None  # type: str

    def rrdata_format(self) -> str:
        return self.address


class MXRecord(RRecordBase):
    def __init__(self, owner: str, ttl: Optional[int] = None):
        super().__init__(owner, "MX", ttl)
        self.preference = None  # type: str
        self.exchange = None  # type: str

    def rrdata_format(self) -> str:
        return self.exchange


class KnotConfig(KnotCtl):

    def systemd_knot(self, command: str, password: str = None):
        # cmd = "echo '{0}' | sudo - S systemctl {1} knot".format(password, command)
        cmd = "sudo systemctl {0} knot".format(command)

        # return subprocess.check_output([cmd], timeout=10)
        return subprocess.check_output(["sudo", "systemctl", command, "knot"], timeout=10)

    def restart(self, passwd: str = None):
        try:
            resp = self.systemd_knot("restart", passwd)
        except subprocess.TimeoutExpired as te:
            resp = str(te)
        return resp

    def start(self, passwd: str = None):
        try:
            resp = self.systemd_knot("start", passwd)
        except subprocess.TimeoutExpired as te:
            resp = str(te)
        return resp

    def stop(self, passwd: str = None):
        try:
            resp = self.systemd_knot("stop", passwd)
        except subprocess.TimeoutExpired as te:
            resp = str(te)
        return resp

    def reload(self, passwd: str = None):
        try:
            resp = self.systemd_knot("reload", passwd)
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
    def zone_new(self, domain_name: str) -> JsonNodeT:
        resp = self.set_item(section="zone", identifier=None, item="domain", value=domain_name)
        return resp

    # Removes a DNS zone from configuration section
    def zone_remove(self, domain_name: str, purge_data: bool) -> JsonNodeT:
        resp = self.unset_item(section="zone", identifier=domain_name, item="domain")
        if purge_data:
            self.zone_purge(domain_name)
        return resp

    # Adds a resource record to DNS zone
    def zone_add_record(self, domain_name: str, rr: RRecordBase) -> JsonNodeT:
        if not self.connected:
            raise KnotApiError("Knot socket is closed")

        try:
            res_data = rr.rrdata_format()
            self.send_block("zone-set", zone=domain_name, owner=rr.owner, ttl=rr.ttl_str, rtype=rr.type, data=res_data)

            debug_knot("Inserting zone \"{}\" RR, type=\"{}\", owner=\"{}\", ttl={}, data=\"{}\"".format(
                domain_name, rr.type, rr.owner, rr.ttl_str, res_data
            ))
            resp = self.receive_block()
        except KnotCtlError as e:
            raise KnotInternalError(str(e))
        return resp

    # Removes a resource record from DNS zone
    # If the zone contains two or more records with the same owner and type, selector parameter can specify
    # which one to remove. Usually it is the same as record data.
    def zone_del_record(self, domain_name: str, owner: str, rr_type: str, selector: str = None) -> JsonNodeT:
        if not self.connected:
            raise KnotApiError("Knot socket is closed")

        try:
            self.send_block("zone-unset", zone=domain_name, owner=owner, rtype=rr_type, data=selector)
            resp = self.receive_block()
        except KnotCtlError as e:
            raise KnotInternalError(str(e))
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

    def config_set(self, config: JsonNodeT):
        if not self.connected:
            raise KnotApiError("Knot socket is closed")

        conf = config['cznic-dns-slave-server:dns-server']

        # set remote server configuration
        self.unset_section(section="remote")
        for rem_server in conf['remote-server']:

            name = rem_server.get("name")
            # set remote-server
            self.set_item(
                section="remote",
                identifier=None,
                item="id",
                value=name
            )

            # set description
            if 'description' in rem_server:
                self.set_item(
                    section="remote",
                    identifier=name,
                    item="comment",
                    value=rem_server.get("description")
                )

            address = rem_server.get("remote", {}).get("ip-address") + "@" + str(rem_server.get("remote", {}).get("port"))

            # set address
            self.set_item_list(
                section="remote",
                identifier=name,
                item="address",
                value=[address]
            )

        # set zone configuration
        self.unset_section(section="zone")
        for zone in conf['zones']['zone']:
            domain = zone.get("domain")

            # set domain
            self.set_item(
                section="zone",
                identifier=None,
                item="domain",
                value=domain
            )

            # set description
            if 'description' in zone:
                self.set_item(
                    section="zone",
                    identifier=domain,
                    item="comment",
                    value=zone.get("description")
                )

            # set master
            self.set_item_list(
                section="zone",
                identifier=domain,
                item="master",
                value=zone.get("master", [])
            )

            # set notify
            self.set_item_list(
                section="zone",
                identifier=domain,
                item="notify",
                value=zone.get("notify", {}).get("recipient", [])
            )

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
                zone_dict = {'domain': zone}

                if 'master' in resp['zone'][zone]:
                    zone_dict['master'] = resp['zone'][zone]['master']
                if 'notify' in resp['zone'][zone]:
                    zone_dict['notify'] = {"recipient": resp['zone'][zone]['notify']}

                zones_dict.append(zone_dict.copy())

        conf_data = {"remote-server": [], "zones": {"zone": []}}

        if remote_servers_dict:
            conf_data['remote-server'] = remote_servers_dict
        if zones_dict:
            conf_data['zones']['zone'] = zones_dict

        return {"cznic-dns-slave-server:dns-server": conf_data}

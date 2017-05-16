import json

from colorlog import error

from yangson.datamodel import DataModel
from yangson.instance import NonexistentInstance

from .config import CONFIG_KNOT
from .data import JsonDatastore
from .knot_api import KNOT, KnotError, knot_connect, knot_disconnect
from .helpers import ErrorHelpers


class UserDatastore(JsonDatastore):
    def __init__(self, dm: DataModel, json_file: str, with_nacm: bool = False):
        super().__init__(dm, json_file, with_nacm)
        self.name = "DNS Data"

        # Set datastore commit callbacks
        self.commit_begin_callback = knot_connect
        self.commit_end_callback = knot_disconnect

        # Initialize Knot control interface
        KNOT.set_socket(CONFIG_KNOT["SOCKET"])

    def load(self):
        super().load()

        # Read KnotDNS configuration and save it to the datastore
        try:
            KNOT.knot_connect()
            knot_conf_json = KNOT.config_read()
            KNOT.knot_disconnect()
            new_root = self._data.put_member("dns-server:dns-server", knot_conf_json["dns-server:dns-server"], raw=True).top()
            self.set_data_root(new_root)
        except KnotError as e:
            error("Cannot load KnotDNS configuration, reason: {}".format(ErrorHelpers.epretty(e)))

    def save(self):
        # Just need to save NACM data,
        # everything else is loaded dynamically on startup or when requested
        try:
            nacm_raw = self._data["ietf-netconf-acm:nacm"].raw_value()
            data_raw = {"ietf-netconf-acm:nacm": nacm_raw}
        except NonexistentInstance:
            # NACM data not present
            data_raw = {}

        with open(self.json_file, "w") as jfd:
            json.dump(data_raw, jfd, indent=4)
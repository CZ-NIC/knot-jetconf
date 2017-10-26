import json

from colorlog import error

from yangson.instance import NonexistentInstance

from jetconf import config
from jetconf.data import JsonDatastore
from jetconf.helpers import ErrorHelpers

from .knot_api import KnotConfig, KnotError


class UserDatastore(JsonDatastore):
    def load(self):
        super().load()

        knot = KnotConfig()

        # Initialize Knot control interface
        try:
            knot.set_socket(config.CFG.root["KNOT"]["SOCKET"])
        except KeyError:
            error("Cannot find KNOT/SOCKET item in jetconf config file")

        # Read KnotDNS configuration and save it to the datastore
        try:
            knot.knot_connect()
            knot_conf_json = knot.config_read()
            knot.knot_disconnect()
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

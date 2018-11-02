import json

from colorlog import error

from yangson.instance import NonexistentInstance

from jetconf import config
from jetconf.data import JsonDatastore
from jetconf.helpers import ErrorHelpers

from .exns_api import NsConfig, NsApiError


class UserDatastore(JsonDatastore):
    def load(self):
        super().load()

        exns = NsConfig()

        # Initialize Knot control interface
        try:
            exns.set_cfg_file_path(config.CFG.root["NS"]["CONFFILE"])
        except KeyError:
            error("Cannot find NS config file path in JETCONF's config file")

        # Read KnotDNS configuration and save it to the datastore
        try:
            knot_conf_json = exns.config_read()
            new_root = self._data.put_member("dns-server:dns-server", knot_conf_json["dns-server:dns-server"], raw=True).top()
            self.set_data_root(new_root)
        except NsApiError as e:
            error("Cannot load ExDNS configuration, reason: {}".format(ErrorHelpers.epretty(e)))

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

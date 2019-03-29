from colorlog import error, info
import json
from jetconf import config
from jetconf.data import JsonDatastore
from jetconf.helpers import ErrorHelpers
from yangson.exceptions import NonexistentInstance

from .knot_api import KnotConfig, KnotError
from . import shared_objs as so


class UserDatastore(JsonDatastore):
    def load(self):
        super().load()

        so.KNOT = KnotConfig()
        load_data = False

        # Initialize Knot control interface
        try:
            so.KNOT.set_socket(config.CFG.root["KNOT"]["SOCKET"])
            load_data = config.CFG.root['KNOT']['LOAD_CONF']
        except KeyError as ke:
            error("Cannot set KNOT configuration from configuration YAML file, KeyError: {}".format(ke))
            so.KNOT.set_socket('/run/knot/knot.sock')

        if load_data:
            # Read KnotDNS configuration and save it to the datastore
            info("Loading configuration from KnotDNS")
            try:

                so.KNOT.knot_connect()
                knot_conf_json = so.KNOT.config_read()
                so.KNOT.knot_disconnect()
                new_root = self._data.put_member("cznic-dns-slave-server:dns-server",
                                                 knot_conf_json["cznic-dns-slave-server:dns-server"],
                                                 raw=True).top()
                self.set_data_root(new_root)
            except KnotError as e:
                error("Cannot load KnotDNS configuration, reason: {}".format(ErrorHelpers.epretty(e)))

        else:
            # Set datastore configuration to KnotDNS
            info("Setting datastore configuration to KnotDNS")
            try:
                so.KNOT.knot_connect()
                so.KNOT.begin()
                so.KNOT.config_set(self.get_data_root().add_defaults().value)
                so.KNOT.commit()
                so.KNOT.knot_disconnect()
            except KnotError as e:
                error("Cannot set KnotDNS configuration, reason: {}".format(ErrorHelpers.epretty(e)))

    def save(self):

        if config.CFG.root['KNOT']['LOAD_CONF']:
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

        else:
            super().save()

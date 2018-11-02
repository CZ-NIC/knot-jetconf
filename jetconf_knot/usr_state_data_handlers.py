from yangson.instance import InstanceRoute
from jetconf.helpers import JsonNodeT
from jetconf.handler_base import StateDataContainerHandler, StateDataListHandler
from jetconf.data import BaseDatastore

_DUMMYDATA = [
    {
        "name": "example.com",
        "class": "IN",
        "rrset": [
            {
                "ttl": 3600,
                "rdata": [
                    {
                        "SOA": {
                            "expire": 1209600,
                            "refresh": 10800,
                            "rname": "hostmaster.example.com",
                            "minimum": 7200,
                            "serial": 2010111201,
                            "retry": 3600,
                            "mname": "dns1.example.com"
                        }
                    }
                ],
                "type": "iana-dns-parameters:SOA",
                "owner": "example.com"
            },
            {
                "ttl": 3600,
                "rdata": [
                    {
                        "A": {
                            "address": "192.0.2.3"
                        }
                    }
                ],
                "type": "iana-dns-parameters:A",
                "owner": "mail.example.com"
            }
        ]
    }
]


# ---------- User-defined handlers follow ----------
class ZoneDataStateHandler(StateDataListHandler):
    def generate_list(self, node_ii: InstanceRoute, username: str, staging: bool) -> JsonNodeT:
        # Read all zones contents
        return _DUMMYDATA

    def generate_item(self, node_ii: InstanceRoute, username: str, staging: bool) -> JsonNodeT:
        # Requesting contents of only one specific zone
        domain_name = node_ii[1].keys.get(("name", None))

        retval = {}
        for zone in _DUMMYDATA:
            if zone["name"] == domain_name:
                retval = zone

        return retval


# Instantiate state data handlers
def register_state_handlers(ds: BaseDatastore):
    zdsh = ZoneDataStateHandler(ds, "/dns-zones-state:zone")
    ds.handlers.state.register(zdsh)

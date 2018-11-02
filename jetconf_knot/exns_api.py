import yaml
from yaml.parser import ParserError
from typing import List, Union, Dict, Any
from jetconf.errors import BackendError

JsonNodeT = Union[Dict[str, Any], List[Any], str, int]


class NsApiError(BackendError):
    pass


class NsConfig:
    def __init__(self):
        self.file_path = ""

    def set_cfg_file_path(self, path: str):
        self.file_path = path

    # Reads all configuration data and converts them to YANG model compliant data tree
    def config_read(self) -> JsonNodeT:
        in_yaml = {}

        try:
            with open(self.file_path) as f:
                in_yaml = yaml.load(f)
        except FileNotFoundError as e:
            raise NsApiError(str(e))
        except ParserError as e:
            raise NsApiError(str(e))

        out_conf_dnss = {}

        out_conf_data = {
            "dns-server:dns-server": out_conf_dnss
        }

        out_conf_dnss["description"] = "Configuration acquired from ExNS config file"

        # "server" section
        server_in = in_yaml.get("SERVER")
        if server_in is not None:
            servopts_out = {
                "listen-endpoint": [
                    {
                        "name": "1",
                        "ip-address": server_in["BIND"],
                        "port": server_in["PORT"]
                    }
                ]
            }

            out_conf_dnss["server-options"] = servopts_out

        # "zone" section
        zones_in = in_yaml.get("ZONECFG")
        if zones_in is not None:
            zone_out = []

            for zonecfg in zones_in:
                zone_item_out = {
                    "domain": zonecfg["DOMAIN"].rstrip(".")
                }

                try:
                    zonefile = zonecfg["FILE"]
                    zone_item_out["file"] = zonefile
                except KeyError:
                    pass

                zone_out.append(zone_item_out)

            try:
                out_conf_dnss_zone = out_conf_dnss["zone"]
                out_conf_dnss_zone["zone"] = zone_out
            except KeyError:
                out_conf_dnss["zones"] = {
                    "zone": zone_out
                }

        return out_conf_data

    # Generates ExNS config file from Configuration data tree
    def config_write(self, data: JsonNodeT):
        out_yaml = {}

        servopts = data.get("server-options")
        if servopts is not None:
            server_out = {}

            ep = servopts.get("listen-endpoint", [])
            if len(ep) > 0:
                server_out["BIND"] = ep[0]["ip-address"]
                server_out["PORT"] = ep[0]["port"]

            out_yaml["SERVER"] = server_out

        zonescfg = data.get("zones", {}).get("zone")
        if zonescfg is not None:
            zonescfg_out = []

            for zonecfg_in in zonescfg:
                z_out = {}

                domain = zonecfg_in.get("domain")
                if domain is not None:
                    z_out["DOMAIN"] = domain

                zonefile = zonecfg_in.get("file")
                if zonefile is not None:
                    z_out["FILE"] = zonefile

                zonescfg_out.append(z_out)

            out_yaml["ZONECFG"] = zonescfg_out

        try:
            with open(self.file_path, "w") as f:
                yaml.dump(out_yaml, f, default_flow_style=False)
        except FileNotFoundError as e:
            raise NsApiError(str(e))
        except IOError as e:
            raise NsApiError(str(e))

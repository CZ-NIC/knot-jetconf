from colorlog import error, info
from jetconf.helpers import JsonNodeT, LogHelpers
from jetconf.data import BaseDatastore
from . import shared_objs as so

debug_oph = LogHelpers.create_module_dbg_logger(__name__)

# ---------- User-defined handlers follow ----------


class OpHandlersContainer:
    def __init__(self, ds: BaseDatastore):
        self.ds = ds

    def reload_server_op(self, input_args: JsonNodeT, username: str) -> JsonNodeT:
        debug_oph(self.__class__.__name__ +
                  " reload server rpc triggered, user: {}".format(username))
        res = so.KNOT.systemd_knot("reload")
        if res is "":
            info("KnotDNS has been reloaded")
        else:
            error("KnotDNS reload failed, reason: {}".format(res))

    def restart_server_op(self, input_args: JsonNodeT, username: str) -> JsonNodeT:
        debug_oph(self.__class__.__name__ +
                  " restart server rpc triggered, user: {}".format(username))
        res = so.KNOT.systemd_knot("restart")
        if res is "":
            info("KnotDNS has been restarted")
        else:
            error("KnotDNS stop failed, reason: {}".format(res))

    def start_server_op(self, input_args: JsonNodeT, username: str) -> JsonNodeT:
        debug_oph(self.__class__.__name__ +
                  " start server rpc triggered, user: {}".format(username))
        res = so.KNOT.systemd_knot("start")
        if res is "":
            info("KnotDNS has been started")
        else:
            error("KnotDNS start failed, reason: {}".format(res))

    def stop_server_op(self, input_args: JsonNodeT, username: str) -> JsonNodeT:
        debug_oph(self.__class__.__name__ +
                  " stop server rpc triggered, user: {}".format(username))
        res = so.KNOT.systemd_knot("stop")
        if res is "":
            info("KnotDNS has been stopped")
        else:
            error("KnotDNS stop failed, reason: {}".format(res))


def register_op_handlers(ds: BaseDatastore):
    op_handlers_obj = OpHandlersContainer(ds)

    ds.handlers.op.register(op_handlers_obj.reload_server_op,
                            "cznic-dns-slave-server:reload-server")
    ds.handlers.op.register(op_handlers_obj.restart_server_op,
                            "cznic-dns-slave-server:restart-server")
    ds.handlers.op.register(op_handlers_obj.start_server_op,
                            "cznic-dns-slave-server:start-server")
    ds.handlers.op.register(op_handlers_obj.stop_server_op,
                            "cznic-dns-slave-server:stop-server")

from enum import Enum
from typing import Dict, List
from colorlog import error, warning as warn, info

from . import shared_objs as so
from jetconf.helpers import JsonNodeT
from jetconf.data import BaseDatastore

from .knot_api import SOARecord, ARecord, AAAARecord, MXRecord, CNAMERecord


# ---------- User-defined handlers follow ----------

OP_HANDLERS_IMPL = None     # type: OpHandlersContainer


class KnotZoneCmd(Enum):
    SET = 0
    UNSET = 1


class KnotOp:
    def __init__(self, cmd: KnotZoneCmd, op_input: JsonNodeT):
        self.cmd = cmd
        self.op_input = op_input


class OpHandlersContainer:
    def __init__(self):
        self.op_journal = {}     # type: Dict[str, List[KnotOp]]

    def zone_begin_transaction(self, input_args: JsonNodeT, username: str) -> JsonNodeT:
        self.op_journal[username] = []

    def zone_commit_transaction(self, input_args: JsonNodeT, username: str) -> JsonNodeT:
        try:
            usr_op_journal = self.op_journal[username]
        except KeyError:
            warn("zone_commit_transaction: Nothing to commit")
            return

        # Connect to Knot socket and start zone transaction
        so.KNOT.knot_connect()
        so.KNOT.begin_zone()

        for knot_op in usr_op_journal:
            input_args = knot_op.op_input
            domain = input_args["dns-zone-rpcs:zone"]
            if knot_op.cmd == KnotZoneCmd.SET:
                rr_type = input_args["dns-zone-rpcs:type"][0]
                if rr_type == "SOA":
                    rrdata = input_args["dns-zone-rpcs:SOA"]
                    rr = SOARecord()
                    rr.ttl = input_args["dns-zone-rpcs:ttl"]
                    rr.mname = rrdata["mname"]
                    rr.rname = rrdata["rname"]
                    rr.serial = rrdata["serial"]
                    rr.refresh = rrdata["refresh"]
                    rr.retry = rrdata["retry"]
                    rr.expire = rrdata["expire"]
                    rr.minimum = rrdata["minimum"]
                    so.KNOT.zone_add_record(domain, rr)
                elif rr_type == "A":
                    rrdata = input_args["dns-zone-rpcs:A"]
                    rr = ARecord(input_args["dns-zone-rpcs:owner"], input_args["dns-zone-rpcs:ttl"])
                    rr.address = rrdata["address"]
                    so.KNOT.zone_add_record(domain, rr)
                elif rr_type == "AAAA":
                    rrdata = input_args["dns-zone-rpcs:AAAA"]
                    rr = AAAARecord(input_args["dns-zone-rpcs:owner"], input_args["dns-zone-rpcs:ttl"])
                    rr.address = rrdata["address"]
                    so.KNOT.zone_add_record(domain, rr)
                elif rr_type == "MX":
                    rrdata = input_args["dns-zone-rpcs:MX"]
                    rr = MXRecord(input_args["dns-zone-rpcs:owner"], input_args["dns-zone-rpcs:ttl"])
                    rr.preference = rrdata["preference"]
                    rr.exchange = rrdata["exchange"]
                    so.KNOT.zone_add_record(domain, rr)
                elif rr_type == "CNAME":
                    rrdata = input_args["dns-zone-rpcs:CNAME"]
                    rr = CNAMERecord(input_args["dns-zone-rpcs:owner"], input_args["dns-zone-rpcs:ttl"])
                    rr.cname = rrdata["cname"]
                    so.KNOT.zone_add_record(domain, rr)

            elif knot_op.cmd == KnotZoneCmd.UNSET:
                input_args = knot_op.op_input
                domain = input_args["dns-zone-rpcs:zone"]
                owner = input_args.get("dns-zone-rpcs:owner")

                try:
                    rr_type = input_args["dns-zone-rpcs:type"][0]
                    rrdata = input_args["dns-zone-rpcs:" + rr_type]
                except KeyError:
                    rr_type = None
                    rrdata = None

                if rrdata:
                    if rr_type == "A":
                        rr = ARecord(input_args["dns-zone-rpcs:owner"], 0)
                        rr.address = rrdata["address"]
                    elif rr_type == "AAAA":
                        rr = AAAARecord(input_args["dns-zone-rpcs:owner"], 0)
                        rr.address = rrdata["address"]
                    elif rr_type == "MX":
                        rr = MXRecord(input_args["dns-zone-rpcs:owner"], 0)
                        rr.preference = rrdata["preference"]
                        rr.exchange = rrdata["exchange"]
                    elif rr_type == "CNAME":
                        rr = CNAMERecord(input_args["dns-zone-rpcs:owner"], 0)
                        rr.cname = rrdata["cname"]
                    else:
                        rr = None

                    selector = rr.rrdata_format() if rr is not None else None
                else:
                    selector = None

                so.KNOT.zone_del_record(domain, owner, rr_type, selector)

        so.KNOT.commit()
        so.KNOT.knot_disconnect()
        del self.op_journal[username]

    def zone_abort_transaction(self, input_args: JsonNodeT, username: str) -> JsonNodeT:
        try:
            del self.op_journal[username]
        except KeyError:
            warn("zone_abort_transaction: Nothing to abort")

    def zone_set(self, input_args: JsonNodeT, username: str) -> JsonNodeT:
        try:
            usr_op_journal = self.op_journal[username]
        except KeyError:
            warn("zone_set: Op transaction not started")
            return

        usr_op_journal.append(KnotOp(KnotZoneCmd.SET, input_args))

    def zone_unset(self, input_args: JsonNodeT, username: str) -> JsonNodeT:
        try:
            usr_op_journal = self.op_journal[username]
        except KeyError:
            warn("zone_set: Op transaction not started")
            return

        usr_op_journal.append(KnotOp(KnotZoneCmd.UNSET, input_args))


def get_op_container() -> OpHandlersContainer:
    return OP_HANDLERS_IMPL


def register_op_handlers(ds: BaseDatastore):
    global OP_HANDLERS_IMPL
    op_handlers_obj = OpHandlersContainer()
    OP_HANDLERS_IMPL = op_handlers_obj

    ds.handlers.op.register(op_handlers_obj.zone_begin_transaction, "dns-zone-rpcs:begin-transaction")
    ds.handlers.op.register(op_handlers_obj.zone_commit_transaction, "dns-zone-rpcs:commit-transaction")
    ds.handlers.op.register(op_handlers_obj.zone_abort_transaction, "dns-zone-rpcs:abort-transaction")
    ds.handlers.op.register(op_handlers_obj.zone_set, "dns-zone-rpcs:zone-set")
    ds.handlers.op.register(op_handlers_obj.zone_unset, "dns-zone-rpcs:zone-unset")


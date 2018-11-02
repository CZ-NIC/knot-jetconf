from jetconf.data import BaseDatastore


# ---------- User-defined handlers follow ----------

OP_HANDLERS_IMPL = None     # type: OpHandlersContainer


class OpHandlersContainer:
    pass


def get_op_container() -> OpHandlersContainer:
    return OP_HANDLERS_IMPL


def register_op_handlers(ds: BaseDatastore):
    global OP_HANDLERS_IMPL
    op_handlers_obj = OpHandlersContainer()
    OP_HANDLERS_IMPL = op_handlers_obj

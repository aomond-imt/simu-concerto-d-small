import json
import time
from collections import namedtuple

from esds.node import Node
from esds.plugins.power_states import PowerStates, PowerStatesComms


PING_SIZE = 84
IDLE_CONSO = 1.339
UPT_DURATION = 60
INTERFACE_NAME = "eth0"
COMMS_CONSO = 0.16
entry = namedtuple("entry", ["node_id", "nb_hops", "next_hop"])
ENTRY_SIZE = 56  # 8 + 8 + 8 + 32
REQUEST_SIZE = 257


def execute(api: Node):
    # Energy states
    node_cons = PowerStates(api, 0)
    comms_cons = PowerStatesComms(api)
    comms_cons.set_power(INTERFACE_NAME, 0, COMMS_CONSO, COMMS_CONSO)

    upt_count, nb_msg_sent, nb_msg_rcv = 0, 0, 0

    termination_list = api.args[0]
    with open("/home/aomond/leverages/uptimes_schedules/0-60.json") as f:
        uptimes_schedules = json.load(f)[api.node_id]
    map_shared_routing_table = {}
    routing_table = [
        entry(api.node_id, 0, api.node_id)
    ]
    for upt in uptimes_schedules:
        # Sleeping period
        api.turn_off()
        node_cons.set_power(0)
        api.wait(upt - api.read("clock"))
        if all(termination_list):
            break

        api.turn_on()
        upt_count += 1
        node_cons.set_power(IDLE_CONSO)
        api.send(INTERFACE_NAME, (api.node_id, "ping"), PING_SIZE, 0)
        nb_msg_sent += 1
        upt_end = upt + UPT_DURATION
        code, data = api.receivet(INTERFACE_NAME, timeout=upt_end - api.read("clock"))
        while data is not None:
            sender_id, payload = data
            nb_msg_rcv += 1
            if payload == "ping":
                data_to_send = []
                data_size = 0
                for e in routing_table:
                    if e not in map_shared_routing_table.setdefault(sender_id, set()):
                        map_shared_routing_table[sender_id].add(e)
                        data_to_send.append(e)
                        data_size += REQUEST_SIZE + ENTRY_SIZE
                api.send(INTERFACE_NAME, (api.node_id, data_to_send), data_size, 0)
                nb_msg_sent += 1
            else:
                for e in payload:
                    n_id, hop_count, _ = e
                    routing_table.append(entry(n_id, hop_count+1, sender_id))
            code, data = api.receivet(INTERFACE_NAME, timeout=upt_end - api.read("clock"))

        if len(routing_table) >= api.args[1]:
            termination_list[api.node_id] = True

    api.turn_off()
    node_cons.set_power(0)
    api.log(f"node_cons: {node_cons.energy}")
    api.log(f"comms_cons: {float(comms_cons.get_energy())}")
    api.log(f"nb_msg_sent: {nb_msg_sent}")
    api.log(f"nb_msg_rcv: {nb_msg_rcv}")
    api.log(f"upt_count: {upt_count}")
    api.log(f"time: {api.read('clock')}")
    api.log(f"routing_table: {routing_table}")

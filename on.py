import json

from esds.node import Node
from esds.plugins.power_states import PowerStates, PowerStatesComms

IDLE_CONSO = 1.339
STRESS_CONSO = 2.697
PING_SIZE = 84
UPT_DURATION = 60
INTERFACE_NAME = "eth0"
COMMS_CONSO = 0.16

# DATA SIZE
SERVICE_NAME_SIZE = 8  # Service mapped with id from 0 to 255
NODE_ID_SIZE = 8  # Nb nodes < 30
EXPORTED_VALUES_SIZE = 1_000  # High value to cover worst cases
SERVICE_TABLE_ENTRY_SIZE = SERVICE_NAME_SIZE + NODE_ID_SIZE + EXPORTED_VALUES_SIZE
REQUEST_SIZE = 257

ons_tasks = [
    [("run0", 10, ("run1", "run2", "run3"))],
    [("run1", 10, ())],
    [("run2", 10, ())],
    [("run3", 10, ())],
]


def execute(api: Node):
    # Energy states
    node_cons = PowerStates(api, 0)
    comms_cons = PowerStatesComms(api)
    comms_cons.set_power(INTERFACE_NAME, 0, COMMS_CONSO, COMMS_CONSO)

    # Metrics
    upt_count, sleep_time, upt_time, stress_time, nb_msg_sent, nb_msg_rcv = 0, 0, 0, 0, 0, 0

    service_table = {}
    tasks_list = ons_tasks[api.node_id]
    termination_list = api.args
    with open("/home/aomond/leverages/uptimes_schedules/0-60.json") as f:
        uptimes_schedules = json.load(f)[api.node_id]
    for upt in uptimes_schedules:
        # Sleeping period
        api.turn_off()
        node_cons.set_power(0)
        sleeping_duration = upt - api.read("clock")
        api.wait(sleeping_duration)
        sleep_time += sleeping_duration
        if all(termination_list):
            break

        # Uptime period
        api.turn_on()
        node_cons.set_power(IDLE_CONSO)
        upt_count += 1
        api.send(INTERFACE_NAME, "ping", PING_SIZE, 0)
        nb_msg_sent += 1
        upt_end = upt + UPT_DURATION
        code, data = api.receivet(INTERFACE_NAME, timeout=upt_end - api.read("clock"))
        while data is not None:
            nb_msg_rcv += 1
            if data == "ping":
                data_size = REQUEST_SIZE + SERVICE_TABLE_ENTRY_SIZE * len(service_table.keys())
                api.send(INTERFACE_NAME, service_table, data_size, 0)
                nb_msg_sent += 1
            else:
                service_table.update(data)
                if len(tasks_list) > 0 and all(dep in service_table.keys() for dep in tasks_list[0][2]):
                    task_name, task_time, _ = tasks_list[0]
                    node_cons.set_power(STRESS_CONSO)
                    api.wait(task_time)
                    node_cons.set_power(IDLE_CONSO)
                    stress_time += task_time
                    tasks_list.pop(0)
                    service_table[task_name] = [api.node_id, {}]
                    if len(tasks_list) == 0:
                        termination_list[api.node_id] = True
            code, data = api.receivet(INTERFACE_NAME, timeout=upt_end - api.read("clock"))
        upt_time += UPT_DURATION
    api.turn_off()
    node_cons.set_power(0)
    api.log(f"node_cons: {node_cons.energy}")
    api.log(f"comms_cons: {float(comms_cons.get_energy())}")
    api.log(f"upt_count: {upt_count}")
    api.log(f"sleep_time: {sleep_time}")
    api.log(f"upt_time: {upt_time}")
    api.log(f"stress_time: {stress_time}")
    api.log(f"nb_msg_sent: {nb_msg_sent}")
    api.log(f"nb_msg_rcv: {nb_msg_rcv}")
    api.log(f"time: {api.read('clock')}")

    # Save table state

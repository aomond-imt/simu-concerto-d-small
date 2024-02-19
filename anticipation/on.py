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
SERVICE_NAME_SIZE = 16
NODE_ID_SIZE = 16
EXPORTED_VALUES_SIZE = 1_000  # High value to cover worst cases
SERVICE_TABLE_ENTRY_SIZE = SERVICE_NAME_SIZE + NODE_ID_SIZE + EXPORTED_VALUES_SIZE
REQUEST_SIZE = 257


def execute(api: Node):
    # Energy states
    node_cons = PowerStates(api, 0)
    comms_cons = PowerStatesComms(api)
    comms_cons.set_power(INTERFACE_NAME, 0, COMMS_CONSO, COMMS_CONSO)

    # Metrics
    upt_count, sleep_time, upt_time, stress_time, nb_msg_sent, nb_msg_rcv = 0, 0, 0, 0, 0, 0

    service_table = {}
    tasks_list = api.args["ons_tasks"][api.node_id]
    termination_list = api.args["termination_list"]
    uptimes_schedules = api.args["uptimes_schedules"][api.node_id]
    data_to_fetch = set(d for d in tasks_list[0][2])
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
        api.send(INTERFACE_NAME, ("ping", data_to_fetch), PING_SIZE, 0)
        nb_msg_sent += 1
        upt_end = upt + UPT_DURATION
        code, data = api.receivet(INTERFACE_NAME, timeout=max(0, upt_end - api.read("clock")))
        while data is not None:
            nb_msg_rcv += 1
            t, content = data
            api.log(f"content: {str(content)}")
            if t == "ping":
                if api.args["type_comms"] == "push":
                    data_to_send = service_table
                else:
                    data_to_send = {task_name: val for task_name, val in service_table.items() if task_name in content}
                    for task_name in content:
                        if task_name not in service_table.keys():
                            data_to_fetch.add(task_name)
                api.log(f"data_to_send: {str(data_to_send)}")
                api.log(f"data_to_fetch: {str(data_to_fetch)}")
                content_size = REQUEST_SIZE + SERVICE_TABLE_ENTRY_SIZE * len(data_to_send.keys())
                api.send(INTERFACE_NAME, ("resp", data_to_send), content_size, 0)
                nb_msg_sent += 1
            else:
                service_table.update(content)
                for task_name in service_table.keys():
                    if task_name in data_to_fetch:
                        data_to_fetch.remove(task_name)
                api.log(f"service_table: {str(service_table)}")
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
                    else:
                        for task_name in tasks_list[0][2]:
                            data_to_fetch.add(task_name)
            code, data = api.receivet(INTERFACE_NAME, timeout=max(0, upt_end - api.read("clock")))
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

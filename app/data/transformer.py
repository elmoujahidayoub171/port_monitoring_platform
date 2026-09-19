from app.models.process import Process
from app.models.port import Port
from app.models.connection import Connection

# process object
def create_process_object(raw_processes):
    processes =[]
    for raw_process in raw_processes :
        process = Process(pid = raw_process["process_id"],
                          name=raw_process["name"],
                          memory_usage=raw_process["memory_usage"],
                          cpu_usage=raw_process["cpu_usage"],
                          executable=raw_process["executable"],
                          username=raw_process["username"],

        )
        processes.append(process)
    return processes

#create port object
def create_port_object(raw_ports):
    ports=[]
    for raw_port in raw_ports :
        port = Port(port_number=raw_port["port"],
                      protocol=raw_port["protocol"],
                      local_ip=raw_port["local_ip"],
                      state=raw_port["state"],
        )
        ports.append(port)
    return ports

# create connection object
def create_connection_object(raw_connections):
    connections =[]
    for raw_connection in raw_connections:
        connection = Connection(local_ip=raw_connection["local_ip"],
                                local_port=raw_connection["local_port"],
                                remote_ip=raw_connection["remote_ip"],
                                remote_port=raw_connection["remote_port"],
                                protocol=raw_connection["protocol"],
                                pid= raw_connection["pid"]
                                )
        connections.append(connection)

    return connections








import logging
import datetime
from app.data.collector import get_processes , scan_port
from app.data.cleaner import clean_process , clean_connection , clean_port
from app.data.transformer import create_process_object , create_connection_object , create_port_object
from app.repositories.process_repository import save_process 
from app.repositories.connection_repository import save_connection
from app.repositories.metric_repository import save_metrics
from app.repositories.port_repository import save_port
from app.analytics.statistics import generate_alerts




def process_connection_port_manager():
    #collector
    data1 , data2 = get_processes()
    data = scan_port()
    #cleaner
    raw_processes = clean_process(out_1=data1 , out_2=data2)
    raw_connections = clean_connection(result=data)
    raw_ports = clean_port(result=data)

    #transformer
    processes = create_process_object(raw_processes=raw_processes)
    connections = create_connection_object(raw_connections=raw_connections)
    ports = create_port_object(raw_ports=raw_ports)
    #store in postgres
    pid_to_db_id = _store_processes(processes=processes)
    _store_ports(ports=ports)
    _store_connections(connections=connections , tmps=pid_to_db_id)
    #
    alerts = generate_alerts()
    totals ={
        "listening_ports" : len([p for p in ports if p.state == 'LISTEN']),
        "active_connections" : len(connections) ,
        "active_processes" : len(processes) ,
        "open_alerts" : len(alerts) ,
        "tcp" : len([p for p in ports if p.protocol == 'tcp']) ,
        "udp" : len([p for p in ports if p.protocol == 'udp'])
    }
    _store_metrics(totals=totals)




def _store_processes(processes):
    tmps = {}
    for process in processes :
        process_id = save_process(process=process)
        tmps[process.pid] = process_id

    return tmps


def _store_connections(connections , tmps ) :
    for connection in connections :
        process_id = tmps.get(connection.pid)
        save_connection(connection=connection , process_id= process_id)

def _store_ports(ports):
    for port in ports :
        save_port(port=port)

def _store_metrics(totals):
    save_metrics(totals=totals)
    


if __name__ == "__main__" :
    process_connection_port_manager()
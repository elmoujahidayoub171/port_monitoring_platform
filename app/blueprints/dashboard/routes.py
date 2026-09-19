from flask import Blueprint, render_template

from app.analytics.statistics import *


dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    template_folder='templates'
)


def _spark_points(values, w=120, h=32, pad=2):
    if not values:
        return ""

    vmin, vmax = min(values), max(values)
    span = (vmax - vmin) or 1.0
    n = len(values)

    pts = []
    for i, v in enumerate(values):
        x = pad + i * (w - 2 * pad) / (n - 1 or 1)
        y = (h - pad) - (v - vmin) / span * (h - 2 * pad)
        pts.append(f"{x:.1f},{y:.1f}")

    return " ".join(pts)


def protocol_split():
    by_protocol = dict(port_statistics()["by_protocol"])
    tcp_n = by_protocol.get("tcp", 0)
    udp_n = by_protocol.get("udp", 0)
    return tcp_n , udp_n

def merge_processes_cpu_memory(top_cpu, top_memory):
    rows = {}
    for name, pid, cpu in top_cpu:
        row = rows.setdefault(pid, {"name": name, "pid": pid, "cpu_usage": 0.0, "memory_usage": 0.0})
        row.update(name=name, cpu_usage=cpu)
    for name, pid, mem in top_memory:
        row = rows.setdefault(pid, {"name": name, "pid": pid, "cpu_usage": 0.0, "memory_usage": 0.0})
        row.update(name=name, memory_usage=mem)
    return sorted(rows.values(), key=lambda r: r["cpu_usage"], reverse=True)


@dashboard_bp.route("/")
def index():

    listening_ports = listening_ports_statistics().get("listening_ports")
    active_processes = process_statistics().get("total")
    active_connections = connections_statistics().get("total")
    alertes  = generate_alerts()
    open_alertes = len(alertes)
    ports_spark = _spark_points(listening_ports_history(hours=24))
    processes_spark = _spark_points(active_processes_history(hours=24))
    connections_spark = _spark_points(active_connections_history(hours=24))
    alerts_spark = _spark_points(open_alerts_history(hours=24))
    tcp_n , udp_n = protocol_split()
    total = tcp_n + udp_n
    tcp_pct = round(tcp_n / total * 100) if total != 0 else 0
    udp_pct = 100 - tcp_pct

    listening_ports_description = listening_ports_statistics().get("active_ports")

    top_processes = merge_processes_cpu_memory(
        process_statistics().get("top_cpu"),
        process_statistics().get("top_memory")
    )
    pr_by_conn_count = group_connections_by_pid()

    top_remote_ips = connections_statistics().get("top_remote_ips")
    remote_ips_infos = top_remote_ips_infos()


    return render_template("dashboard/dashboard.html" , listening_ports=listening_ports ,
                           active_processes=active_processes ,
                           active_connections=active_connections,
                           open_alertes=open_alertes,
                           alertes=alertes,
                           ports_spark=ports_spark,
                           processes_spark=processes_spark,
                           connections_spark=connections_spark,
                           alerts_spark=alerts_spark , 
                           tcp_n=tcp_n ,
                           udp_n= udp_n ,
                           tcp_pct=tcp_pct,
                           udp_pct=udp_pct,
                           total=total,
                           listening_ports_description=listening_ports_description,
                           top_processes=top_processes ,
                           pr_by_conn_count=pr_by_conn_count ,
                           top_remote_ips=top_remote_ips,
                           remote_ips_infos=remote_ips_infos)
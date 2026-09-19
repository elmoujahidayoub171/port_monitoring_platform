import logging
import datetime
import psycopg2
from app.database.connection import get_connection

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Port statistics
# ------------------------------------------------------------------

def port_statistics():
    with get_connection() as conn :
        # udp tcp sockets statistics
        with conn.cursor() as cursor :
            cursor.execute(
                """
                SELECT 
                protocol , 
                COUNT(*) AS total
                from ports
                group by protocol
                order by protocol
                """
            )
            result = cursor.fetchall()
        # total ports (protocols seen)
        with conn.cursor() as cursor :
            cursor.execute(
                """
                SELECT  COUNT(protocol) as total
                from ports
                """
            )
            total_sockets = cursor.fetchone()[0]
        # sockets state
        with conn.cursor() as cursor :
            cursor.execute(
                """
                SELECT  
                protocol ,
                COUNT(*) FILTER(WHERE state = 'LISTEN') AS listening ,
                COUNT(*) FILTER(WHERE state = 'ESTAB') AS established ,
                COUNT(*) FILTER(WHERE state = 'TIME-WAIT') AS time_wait ,
                COUNT(*) FILTER(WHERE state = 'CLOSE-WAIT') AS close_wait ,
                COUNT(*) FILTER(WHERE state = 'UNCONN') AS udp_unconnected 
                from ports 
                group by protocol
                order by protocol
                """
            )
            sockets_state = cursor.fetchall()
    return {
        "by_protocol": result,
        "total": total_sockets,
        "sockets_state": sockets_state,
    }


# ------------------------------------------------------------------
# Connection statistics
# ------------------------------------------------------------------

def connections_statistics():
    with get_connection() as conn :
        # total active connections
        with conn.cursor() as cursor :
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM connections
                WHERE last_seen >= NOW() - INTERVAL '15 minutes'
                """
            )
            total_connections = cursor.fetchone()[0]
        conn.commit()
        # connections grouped by protocol
        with conn.cursor() as cursor :
            cursor.execute(
                """
                SELECT protocol , COUNT(*) AS total
                FROM connections
                WHERE last_seen >= NOW() - INTERVAL '15 minutes'
                GROUP BY protocol
                """
            )
            by_protocol = cursor.fetchall()
        conn.commit()
        # connections grouped by remote ip (top destinations)
        with conn.cursor() as cursor :
            cursor.execute(
                """
                SELECT remote_ip , COUNT(*) AS total
                FROM connections
                WHERE last_seen >= NOW() - INTERVAL '15 minutes'
                  AND remote_ip IS NOT NULL
                GROUP BY remote_ip
                ORDER BY total DESC
                LIMIT 10
                """
            )
            top_remote_ips = cursor.fetchall()
        conn.commit()
        # connections grouped by process
        with conn.cursor() as cursor :
            cursor.execute(
                """
                SELECT p.name , COUNT(c.id) AS total
                FROM connections c
                JOIN processes p ON p.id = c.process_id
                WHERE c.last_seen >= NOW() - INTERVAL '15 minutes'
                GROUP BY p.name
                ORDER BY total DESC
                LIMIT 10
                """
            )
            top_processes = cursor.fetchall()
        conn.commit()
    return {
        "total": total_connections,
        "by_protocol": by_protocol,
        "top_remote_ips": top_remote_ips,
        "top_processes": top_processes,
    }

def group_connections_by_pid():
    with get_connection() as conn :
        with conn.cursor() as cur :
            cur.execute(
                """
                SELECT pr.pid , COUNT(DISTINCT c.id)
                FROM processes   pr
                LEFT JOIN connections  c ON  c.process_id = pr.id
                GROUP BY pr.pid ;
                """
            )
            by_pid = cur.fetchall()
        conn.commit()
        return { pid : count for pid ,count in by_pid}



def top_remote_ips_infos():
    with get_connection() as conn :
        with conn.cursor() as cur :
            cur.execute(
                """
                SELECT c.remote_ip , c.remote_port , 
                    MAX(pr.name),
                    COUNT(DISTINCT c.id)
                FROM connections c 
                LEFT JOIN processes  pr ON  c.process_id = pr.id
                WHERE  c.remote_ip IS  NOT NULL
                GROUP BY c.remote_ip , c.remote_port
                ORDER BY COUNT(DISTINCT c.id) DESC;
                """
            )
            by_remote_ip = cur.fetchall()
        conn.commit()
        return {remote_ip : [remote_ip , remote_port , process , count]
                for remote_ip , remote_port , process , count in by_remote_ip}



# ------------------------------------------------------------------
# Process statistics
# ------------------------------------------------------------------

def process_statistics():
    with get_connection() as conn :
        # total tracked processes
        with conn.cursor() as cursor :
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM processes
                WHERE last_seen >= NOW() - INTERVAL '15 minutes'
                """
            )
            total_processes = cursor.fetchone()[0]
        conn.commit()
        # top processes by cpu usage
        with conn.cursor() as cursor :
            cursor.execute(
                """
                SELECT name , pid , cpu_usage
                FROM processes
                ORDER BY cpu_usage DESC
                LIMIT 10
                """
            )
            top_cpu = cursor.fetchall()
        conn.commit()
        # top processes by memory usage
        with conn.cursor() as cursor :
            cursor.execute(
                """
                SELECT name , pid , memory_usage
                FROM processes
                ORDER BY memory_usage DESC
                LIMIT 10
                """
            )
            top_memory = cursor.fetchall()
        conn.commit()
    return {
        "total": total_processes,
        "top_cpu": top_cpu,
        "top_memory": top_memory,
    }




# ------------------------------------------------------------------
# Listening port statistics (for the dashboard)
# ------------------------------------------------------------------

def listening_ports_statistics():
    with get_connection() as conn :
        # count of listening ports
        with conn.cursor() as cursor :
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM ports
                WHERE state = 'LISTEN'
                """
            )
            listening_ports = cursor.fetchone()[0]
        conn.commit()
        # distribution by port number
        with conn.cursor() as cursor :
            cursor.execute(
                """
                SELECT
                    port_number , 
                    COUNT(*) AS total
                FROM ports
                WHERE state = 'LISTEN'
                GROUP BY port_number
                ORDER BY total DESC
                LIMIT 10
                """
            )
            port_distribution = cursor.fetchall()
        conn.commit()
        # active listening ports with owning process
        with conn.cursor() as cursor :
            cursor.execute(
                """
                SELECT
                    p.port_number ,
                    p.protocol ,
                    pr.name AS process_name ,
                    pr.pid , 
                    p.state , 
                    p.first_seen
                FROM ports p
                LEFT JOIN connections c
                       ON c.local_port = p.port_number
                      AND c.protocol = p.protocol
                      AND c.local_ip = p.local_ip
                LEFT JOIN processes pr
                       ON pr.id = c.process_id
                WHERE p.state = 'LISTEN'
                ORDER BY p.port_number
                LIMIT 50
                """
            )
            active_ports = cursor.fetchall()
        conn.commit()
    return {
        "listening_ports": listening_ports,
        "port_distribution": port_distribution,
        "active_ports": active_ports,
    }


# ------------------------------------------------------------------
# Alerting / anomaly detection
# ------------------------------------------------------------------

def recent_activities(minutes: int = 30, limit: int = 50):
    """Newly first-seen ports, processes and connections in the last `minutes`."""
    window = datetime.timedelta(minutes=minutes)
    since = datetime.datetime.now() - window
    with get_connection() as conn :
        # newly seen ports
        with conn.cursor() as cursor :
            cursor.execute(
                """
                SELECT port_number , protocol , local_ip , state , first_seen
                FROM ports
                WHERE first_seen >= %s
                ORDER BY first_seen DESC
                LIMIT %s
                """,
                (since, limit),
            )
            new_ports = cursor.fetchall()
        conn.commit()
        # newly seen processes
        with conn.cursor() as cursor :
            cursor.execute(
                """
                SELECT pid , name , cpu_usage , memory_usage , first_seen
                FROM processes
                WHERE first_seen >= %s
                ORDER BY first_seen DESC
                LIMIT %s
                """,
                (since, limit),
            )
            new_processes = cursor.fetchall()
        conn.commit()
        # newly seen connections
        with conn.cursor() as cursor :
            cursor.execute(
                """
                SELECT local_ip , local_port , remote_ip , remote_port ,
                       protocol , pid , first_seen
                FROM connections
                WHERE first_seen >= %s
                ORDER BY first_seen DESC
                LIMIT %s
                """,
                (since, limit),
            )
            new_connections = cursor.fetchall()
        conn.commit()
    return {
        "new_ports": new_ports,
        "new_processes": new_processes,
        "new_connections": new_connections,
    }


def connection_spike_detected(threshold: int = 100, window_minutes: int = 5):
    """Whether the number of active connections exceeds the given threshold."""
    with get_connection() as conn :
        with conn.cursor() as cursor :
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM connections
                WHERE last_seen >= NOW() - (INTERVAL '1 minute' * %s)
                """,
                (window_minutes,),
            )
            count = cursor.fetchone()[0]
        conn.commit()
    return count > threshold


def unexpected_listening_ports(baseline_window_hours: int = 24, limit: int = 20):
    """Listening ports that were not seen during the baseline window."""
    baseline_since = datetime.datetime.now() - datetime.timedelta(hours=baseline_window_hours)
    cutoff = baseline_since + datetime.timedelta(minutes=1)
    with get_connection() as conn :
        with conn.cursor() as cursor :
            cursor.execute(
                """
                SELECT port_number , protocol , local_ip , first_seen
                FROM ports
                WHERE state = 'LISTEN'
                  AND first_seen >= %s
                EXCEPT
                SELECT port_number , protocol , local_ip , first_seen
                FROM ports
                WHERE state = 'LISTEN'
                  AND first_seen < %s
                ORDER BY first_seen DESC
                LIMIT %s
                """,
                (cutoff, cutoff, limit),
            )
            unexpected = cursor.fetchall()
        conn.commit()
    return unexpected


def generate_alerts(window_minutes: int = 30, spike_threshold: int = 100):
    """High-level alert aggregation for the dashboard."""
    alerts = []
    # newly seen entities in the window
    activity = recent_activities(minutes=window_minutes)
    for port in activity["new_ports"]:
        alerts.append({
            "severity": "warning",
            "title": "New listening port detected",
            "description": f"Port {port[0]}/{port[1]} on {port[2]} entered state '{port[3]}'.",
            "created_at": str(port[4]),
        })
    for process in activity["new_processes"][:10]:
        alerts.append({
            "severity": "info",
            "title": "New network process detected",
            "description": f"PID {process[0]} ({process[1]}) started network activity.",
            "created_at": str(process[4]),
        })
    # connection spike
    if connection_spike_detected(threshold=spike_threshold, window_minutes=window_minutes):
        alerts.append({
            "severity": "warning",
            "title": "Connection spike detected",
            "description": f"Unusual network activity detected (> {spike_threshold} active connections).",
            "created_at": str(datetime.datetime.now()),
        })
    # unexpected listening ports
    for port in unexpected_listening_ports():
        alerts.append({
            "severity": "critical",
            "title": "Unexpected listening port",
            "description": f"Port {port[0]} was opened by an unknown process.",
            "created_at": str(port[3]),
        })
    return alerts

#bucket the snapshots, feed the SVG curve

def _metric_history(column, hours=24):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT date_trunc('hour', ts) AS bucket,
                       MAX({column})
                FROM metrics
                WHERE ts >= NOW() - INTERVAL '1 hour' * %s
                GROUP BY 1 ORDER BY 1
            """, (hours,))
            rows = cur.fetchall()
    return [r[1] for r in rows]


def listening_ports_history(hours=24):
    return _metric_history("listening_ports", hours=hours)


def active_processes_history(hours=24):
    return _metric_history("active_processes", hours=hours)


def active_connections_history(hours=24):
    return _metric_history("active_connections", hours=hours)


def open_alerts_history(hours=24):
    return _metric_history("open_alerts", hours=hours)          

# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------

if __name__ == "__main__" :
    results = {
        "PORT STATISTICS": port_statistics(),
        "CONNECTION STATISTICS": connections_statistics(),
        "PROCESS STATISTICS": process_statistics(),
        "LISTENING PORTS STATISTICS": listening_ports_statistics(),
        "RECENT ACTIVITIES": recent_activities(),
        "GENERATED ALERTS": generate_alerts(),
    }

    for label , result in results.items() :
        print(label)
        print("=" * 100)
        print(result)
        print()


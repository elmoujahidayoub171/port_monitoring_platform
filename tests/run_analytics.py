from app.analytics.statistics import (port_statistics , connections_statistics , process_statistics,
                                      listening_ports_statistics ,recent_activities ,
                                       generate_alerts )



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
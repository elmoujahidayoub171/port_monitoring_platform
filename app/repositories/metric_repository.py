from app.database.connection import get_connection

def save_metrics(totals):
    with get_connection() as conn :
        with conn.cursor() as cursor :
            cursor.execute(
                """
            INSERT INTO metrics(
            listening_ports ,
            active_connections  ,
            active_processes ,
            open_alerts
            )
            VALUES
            (%s , %s , %s , %s  )

            """,
            (totals["listening_ports"],
             totals["active_connections"] ,
             totals["active_processes"],
             totals["open_alerts"] )

            )
        conn.commit()
    return True
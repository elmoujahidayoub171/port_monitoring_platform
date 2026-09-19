from app.database.connection import get_connection

def save_port(port):
    with get_connection() as conn :
        with conn.cursor() as cursor :
            cursor.execute(
                """
            INSERT INTO PORTS(
            port_number ,
            protocol ,
            local_ip ,
            state ,
            last_seen
            )
            VALUES
            (%s , %s , %s , %s  , NOW())
            ON CONFLICT (port_number , protocol  , local_ip)
            DO UPDATE SET 
                state = EXCLUDED.state ,
                last_seen = NOW()
            """,
            (port.port_number,
             port.protocol ,
             port.local_ip ,
             port.state )

            )
        conn.commit()
    return True
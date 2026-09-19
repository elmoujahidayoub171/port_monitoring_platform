from app.database.connection import get_connection
import psycopg2

def save_connection(connection, process_id):
    with get_connection() as conn :
        with conn.cursor() as cursor :
            try:
                cursor.execute(
                    """
                    INSERT INTO connections
                    (local_ip ,
                    local_port,
                    remote_port,
                    remote_ip,
                    protocol,
                    pid,
                    process_id,
                    last_seen
                    )
                    VALUES
                    (%s , %s , %s , %s , %s , %s , %s , NOW() )
                    ON CONFLICT (local_ip , local_port , remote_ip , remote_port ,
                                    protocol , process_id)
                    DO UPDATE SET 
                        last_seen = NOW()
                    """,
                    (connection.local_ip,
                    connection.local_port ,
                    connection.remote_port ,
                    connection.remote_ip ,
                    connection.protocol ,
                    connection.pid,
                    process_id)

                )
                conn.commit()


            except psycopg2.errors.ForeignKeyViolation as e :
                conn.rollback()
                print(f"DATABASE ERROR : {e}\n"
                      "connection was not inserted")
            
    
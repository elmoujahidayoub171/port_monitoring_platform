import psycopg2
from app.database.connection import get_connection

def save_process(process):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
            INSERT INTO PROCESSES(
            pid,
            name,
            cpu_usage,
            memory_usage,
            executable,
            username,
            last_seen
            )
            VALUES
            (%s , %s , %s , %s , %s , %s  , NOW())
            ON CONFLICT (pid , name , executable )
            DO UPDATE SET 
                cpu_usage = EXCLUDED.cpu_usage,
                memory_usage = EXCLUDED.memory_usage,
                username = EXCLUDED.username,
                last_seen = NOW()
            RETURNING id
                """,
            (process.pid ,
             process.name ,
             process.cpu_usage ,
             process.memory_usage ,
             process.executable ,
             process.username 
            )
            )
            process_id = cursor.fetchone()[0]
        connection.commit()
    return  process_id

CREATE TABLE IF NOT EXISTS metrics(
    id SERIAL PRIMARY KEY ,
    ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ,
    listening_ports INT NOT NULL ,
    active_connections INT NOT NULL ,
    active_processes  INT NOT NULL ,
    open_alerts  INT NOT NULL

);
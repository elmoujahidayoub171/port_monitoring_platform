CREATE TABLE CONNECTIONS(
    id SERIAL PRIMARY KEY ,
    local_ip INET NOT NULL ,
    local_port INT NOT NULL ,
    remote_port INT ,
    remote_ip INET ,
    protocol VARCHAR(10) ,
    pid INT NOT NULL  ,
    process_id INT NOT NULL ,
    first_seen TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ,
    last_seen TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ,
    UNIQUE NULLS NOT DISTINCT (local_ip , local_port , remote_port , remote_ip , 
            protocol , process_id),
    CONSTRAINT fk_connection_port
        FOREIGN KEY (local_port , protocol , local_ip) 
        REFERENCES ports(port_number , protocol , local_ip) ,
    CONSTRAINT fk_connection_process
        FOREIGN KEY (process_id) 
        REFERENCES processes(id)

);

CREATE INDEX   idx_connections_last_seen ON CONNECTIONS(last_seen) ;
CREATE INDEX idx_connections_protocol ON CONNECTIONS(protocol);

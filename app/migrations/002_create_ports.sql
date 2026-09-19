create table ports(
    id  SERIAL  PRIMARY KEY ,
    port_number INTEGER NOT NULL ,
    protocol  VARCHAR(10) NOT NULL ,
    local_ip INET NOT NULL ,
    state VARCHAR(10) ,
    first_seen TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ,
    last_seen TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ,
    UNIQUE (port_number , protocol , local_ip)
);

CREATE INDEX   idx_ports_protocol ON ports(protocol) ;
CREATE INDEX   idx_ports_state ON ports(state) ;
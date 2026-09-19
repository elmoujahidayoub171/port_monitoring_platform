create table processes(
    id SERIAL PRIMARY KEY ,
    pid INTEGER NOT NULL ,
    name VARCHAR(255)  NOT NULL ,
    cpu_usage DOUBLE PRECISION ,
    memory_usage DOUBLE PRECISION  ,
    executable TEXT ,
    username VARCHAR(255) ,
    first_seen TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ,
    last_seen TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ,
    UNIQUE(pid , name , executable )

);
CREATE INDEX idx_processes_last_seen  ON processes(last_Seen) ;

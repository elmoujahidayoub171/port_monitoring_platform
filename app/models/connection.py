from dataclasses import dataclass
from datetime import datetime

@dataclass
class Connection:
    local_ip : str
    local_port : int
    remote_ip : str
    remote_port : int
    protocol : str
    pid : int 
    first_seen : datetime  | None = None
    last_seen : datetime | None = None
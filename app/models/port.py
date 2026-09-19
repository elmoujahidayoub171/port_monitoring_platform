from dataclasses import dataclass
from datetime import datetime

@dataclass
class Port:
    port_number : int
    protocol : str
    local_ip : str
    state : str

    first_seen : datetime | None = None
    last_seen : datetime | None = None

    

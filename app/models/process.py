from dataclasses import dataclass
from datetime import datetime

@dataclass
class Process:
    pid : int 
    name  : str 
    memory_usage : float
    cpu_usage : float
    executable : str | None = None
    username : str | None = None

    first_seen : datetime | None = None
    last_seen : datetime | None = None
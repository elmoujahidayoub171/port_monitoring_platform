import re
from app.data.collector import scan_port
import ipaddress
import logging




logger = logging.getLogger(__name__)

# function to normalize the ip address && -> str : means the return type hint
def normalize_ip(ip : str , ip_version : int | None = None) -> str:
    ip = ip.strip()

    #remove the [ ]
    if ip.startswith("[") and ip.endswith("]") :
        ip =  ip[1:-1]

    # remove zone / interface identifier
    if "%" in ip :
        ip = ip.split("%" , 1)[0]

    # handle all addresses "*"
    if ip == "*" :
        if ip_version == 6 :
            return "::"
        return "0.0.0.0"

    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        logger.error("Invalid IP address: %s", ip)
        return None
    ## ipv4_mapped : convert ipv6 adress to ipv4 address
    if addr.version == 6 and addr.ipv4_mapped:
        return str(addr.ipv4_mapped)

    return str(addr)



def clean_process(out_1 , out_2):
    # structure to save the out_1
        lines = out_1.splitlines()
        #
        l1 =[]
        for line in lines[1:]:
            out = line.split()
            if len(out) <  9 :
                continue
            try :
                Process_inofs = {"name" : str(out[0]) ,
                                "pid" : int(out [1]) ,
                                "username" : str(out[2]) ,
                                "port" : int(out[8].split(":")[-1])
                }
                l1.append(Process_inofs)
            except (ValueError , IndexError) :
                logger.error("Skipping malformed line {} .".format(line))

        #structure to save out_2
        lines = out_2.splitlines()
        #
        l2 = []
        for line in lines[1:] :
            out = line.split()
            if len(out) < 11 :
                continue
            try :
                addit_process_infos = {"process_id" :int(out[1] ),
                                    "cpu_usage" : float(out[2]) ,
                                    "memory_usage" : float(out[3]),
                                    "executable" : str(out[10])
                                    }
                l2.append(addit_process_infos)
            except (ValueError , IndexError) :
                logger.error("Skipping malformed line {} .".format(line))             

        # join the two structure l1 , l2
        processes_by_ids = {ps["process_id"] : ps for ps in l2}
        Processes = [{**processes_by_ids[ps["pid"]],**ps}
                    for ps in l1
                    if ps["pid"] in processes_by_ids]
        return Processes


def clean_port(result):
    Ports = []
    lines = result.splitlines()
    for line in lines[1:]:
        out = line.split()
        if len(out) < 7:
            continue
        try:
            local_ip = normalize_ip(out[4].rsplit(":", 1)[0].split("%", 1)[0])
            if local_ip is None:
                continue
            port = int(out[4].rsplit(":", 1)[-1])
            Ports.append({
                "protocol": str(out[0]),
                "local_ip": local_ip,
                "state": str(out[1]),
                "port": port,
            })
        except (ValueError, IndexError):
            logger.error("Skipping malformed line: %s", line)
    return Ports

def clean_connection(result):
    Connections =[]
    lines = result.splitlines()
    for line in lines[1:]:
        out = line.split()
        if len(out) < 7 :
            continue
        try :
            # handle the process column
            pattern = r'\("([^"]+)",pid=(\d+),fd=(\d+)\)'
            matches = re.findall(pattern=pattern, string=out[6])
            # handle the remote port
            remote_port = out[5].rsplit(":",1)[1]
            for match in matches:
                connection = {"local_ip" : normalize_ip(out[4].rsplit(":",1)[0].split("%" , 1)[0])  ,
                                "local_port" : int(out[4].rsplit(":",1)[1]) ,
                                #handle the remote ip
                                "remote_ip" : normalize_ip(out[5].rsplit(":",1)[0].split("%", 1)[0]) ,
                                "protocol" :str(out[0].strip()) ,
                                "remote_port" : None if remote_port == "*" else int(remote_port) ,
                                "pid" : int(match[1])
                                
                                }
                Connections.append(connection)
        except (ValueError , IndexError) :
            logger.error("Skipping malformed line {} .".format(line))

    return Connections



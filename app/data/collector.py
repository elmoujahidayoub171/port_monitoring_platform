import subprocess
import logging

logger = logging.getLogger(__name__)

def _run_commad(command , timeout=10):

    try:
        result = subprocess.run(command ,
                                capture_output=True ,
                            text=True , 
                            timeout=timeout)
        return result

    except subprocess.TimeoutExpired :
        logger.error("{} timed out after {%.2f} s .".format(command , timeout))

    except Exception as e :
        logger.error("{} raised an exception {} .".format(command , e))



# process
def get_processes():

    # get the prot owned by process
    out_1 = _run_commad(["sudo" , "-n" , "/usr/bin/lsof" , "-i" , "-n" , "-P"])

     # get disk & memory usage by each process
    out_2 = _run_commad(["sudo" , "-n" , "ps" , "axu"])

    return out_1.stdout , out_2.stdout
    

# scan ports & connections
def scan_port():

    # understand ports 
    ## run the socket statistics
    result = _run_commad(["sudo" , "-n" , "/usr/bin/ss","-tunap"])

    return result.stdout
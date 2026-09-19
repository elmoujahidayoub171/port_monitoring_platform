from app.services import  process_connection_port_manager
import time



def run_pipline():

    process_connection_port_manager.process_connection_port_manager()
    print("Pipline Completed Successfully")


if __name__ == "__main__" :
    run_pipline()

""" 
    simple script to send the local ip into the .env file, to use simulation if the ip is not correctly found 
"""

import os
import socket
import logging
from dotenv import load_dotenv, set_key

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("set_simulation_ip")

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

if __name__ == "__main__":
    load_dotenv()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dotenv_path = os.path.join(dir_path, '.env')
    logger.info(f"path of the .env file:{dotenv_path}")

    key_to_update = "ROBOT_IP"
    new_value = f"{get_local_ip()}"

    set_key(dotenv_path, key_to_update, new_value)

    # Verify the update (optional)
    load_dotenv() 
    logger.info(f"loaded ip for simulation:{os.getenv(key_to_update)}")
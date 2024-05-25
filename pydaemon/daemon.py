import time
import logging

logging.basicConfig(filename='/var/log/mydaemon.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

def handle_request(request):
    if request == "status":
        return "Daemon is running."
    elif request == "time":
        return f"The current time is {time.strftime('%H:%M:%S')}."
    else:
        return "Unknown command."

def daemon_main():
    while True:
        request = "time"
        response = handle_request(request)
        logging.info(f"Response: {response}")
        time.sleep(10) 

if __name__ == "__main__":
    daemon_main()

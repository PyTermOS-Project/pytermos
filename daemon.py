import time
import logging

# Set up logging
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
        # Example of how you might handle requests
        request = "time"  # This could be replaced by a mechanism that reads requests from a file or network
        response = handle_request(request)
        logging.info(f"Response: {response}")
        time.sleep(10)  # Delay for demonstration purposes

if __name__ == "__main__":
    daemon_main()

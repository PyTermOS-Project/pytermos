import time

def handle_request(request):
    # Process the request and generate a response
    if request == "status":
        return "Daemon is running."
    elif request == "time":
        return f"The current time is {time.strftime('%H:%M:%S')}."
    else:
        return "Unknown command."

def daemon_main():
    while True:
        request = input("Enter a command: ").strip().lower()

        response = handle_request(request)
        
        print("Response:", response)

if __name__ == "__main__":
    daemon_main()

import subprocess
import sys

def send_request(request):
    python_executable = sys.executable
    process = subprocess.Popen([python_executable, "daemon.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    stdout, _ = process.communicate(input=request)
    return stdout.strip()

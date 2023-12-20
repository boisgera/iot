# Python Standard Library
import subprocess
import sys

NUM_PROCESSES = 2

# ------------------------------------------------------------------------------

processes = []
for i in range(NUM_PROCESSES):
    processes.append(subprocess.Popen([sys.executable, "pi-contributor.py"]))

processes[0].wait()

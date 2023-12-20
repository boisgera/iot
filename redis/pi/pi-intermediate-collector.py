# Python Standard Library
import atexit
import os
import platform
import signal
import subprocess
import sys
import threading

# Third-Party Libraries
import numpy as np
import numpy.random as npr
import redis

# Constants
SELF = f"{platform.node()}-{os.getpid()}"
FOREVER = threading.TIMEOUT_MAX
REDIS_CONFIG = {}
N = 80_000_000 # 640 Mo data
Nsub = 10_000_000 # 80 Mo data
NUM_PROCESSES = 8

# ------------------------------------------------------------------------------
r = redis.Redis(**REDIS_CONFIG)
p = r.pubsub()

p.subscribe(SELF)
m = p.get_message(timeout=FOREVER)
assert isinstance(m, dict) and m.get("type") == "subscribe"

partial_results = []
children = []

for i in range(NUM_PROCESSES):
    child = subprocess.Popen([sys.executable, "pi-micro-contributor.py", SELF])
    children.append(child)

def kill_children():
    for child in children:
        child.kill(signal.SIGKILL)

atexit.register(kill_children)
    

while True:
    m = p.get_message(timeout=FOREVER)
    partial_results.append(float(m["data"]))
    if len(partial_results) == 8:
        approx_pi = np.mean(partial_results)
        r.publish("PI", repr(approx_pi).encode("utf-8"))
        partial_results = []


# Python Standard Library
import json
import os
import platform
import threading

# Third-Party Libraries
import numpy as np
import numpy.random as npr
import redis

# Constants
SELF = f"PI"
FOREVER = threading.TIMEOUT_MAX
REDIS_CONFIG = {}
N = 80_000_000 # 640 Mo data

# ------------------------------------------------------------------------------
r = redis.Redis(**REDIS_CONFIG)
p = r.pubsub()

p.subscribe(SELF)
m = p.get_message(timeout=FOREVER)
assert isinstance(m, dict) and m.get("type") == "subscribe"

partial_results = []

def step():
    x = npr.random(N)
    y = npr.random(N)
    t =  x * x + y * y <= 1.0
    return 4 * t.mean()

while True:
    m = p.get_message(timeout=FOREVER)
    partial_results.append(float(m["data"]))
    p_ = 3.15 / 4
    q = (1 - 3.14/4)
    n = N * len(partial_results)
    sigma = 4 * np.sqrt(p_ * q / n)
    pi_approx = np.mean(partial_results)
    print(f"{pi_approx:.17f} {abs(pi_approx - np.pi):.2g} {3.0*sigma:.2g}")
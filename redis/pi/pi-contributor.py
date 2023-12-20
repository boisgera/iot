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
FOREVER = threading.TIMEOUT_MAX
REDIS_CONFIG = {}
N = 80_000_000 # 640 Mo data

# ------------------------------------------------------------------------------
r = redis.Redis(**REDIS_CONFIG)
p = r.pubsub()

def step():
    x = npr.random(N)
    y = npr.random(N)
    t =  x * x + y * y <= 1.0
    return 4 * t.mean()

while True:
    r.publish("PI", repr(step()).encode("utf-8"))

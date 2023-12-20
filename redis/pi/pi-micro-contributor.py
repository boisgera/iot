# Python Standard Library
import threading
import sys

# Third-Party Libraries
import numpy as np
import numpy.random as npr
import redis

# Constants
FOREVER = threading.TIMEOUT_MAX
REDIS_CONFIG = {}
N = 10_000_000 # 80 Mo data

# ------------------------------------------------------------------------------
r = redis.Redis(**REDIS_CONFIG)
p = r.pubsub()

SINK = sys.argv[1]

def step():
    x = npr.random(N)
    y = npr.random(N)
    t =  x * x + y * y <= 1.0
    return 4 * t.mean()

while True:
    r.publish(SINK, repr(step()).encode("utf-8"))

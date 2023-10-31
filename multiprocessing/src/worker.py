
# Python Standard Library
import os
import math
import pathlib
import pickle
import sys
import threading

# Third Party Libraries
import redis


# About this process
# ------------------------------------------------------------------------------
pid = os.getpid()
if __name__ == "__main__":
    name = pathlib.Path(__file__).stem
else:
    name = __name__
self = f"{name}.{pid}"


# Utility constants & functions
# ------------------------------------------------------------------------------
def log(*args, **kwargs):
    print(self + " >", *args, **kwargs)

TIMEOUT_MAX = threading.TIMEOUT_MAX


# Redis & mailbox init 
# ------------------------------------------------------------------------------
r = redis.Redis()
p = r.pubsub()
p.subscribe(self)
message = p.get_message(timeout=TIMEOUT_MAX)
log(message)

# Start a worker & exchange connexion information
# ------------------------------------------------------------------------------
log(f"{sys.argv = }")
client = sys.argv[1]
r.publish(client, self) # need to be more specific here; use "from" field
# with "ack" content?
# Need to wait for some "ACK" message here.
message = p.get_message(timeout=TIMEOUT_MAX)
log(message)

# Wait for the payload, execute it, send the result back
# ------------------------------------------------------------------------------
payload = p.get_message(timeout=TIMEOUT_MAX)
log(f"{payload = }")
if payload is not None:
    (fct, args, kwargs) = pickle.loads(payload["data"])
    out = fct(*args, **kwargs)
    r.publish(client, pickle.dumps(out))
    log("Done.")
else:
    log("No payload received.")
    sys.exit("No payload received.")


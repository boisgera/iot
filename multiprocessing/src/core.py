# Python Standard Library
import os
import pathlib
import cloudpickle as pickle
import subprocess
import threading
import uuid
import sys

# Third Party Libraries
import redis

# About this process
# ------------------------------------------------------------------------------


# Utility constants & functions
# ------------------------------------------------------------------------------
TIMEOUT_MAX = threading.TIMEOUT_MAX


# Mailbox
# ------------------------------------------------------------------------------
class Channel:
    def __init__(self, mailbox, filter):
        self._mailbox = mailbox
        self._filter = filter
    def __iter__(self):
        return self
    def __next__(self):
        self._mailbox.get_messages(block=False)
        for i, message in enumerate(self._mailbox._messages):
            if self._filter(message):
                return self._mailbox._messages.pop(i)
        else:
            while True:
                self._mailbox.get_messages(block=True)
                new_message = self._mailbox._messages[-1]
                if self._filter(new_message):
                    return self._mailbox._messages.pop(-1)
    def __repr__(self):
        self._mailbox.get_messages(block=False)
        return repr([m for m in self._mailbox._messages if self._filter(m)])


class Mailbox:
    def __init__(self, r):
        self._r = r
        self._pubsub = r.pubsub()
        self._messages = [] 
        self._inbox = Channel(self, lambda message: True)
        pid = os.getpid()
        if __name__ == "__main__":
            name = pathlib.Path(__file__).stem
        else:
            name = __name__
        self.id = f"{name}.{pid}"
        self._pubsub.subscribe(self.id)
        _ = next(self[self._subscribe_ack])
    def _subscribe_ack(self, message):
        return (
            message["type"] == "subscribe" and 
            message["channel"] == self.id.encode("ascii")
            ) 
    def __getitem__(self, filter):
        return Channel(self, filter)
    def __iter__(self):
        return iter(self._inbox)
    def __next__(self):
        return next(self._inbox)
    def __repr__(self):
        return repr(self._inbox)
    def get_messages(self, block=False):
        while message := self._pubsub.get_message(timeout=0.0):
            self._messages.append(message)
        if block:
            message = self._pubsub.get_message(timeout=TIMEOUT_MAX)
            assert message is not None, "Timeout"
            self._messages.append(message)
    def send(self, *args, **kwargs):
        self._r.publish(*args, **kwargs)


# Redis init
# ------------------------------------------------------------------------------
r = redis.Redis()
mailbox = Mailbox(r) # Question: do we want the mailbox to be sendable?
                     # Or instead, explicitly non-sendable and unique to
                     # each process? (probably the latter, which is what
                     # is achieved here AFAICT)

class Promise:
    def __init__(self, id):
        self._id = id
    def from_subprocess(self, message):
        return message["data"].startswith(self._id)
    def __call__(self):
        message = next(mailbox[self.from_subprocess])
        n = len(self._id)
        return pickle.loads(message["data"][n:]) 

def asyncify(function):
    def wrapped_function(*args, **kwargs):
        worker = subprocess.Popen(
            [sys.executable, "worker.py", mailbox.id],  
            stdout=subprocess.PIPE
        )
        worker_id = next(worker.stdout).strip()
        message = (function, args, kwargs)
        mailbox.send(worker_id, pickle.dumps(message))
        return Promise(worker_id)
    return wrapped_function



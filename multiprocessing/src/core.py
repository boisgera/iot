# Python Standard Library
import math
import os
import pathlib
import pickle
import subprocess
import threading
import sys
import uuid

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
mailbox = Mailbox(r)

class Promise:
    def __init__(self, channel):
        self._channel = channel
    def __call__(self):
        # ISSUE! # need to be channel-specific!
        message = mailbox.get(lambda message: message["channel"] == self._channel)
        log(message)
        result = pickle.loads(message["data"])
        return result

def asyncify(function):
    def wrapped_function(self, *args, **kwargs):
        answer_channel = uuid.uuid4().hex
        r.pubsub().subscribe(answer_channel)
        
        # TODO: deal with subscription ACK
        ack_sub = mailbox.get(lambda message: message["channel"] == answer_channel)
        print(ack_sub)

        subprocess.Popen([sys.executable, "worker.py", pid])
        message = p.get_message(timeout=TIMEOUT_MAX) # get the worker handle
        worker = message["data"]
        # Send the payload to the worker
        payload = pickle.dumps((function, args, kwargs))
        r.publish(worker, payload)
        return Promise(answer_channel)
    return wrapped_function



# Python Standard Library
import json
import os
import platform
import threading

# Third-Party Libraries
import redis

# Constants
SELF = f"{platform.node()}-{os.getpid()}"
FOREVER = threading.TIMEOUT_MAX
REDIS_CONFIG = {}

# ------------------------------------------------------------------------------
r = redis.Redis(**REDIS_CONFIG)
p = r.pubsub()

p.subscribe(SELF)
m = p.get_message(timeout=FOREVER)
assert isinstance(m, dict) and m.get("type") == "subscribe"

inbox = []

# 📝 TODO: timeout against denial of service
def fetch():
    while True:
        m = p.get_message()
        if m is None:
            break
        message = json.loads(m["data"].decode("utf-8"))
        inbox.append(message)

def display(message):
    print(f"From: {message['from']}")
    print(f"To: {', '.join(message["to"])}")
    print(f"Cc: {', '.join(message["cc"])}")
    print(f"Subject: {message['subject']}")
    print()
    print(message["body"])

def send(to, cc=None, subject="", body=""):
    if isinstance(to, str):
        to = [to]
    if isinstance(cc, str):
        cc = [cc]
    if cc == None:
        cc = []
    message = {"from": SELF, "to": to, "cc": cc, "subject": subject, "body": body}
    binary = json.dumps(message).encode("utf-8")
    for target in to + cc:
        r.publish(target, binary)

def reply(message, body=""):
    to = message["from"]
    subject = f'Re: {message["subject"]}'
    preamble = "\n".join([f">{line}" for line in message["body"].splitlines()])
    body = preamble + "\n" + body
    send(to, cc=[], subject=subject, body=body)

def reply_all(message, body=""):
    to = [message["from"]] + list(set(message["to"]) - {SELF})
    cc = message["cc"]
    subject = f'Re: {message["subject"]}'
    preamble = "\n".join([f">{line}" for line in message["body"].splitlines()])
    body = preamble + "\n" + body
    send(to, cc, subject=subject, body=body)
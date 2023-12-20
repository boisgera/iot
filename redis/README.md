Redis
================================================================================

<https://redis.io/>

> The open source, in-memory data store used by millions of developers 
> as a database, cache, streaming engine, and message broker. 

## Quickstart

```bash session
$ conda create --name redis
...
$ conda activate redis
$ conda install redis-server  # Install Redis server and CLI
...
```


```
$ redis-server
...
                _._                                                  
           _.-``__ ''-._                                             
      _.-``    `.  `_.  ''-._           Redis 5.0.3 (00000000/0) 64 bit
  .-`` .-```.  ```\/    _.,_ ''-._                                   
 (    '      ,       .-`  | `,    )     Running in standalone mode
 |`-._`-...-` __...-.``-._|'` _.-'|     Port: 6379
 |    `-._   `._    /     _.-'    |     PID: 60817
  `-._    `-._  `-./  _.-'    _.-'                                   
 |`-._`-._    `-.__.-'    _.-'_.-'|                                  
 |    `-._`-._        _.-'_.-'    |           http://redis.io        
  `-._    `-._`-.__.-'_.-'    _.-'                                   
 |`-._`-._    `-.__.-'    _.-'_.-'|                                  
 |    `-._`-._        _.-'_.-'    |                                  
  `-._    `-._`-.__.-'_.-'    _.-'                                   
      `-._    `-.__.-'    _.-'                                       
          `-._        _.-'                                           
              `-.__.-'                                               

60817:M 31 Jul 2023 15:33:14.699 # Server initialized
60817:M 31 Jul 2023 15:33:14.700 * DB loaded from disk: 0.000 seconds
60817:M 31 Jul 2023 15:33:14.700 * Ready to accept connections
```

```bash session
$ ps aux | grep redis-server
boisgera   60817  0.1  0.0  46388  5204 pts/0    Sl+  15:33   0:00 redis-server *:6379
```

```bash session
$ redis-cli PING
PONG
```

```bash session
$ redis-cli SET message "Hello world!" 
OK
```

```bash session
$ redis-cli GET message
"Hello world!"
```

## Public redis server

### Bind to IP address

Bind Redis server to your public network address instead of localhost.

```bash session
$ ifconfig -a
wlp111s0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.1.44  netmask 255.255.255.0  broadcast 192.168.1.255
        inet6 fe80::d768:d027:9d50:c820  prefixlen 64  scopeid 0x20<link>
        inet6 2a02:842a:220:6301:5e35:150c:4b5f:f961  prefixlen 64  scopeid 0x0<global>
        inet6 2a02:842a:220:6301:de1:9b24:1557:f48c  prefixlen 64  scopeid 0x0<global>
        ether 18:56:80:7c:2e:a5  txqueuelen 1000  (Ethernet)
        RX packets 566267  bytes 750652878 (750.6 MB)
        RX errors 0  dropped 57  overruns 0  frame 0
        TX packets 161147  bytes 31206122 (31.2 MB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

...
```

```bash session
$ touch redis.conf
$ echo "bind 192.168.1.44" >> redis.conf
$ echo "protected-mode no" >> redis.conf
```

```bash session
$ redis-server redis.conf
...
```

```bash session
$ redis-cli -h 192.168.1.44 PING
PONG
```

### Ngrok

Bind to localhost but tunnel localhost to a public address.

```bash session
$ redis-server 
...
```

```bash session
$ ngrok tcp 6439
...                                    
Forwarding tcp://5.tcp.eu.ngrok.io:12498 -> localhost:6379 
...
```

```bash session
$ redis-cli -h 5.tcp.eu.ngrok.io -p 12498 PING
PONG
```

## Redis Labs (cloud)

Use an external redis server.

```bash session
$ redis -h redis-18650.c325.us-east-1-4.ec2.redns.redis-cloud.com -p 18650 
-a sMvW0CnKQG1A******************** PING
PONG
```

## Python Client

```bash session
$ conda install redis-py  # Install Redis Python client
```

```pycon
>>> import redis
>>> r = redis.Redis(host="localhost", port=6379)  # or simply r = redis.Redis()
>>> r.ping()
True
```

> [!WARNING]
> If the Redis server is not started `r.ping()` won't return `False`,
> but will raise an error instead:
> 
> ```pycon
> >>> r.ping()
> Traceback (most recent call last):
> ...
> redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379. Connection refused.
> ```


Redis version of "Hello world!" in Python.

```pycon
>>> r.set("message", b"Hello world!")
True
>>> r.get("message")
b'Hello world!'
```

## Publish-Subscribe

Create a pubsub object, subscribe to the "chat" channel.

```pycon
>>> import redis
>>> r = redis.Redis()
>>> p = r.pubsub()
>>> p.subscribe("chat")
```

Check your messages. You have received the confirmation of your subscription!

```pycon
>>> p.get_message()
{'type': 'subscribe', 'pattern': None, 'channel': b'chat', 'data': 1}
```

Now, since noone has published anything on the `chat` channel yet,
any subsequent attemps to read a message will return `None`.

```pycon
>>> p.get_message()
```

Send a message on the chat channel

```pycon
>>> r.publish("chat", b"Hello chat!")  # Return the number of "chat" subscribers
1
```

Then read it

```pycon
>>> p.get_message()
{'type': 'message', 'pattern': None, 'channel': b'chat', 'data': b'Hello chat!'}
```

Now your list of unread messages is empty again:

```pycon
>>> p.get_message()
```

Note that you won't receive any message that was sent to a channel prior to
your subscription:

```pycon
>>> r.publish("another chat", b"First message")
>>> p.subscribe("another chat")
>>> r.publish("another chat", b"Second message")
>>> p.get_message()
{'type': 'message', 'pattern': None, 'channel': b'another chat', 'data': b'Second message'}
```

You also won't receive the same message twice ... or maybe at all if you are
temporarily disconnected from the Redis server.

## Chat App

Simple chat writer:

```python
import redis
r = redis.Redis()

name = input("Enter your nickname: " )
while True:
    message = input("> ")
    data = f"{name}: {message}"
    r.publish("chat", data.encode("utf-8"))
```

Chat reader with blocking read:

```python
import threading

import redis

FOREVER = threading.TIMEOUT_MAX

r = redis.Redis()
p = r.pubsub()

p.subscribe("chat")
m = p.get_message(timeout=FOREVER)
assert isinstance(m, dict) and m.get("type") == "subscribe"

while True:
    m = p.get_message(timeout=FOREVER)
    data = m["data"]
    print(data.decode("utf-8"))
```

## Structured data

Let's transmit our name and message to the server and let him format 
the message as he wishes.

Writer:

```python
import json

import redis

FOREVER = threading.TIMEOUT_MAX

r = redis.Redis()

name = input("Enter your nickname: " )
while True:
    message = input("> ")
    data = {"name": name, "message": message}
    binary = json.dumps(data, ensure_ascii=False).encode("utf-8")
    r.publish("chat", binary)
```

Reader:

```python
import json
import threading

import redis

FOREVER = threading.TIMEOUT_MAX

r = redis.Redis()
p = r.pubsub()

p.subscribe("chat")
m = p.get_message(timeout=FOREVER)
assert isinstance(m, dict) and m.get("type") == "subscribe"

while True:
    m = p.get_message(timeout=FOREVER)
    binary = m["data"]
    data = json.loads(binary.decode("utf-8"))
    name = data["name"]
    message = data["message"]
    print(f"{name}: {message}")
```

## Mailbox

`inbox.py`:

```python
import math
import os
import platform

import redis

TIMEOUT = 1.0

r = redis.Redis()
p = r.pubsub()

name = platform.node() + "-" + os.getpid()
print(f"my inbox name is {name}")

p.subscribe(name)
m = p.get_message(timeout=FOREVER)
assert isinstance(m, dict) and m.get("type") == "subscribe"

# TODO: timeout against denial of service
def get_messages():
    messages = []
    while True:
        m = p.get_message()
        if m is None:
            break
        messages.append(m["data"])
```

**TODO:** Mail payload structure and API

Payload: from, to, cc, subject, body

API:

  - messages = get_messages()

  - print_message(message)

  - send(message, to)
  
  - reply(message_received, message)  (do bottom-posting and quoting)
  
  - reply_all(message_received, message)

## Distributed computation

Computation of pi, coming from remote actors.

Payload: number of samples, value. 

Stream of volontary computations received continuously without asking first.


File `mc_pi.py`
```python
import numpy.random as npr

def mc_pi(n):
    x = npr.random(n)
    y = npr.random(n)
    t = (x*x + y*y <= 1.0)
    pi_approx = 4 * t.mean()
    return pi_approx
```

File `pi_worker.py`
```python
import json

import redis

from mc_pi import mc_pi

r = redis.Redis()
channel = "pi_collector"

def send_pi_approx():
    n = 100_000_000
    pi_approx = mc_pi(n)
    binary_data = json.dumps({"n": n, "pi_approx": pi_approx}).encode("utf-8")
    r.publish(channel, binary_data)
```


Collector (interactive):
```python
import json

import redis

# Start channel

inbox = []

# fct to accumulate messages in inbox

# fct to compute pi and estimate standard deviation / check it.

```

## Subprocesses (spawn actors)

Progressions:

  - specialized (one-feature, then many-methods) to generic workers

  - short-lived to long-lived (mmm maybe not necessary?)


`clock.py`:

```python
from datetime import datetime 
import json
import os
import threading

import redis

FOREVER = threading.TIMEOUT_MAX

r = redis.Redis()
p = r.pubsub()

p.subscribe(os.getpid())
m = p.get_message(timeout=FOREVER)
assert m is not None and m.get("type") == "subscribe"

def get_current_time():
    now = datetime.now()
    return {"hour": now.hour, "minute": now.minute, "second": now.second}

while True:
    m = p.get_message(timeout=FOREVER)
    current_time = get_current_time()
    binary = m["data"]
    data = json.loads(binary.decode("utf-8"))
    reply_to = data["reply-to"]
    r.publish(reply_to, json.dumps(current_time).encode("utf-8"))
```

```python
import json
import os
import platform
import sys
import subprocess
import threading
import time

import redis

FOREVER = threading.TIMEOUT_MAX

r = redis.Redis()
p = r.pubsub()

name = platform.node() + "-" + os.getpid()
print(f"my inbox name is {name}")

p.subscribe(name)
m = p.get_message(timeout=FOREVER)
assert m is not None and m.get("type") == "subscribe"

clock = subprocess.Popen([sys.executable, "clock.py"])
time.sleep(0.1) # make sure that the subprocess has time to register to its own 
# inbox. A more foolproof mechanism (broadcast a "ready" somewhere? But where?) 
# would be nice. I'd really like not to use stdout/stdin to communicate between
# processes (that would defeat the purpose!)
# So maybe the master should pass its own mailbox as a command-line argument.
# Yeah that's probably for the best: that + an "ACK" message to let the master
# know that the worker is ready to receive messages.

while True:
    r.publish(clock.pid, json.dumps({"reply-to": platform.node()}))
    m = p.get_message(timeout=FOREVER)
    current_time = json.loads(m["data"].decode("utf-8"))
    print(current_time)
    time.sleep(5.0)
```


**TODO.** Program regular timer? With start/stop?

## Parallelize computations

```python
import math

import numpy as np
import numpy.random as npr


rs = []

n = 100_000_000
x = npr.random(n)
y = npr.random(n)

t = (x*x + y*y <= 1.0)


r = 4 * t.mean()
print(r)
print(np.abs(r - math.pi))
```

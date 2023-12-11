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


```bash session
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

## Python

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
>>> p = r.pubsub(ignore_subscribe_messages=True)
>>> p.subscribe("chat")
```

Ask for the oldest message send to all of you subscription -- if any. 
So far you have received nothing, that will return `None`.

```pycon
>>> p.get_message()
```

> [!NOTE]
> If you have created your pubsub client with `ignore_subscribe_messages=True`
> (the default), you actually have received a message: the confirmation of your
> subscription:
>
> ```pycon
> >>> p = r.pubsub()
> >>> p.get_message()
> {'type': 'subscribe', 'pattern': None, 'channel': b'chat', 'data': 1}
> ```

Send a message on the chat channel

```pycon
>>> r.publish("chat", b"Hello chat!")  # Return the number of "chat" subscribers
1
```

```pycon
>>> p.get_message()
{'type': 'message', 'pattern': None, 'channel': b'chat', 'data': b'Hello stranger!'}
```



>>> 


```
>>> p.get_message()
{'type': 'message', 'pattern': None, 'channel': b'chat', 'data': b'Hello stranger!'}
>>> p.get_message()
{'type': 'message', 'pattern': None, 'channel': b'chat', 'data': b'Hello stranger!'}
>>> p.get_message()
>>> p.get_message()
```

## Chat App

## Mail model

## JSON exchange

## Promises

## Remote execution

(cloudpickle, etc.)

## Patterns?
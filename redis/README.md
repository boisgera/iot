Redis
================================================================================

```bash session
$ conda create --name redis
...
$ conda activate redis
$ conda install python redis-server redis-py
...
```


```bash session
$ redis-server
60817:C 31 Jul 2023 15:33:14.698 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
60817:C 31 Jul 2023 15:33:14.698 # Redis version=5.0.3, bits=64, commit=00000000, modified=0, pid=60817, just started
60817:C 31 Jul 2023 15:33:14.698 # Warning: no config file specified, using the default config. In order to specify a config file use redis-server /path/to/redis.conf
60817:M 31 Jul 2023 15:33:14.699 * Increased maximum number of open files to 10032 (it was originally set to 1024).
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

--------------------------------------------------------------------------------

```pycon
>>> import redis
>>> r = redis.Redis(host="localhost", port=6379, decode_responses=True)
>>> r.ping()
True
```

```pycon
>>> r.ping()
Traceback (most recent call last):
...
redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379. Connection refused.
```

```pycon
>>> try:
...     r.ping()
... except redis.ConnectionError as e:
...     print(e)
...
Error 111 connecting to localhost:6379. Connection refused.
```

```pycon
>>> r.set("message", "Hello world!")
True
>>> r.get("message")
'Hello world!'
```

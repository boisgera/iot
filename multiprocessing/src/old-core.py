"""
>>> @asyncify
... def add_one(x):
...     return x + 1
...
>>> promise = add_one(2)
>>> promise()
3

>>> promise()
3

>>> promise = add_one("Hello")
>>> promise()
Traceback (most recent call last):
...
TypeError: can only concatenate str (not "int") to str

>>> import time
>>> dt = 1e-2

>>> @asyncify
... def add_one(x):  # slow version
...     time.sleep(1.0)
...     return x + 1
...
>>> start = time.time()
>>> promise = add_one(2)
>>> time.time() - start <= dt
True
>>> promise()
3
>>> 1.0 <= time.time() - start <= 1.0 + dt
True
>>> start = time.time()
>>> promise()
3
>>> time.time() - start <= dt
True

>>> @asyncify
... def greet(name):
...     time.sleep(1.0)
...     open("greet.txt", "tw").write(f"Hello {name}")
...
>>> promise = greet("stranger!")
>>> promise()
>>> open("greet.txt").read()
'Hello stranger!'

>>> promise = greet("world!")
>>> promise.kill()
>>> open("greet.txt").read()
'Hello stranger!'

"""

# Nota: how the fuck do the test work? How can one reconstruct `add_one`
#       from a module that doesn't exist AND additionally when the function
#       is overriden by the decorator???

import doctest
import multiprocessing as mp
import os
import signal



# TODO:
#  - make notes / examples about closures that won't work,
#    bound methods that won't work, etc. with processes
#  - explain the consequences of reimport of the functions.
#  - make notes about the pickling stuff that takes place
#    and maybe some examples of what can be pickled and what can't.
#  - use pickletools to see what's going on in pickle files?
#    too bad jsonpickle doesn't cut it (identity not preserved to
#    begin with).

# TODO: make asyncified functions automatically (lazily) support promises
#       arguments ?
#       So that the composition of async function can be "normal"-ish (?)
# TODO: "flag" the asyncified functions with an attribute.
#       Make an "is_async" function that checks that.


# Asyncify
# ------------------------------------------------------------------------------
class Promise:
    def __init__(self, queue, process):
        self._queue = queue
        self._process = process

    def __call__(self):
        if hasattr(self, "_error"):
            if self._error is not None:
                raise self._error
            else:
                return self._value
        else:
            self._value, self._error = self._queue.get()
            self._process.join()
            return self()

    def kill(self):
        pid = self._process.pid
        try:
            os.kill(pid, signal.SIGINT)
        except ProcessLookupError:
            pass


def return_or_raise_in_queue(function, args, kwargs, queue):
    try:
        value = function(*args, **kwargs)
        error = None
    except KeyboardInterrupt:
        value = None
        error = None
    except Exception as e:
        value = None
        error = e
    queue.put((value, error))

class asyncify:
    def __init__(self, function):
        self._function = function

    def __call__(self, *args, **kwargs):
        queue = mp.Queue()
        target_args = (self._function, args, kwargs, queue)
        process = mp.Process(target=return_or_raise_in_queue, args=target_args)
        process.start()
        return Promise(queue, process)


# ------------------------------------------------------------------------------


# Picklable & Parallelizable Iterator Helpers
class StepIterator:
    def __init__(self, it, step, offset):
        # For multiple step iterators to work **in the same process**
        # the iterable must be re-iterable (e.g. range(n) is).
        # But the step iterator itself is not. (It should be though ...)
        self.it = it
        self.iterator = iter(it)
        # print("*", list(iter(it)))
        self.step = step
        self.offset = offset
        self.counter = 0

    def __repr__(self):
        return f"StepIterator({self.it}, step={self.step}, offset={self.offset})"

    def __iter__(self):
        return self

    def __next__(self):
        while self.counter % self.step != self.offset:
            self.counter += 1
            next(self.iterator)
        self.counter += 1
        return next(self.iterator)


def split_iterator(it, n=2):
    return [StepIterator(it, step=n, offset=i) for i in range(n)]


# Compute Pi
# ------------------------------------------------------------------------------

from fractions import Fraction


### Ah that's slow but nicely parallelizable, exactly what I like :)
def compute_pi(n):
    return 4 * sum(Fraction((-1) ** k, 2 * k + 1) for k in range(n))


### Prepare compute_pi first: generalize to accept iterators
def compute_pi(n):
    if isinstance(n, int):
        it = range(n)
    else:
        it = n
    return 4 * sum(Fraction((-1) ** k, 2 * k + 1) for k in it)


def compute_pi(n, parallel=False):
    if isinstance(n, int):
        it = range(n)
    else:
        it = n
    if not parallel:
        return 4 * sum(Fraction((-1) ** k, 2 * k + 1) for k in it)
    if parallel is True:
        parallel = os.cpu_count()
    else:
        parallel = int(parallel)

    iterators = split_iterator(it, parallel)
    partials = [asyncify(compute_pi)(it, parallel=False) for it in iterators]
    return sum(partial() for partial in partials)


# Actors
# ------------------------------------------------------------------------------
def actor(cls, args, kwargs, queue):
    self = cls(*args, **kwargs)
    while True:
        method_name, args, kwargs, answer_queue = queue.get()
        answer = getattr(self, method_name)(*args, **kwargs)
        answer_queue.put(answer)


class Method:
    def __init__(self, name, proxy):
        self._name = name
        self._proxy = proxy

    def __call__(self, *args, **kwargs):
        return self._proxy._call_method((self._name, args, kwargs))


class Proxy:
    def __init__(self, cls):
        self._cls = cls

    def __call__(self, *args, **kwargs):
        self._queue = mp.Queue()
        mp.Process(target=actor, args=(self._cls, args, kwargs, self._queue)).start()
        return self

    def __getattr__(self, name):
        return Method(name, self)

    def _call_method(self, name, args, kwargs):
        queue = mp.Queue()
        self._queue.put((name, args, kwargs, queue))
        return Promise(queue)


def actorify(cls):
    return Proxy(cls)  # Mmm this need to be a class. Mmmm.


# Crypto
# ------------------------------------------------------------------------------
import numpy as np
import hashlib


def proof_of_work(data, level=1):
    # A 2**64 space is plenty; in any case, we'll never get to the end
    # since even an empty loop over that many values takes centuries.
    for i in range(2**64):
        key = np.uint64(i).tobytes()
        if check_proof_of_work(data, key, level):
            return key


def check_proof_of_work(data, key, level=1):
    digest = hashlib.sha256(data + key).digest()
    return digest.startswith(b"\x00" * level)

# TODO: get the first of promise that yields, del the others.
#       How do we do that? We need an extra "construct" where
#       we make everyone return in the same queue, and then
#       get the queue. So we need to wrap every stuff in another
#       layer of processes. This is a select-like construct IMHO.

# TODO: first of Promises that yields. Complicated because of our API choice :(
# AFAICT, we need to dwelve back into the Process API, we can't just use our
# abstraction. Or maybe it's simpler with the Actor paradgim(?)


# NOTA: in this scheme, we are not CANCELLING the other processes ;
#       They are still running in the background until completion.
# Conclusion: the "run all" stuff can be nicely abstracted on top of
# the "asyncify" decorator. But the "yield first" not so much unless
# we tweak the design, with shared return value and cancellation.
#
# Add a common "promise" target is easy in the current design,
# but the cancellation is not. And if the return value is a common
# promise, and not individual promises, then the problem is even
# more severe, since we cannot pass let's say process ids to get
# tasks killed. OTHERWISE, it would be a good idea to have a promise
# carry a "kill" switch ("renounce"? "relnquish"? "give_up"?).
#
# Yeah, maybe we should have that to start with. And then make a select
# on top of that. BUT, if the process killed had subprocesses, then what's
# going on? Unless it explicity handles "kill" (HUP?) signals, it will
# just die and leave the subprocesses running ...
# def return_in_queue(promise, queue):
#     queue.put(promise())


# def yield_first(promises):
#     queue = mp.Queue()
#     for promise in promises:
#         mp.Process(target=return_in_queue, args=(promise, queue)).start()
#     return Promise(queue)


# TODO: split_range would be nice here (with many options of course)


# Simple version of parallel proof of work that goes around the limitations
# of the current design. It's not very nice, but it works.
def proof_of_work(data, level=1, parallel=False, _range=None):
    if _range is None:
        _range = range(2**64)
    if not parallel:
        for i in _range:
            key = np.uint64(i).tobytes()
            if check_proof_of_work(data, key, level):
                return key
        else:
            return None

    if parallel is True:
        parallel = os.cpu_count()
    else:
        parallel = int(parallel)

    N = 2**20
    assert _range == range(2**64)
    workers = []
    current_range = range(0)
    while True:
        while len(workers) < parallel:
            start = current_range.stop
            stop = start + N
            current_range = range(start, stop)
            workers.append(
                asyncify(proof_of_work)(
                    data, level, parallel=False, _range=current_range
                )
            )
        if (key := workers.pop(0)()) != None:
            return key


# TODO: parallelize that

# ------------------------------------------------------------------------------


def grok_promises(f):
    def lazy_f(*args, **kwargs):
        args = [arg.get() if hasattr(arg, "get") else arg for arg in args]
        kwargs = {k: v.get() if hasattr(v, "get") else v for k, v in kwargs.items()}
        return f(*args, **kwargs)

    return lazy_f


# Now, we can make some stuff "lazy"


def lazy(f):
    return asyncify(grok_promises(f))


# TODO:
#   - ressource analysis at each step (here: memory & cpu)
#   - make a simple process-based ressource logger?
#   - other "classic" concurrent & distributed schemes.
#   - abstract some remote stuff from multiprocessing (urk, probably not)

# TODO:
#   - Actors (ie "subject") aka long-running processes you discuss with.
#   - Use proxy / rpc-like approach (abstraction on top of queues?)

# ------------------------------------------------------------------------------

# Everything is synchronous so far (but running in another process)

class PromiseFromQueue:
    def __init__(self, queue, id):
        self._queue = queue
        self._id = id

    def __call__(self):
        if hasattr(self, "_value"):
                return self._value
        else:
            self._value = self._queue.get()
            return self()

    def kill(self):
        pid = self._process.pid
        try:
            os.kill(pid, signal.SIGINT)
        except ProcessLookupError:
            pass

def self_loop(cls, args, kwargs, input_queue, output_queue):
    # MMmm we need to start
    self = cls(*args, **kwargs)
    while True:
        method_name, args, kwargs = input_queue.get()
        answer = getattr(self, method_name)(*args, **kwargs)
        output_queue.put(answer)

# TODO: promisify (but serialize!) the methods calls.

def make_proxy(cls):
    def __init__(self, *args, **kwargs):
        self._counter = 0
        self._answers = {} 
        self._input_queue = mp.Queue()
        self._output_queue = mp.Queue()
        args=(cls, args, kwargs, self._input_queue, self._output_queue)
        self._process = mp.Process(target=self_loop, args=args)
        self._process.start()
    def __getattr__(self, name):
        def method(*args, **kwargs):
            self._input_queue.put((name, args, kwargs, self.counter))
            self.counter += 1
            return _Promise(self._output_queue, self.counter)
        return method
    def kill(self):
        pid = self._process.pid
        try:
            os.kill(pid, signal.SIGINT)
        except ProcessLookupError:
            pass

    cls_proxy = type(cls.__name__ + "Proxy", (), {
        "__init__": __init__, 
        "__getattr__": __getattr__,
        "kill": kill,
    })
    return cls_proxy

class Store:
    def __init__(self, value):
        self.value = value
    def get_value(self):
        return self.value
    def set_value(self, value):
        self.value = value

def test_proxy():
    """
    >>> StoreProxy = make_proxy(Store)
    >>> s = StoreProxy("yay!")
    >>> s.get_value()
    'yay!'
    >>> s.set_value("nay!")
    >>> s.get_value()
    'nay!'
    """
    pass

# ------------------------------------------------------------------------------

if __name__ == "__main__":
    doctest.testmod()


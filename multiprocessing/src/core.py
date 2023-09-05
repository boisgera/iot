import multiprocessing as mp
import os
from typing import Any

# TODO: single function/decorator that can be used on functions and classes?
#       "processify"? "workerify"? "actorify"? "parallelize"? "asyncify"?

# TODO: wrap_t this stuff?

# TODO:
#  - make notes / examples about closures that won't work,
#    bound methods that won't work, etc. with processes
#  - explain the consequences of reimport of the functions.
#  - make notes about the pickling stuff that takes place
#    and maybe some examples of what can be pickled and what can't.

# TODO: "flag" the asyncified functions with an attribute.
#       Make an "is_async" function that checks that.

# TODO: wrap a Queue into a Promise object (new class),
#       that will make things simpler.

# TODO: make asyncified functions automatically (lazily) support promises?
#       So that the composition of async function can be "normal"-ish.

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

# Asyncify
# ------------------------------------------------------------------------------
class Promise:
    def __init__(self, queue=None):
        if queue is None:
            queue = mp.Queue()
        self._queue = queue
    def __call__(self):
        try:
            return self._value
        except AttributeError:
            self._value = self._queue.get()
            return self()

def return_in_queue(f, args, kwargs, queue):
    value = f(*args, **kwargs)
    queue.put(value)

class asyncify:
    def __init__(self, f):
        self._f = f
    def __call__(self, *args, **kwargs):
        queue = mp.Queue()
        target_args = (self._f, args, kwargs, queue)
        process = mp.Process(target=return_in_queue, args=target_args)
        process.start()
        return Promise(queue)

# Compute Pi
# ------------------------------------------------------------------------------

from fractions import Fraction

### Ah that's slow but nicely parallelizable :)
def compute_pi(n):
    return 4 * sum(Fraction((-1)**k, 2*k+1) for k in range(n))

### Prepare compute_pi first: generalize to accept iterators
def compute_pi(n):
    if isinstance(n, int):
        it = range(n)
    else:
        it = n
    return 4 * sum(Fraction((-1)**k, 2*k+1) for k in it)

def compute_pi(n, parallel=False):
    if isinstance(n, int):
        it = range(n)
    else:
        it = n
    if not parallel:
        return 4 * sum(Fraction((-1)**k, 2*k+1) for k in it)
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

    return Proxy(cls) # Mmm this need to be a class. Mmmm.

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
def return_in_queue(promise, queue):
    queue.put(promise())

def yield_first(promises):
    queue = mp.Queue()
    for promise in promises:
        mp.Process(target=return_in_queue, args=(promise, queue)).start()
    return Promise(queue)

def proof_of_work(data, level=1, it=None, parallel=False):
    if it is None:
        it = range(2**64)
    if not parallel:
        for i in it:
            key = np.uint64(i).tobytes()
            if check_proof_of_work(data, key, level):
                return key
        else:
            return None

    if parallel is True:
        parallel = os.cpu_count()
    else:
        parallel = int(parallel)

    it = range(2**64)
    iterators = split_iterator(it, parallel)
    # Need to start the processes and check for the first that returns AND
    # for which the return value is not None. Arf, so we need a select-like
    # construct. This is "our fault" since our asyncify generates a Promise
    # for each function.

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
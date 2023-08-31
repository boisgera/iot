import multiprocessing as mp
import os

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
    def __init__(self, queue):
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

### Ah that's nicely parallelizable :)
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

# Crypto
# ------------------------------------------------------------------------------
import numpy as np
import hashlib

def proof_of_work(data, level=1, verbose=False):
    for i in range(2**64 - 1):
        key = np.uint64(i).tobytes()
        if check_proof_of_work(data, key, level, verbose):
            return key

def check_proof_of_work(data, key, level=1, verbose=False):
    digest = hashlib.sha256(data + key).digest()
    if verbose:
        print(digest)
    return digest.startswith(b"\x00" * level)

# TODO: parallelize that

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
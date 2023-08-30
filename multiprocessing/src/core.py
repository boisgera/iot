import multiprocessing as mp

# TODO: wrap_t this stuff?

def _a_target(f, args, kwargs, queue):
    queue.put(f(*args, **kwargs))

def cast(f):
    def wrapper_f(*args, **kwargs):
        queue = mp.Queue()
        p = mp.Process(target=_a_target, args=(f, args, kwargs, queue))
        p.start()
        return queue
    return wrapper_f

# "grok_promises" is a better name than "unwrap" or "unwrap_promises"
# We could call that "strict"? "auto_get"? "auto_unwrap"? "auto_unpromise"?

# TODO: compute_pi by Bellard

from fractions import Fraction as F 

### Ah that's nicely parallelizable :)
def compute_pi(n):
    return float(4 * sum(F((-1)**k, 2*k+1) for k in range(n)))


# TODO: noonce (crypto stuff)

def grok_promises(f):
    def lazy_f(*args, **kwargs):
        args = [arg.get() if hasattr(arg, "get") else arg for arg in args]
        kwargs = {k: v.get() if hasattr(v, "get") else v for k, v in kwargs.items()}
        return f(*args, **kwargs)
    return lazy_f

# Now, we can make some stuff "lazy"

def lazy(f):
    return cast(grok_promises(f))

def compute_pi(n, post=float):
    if not isinstance(n, range):
        n = range(n)
    r = n
    return post(4 * sum(F((-1)**k, 2*k+1) for k in r))

# TODO: 
#   - make that work with range
#   - support number of nodes
#   - make the map-reduce scheme obvious

def better_compute_pi(n, post=float):
    # Shit, we need to support range :(. OK, learn to split a range, that's fine
    r_len = n // 8
    ranges = [range(i*r_len, (i+1)*r_len) for i in range(7)]
    ranges.append(range(7*r_len, n))
    partials = [cast(compute_pi)(r, post=lambda x:x) for r in ranges]
    return post(sum(partial.get() for partial in partials))

# TODO:
#   - ressource analysis at each step (here: memory & cpu)
#   - other "classic" concurrent & distributed schemes.
#   - abstract some remote stuff from multiprocessing (urk, probably not)
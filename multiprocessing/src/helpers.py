import multiprocessing as mp
import time

if __name__ == "__main__":
    mp.set_start_method("spawn")  # would break in the subprocess

# TODO: Implicit pool of workers ?


def wrapper(args, kwargs, fun, queue):
    queue.put(fun(*args, **kwargs))


def task(fun):
    def start(*args, **kwargs):
        queue = mp.Queue()
        p = mp.Process(target=wrapper, args=(args, kwargs, fun, queue))
        p.start()
        return queue

    return start

# ------------------------------------------------------------------------------

def transfer(input, output):
    while True:
        output.put(input.get())

def merge_queues(queues):
    output = mp.Queue()
    for input in queues:
        mp.Process(target=transfer, args=(input, output)).start()
    
# ------------------------------------------------------------------------------


N = 10_000_000


def f(x):
    for i in range(N):
        x = (x + i) % 3.14
    return x


if __name__ == "__main__":
    t_0 = time.time()
    print(f(60.0))
    t = time.time()
    print(f"Time: {t - t_0:.3f} s")

    f2 = task(f)
    t_0 = t
    print(f2(60.0).get())
    t = time.time()
    print(f"Time: {t - t_0:.3f} s")

    t_0 = time.time()
    print(f(60.0))
    t = time.time()
    print(f"Time: {t - t_0:.3f} s")

    f2 = task(f)
    t_0 = t
    print(f2(60.0).get())
    t = time.time()
    print(f"Time: {t - t_0:.3f} s")

    print(40 * "-")

    t_0 = time.time()
    print(f(f(f(60.0))))
    t = time.time()
    print(f"Time: {t - t_0:.3f} s")

    f2 = lambda *args, **kwargs: task(f)(*args, **kwargs).get()
    t_0 = t
    print(f2(f2(f2(60.0))))
    t = time.time()
    print(f"Time: {t - t_0:.3f} s")

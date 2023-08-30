import multiprocessing as mp
import time

if __name__ == "__main__":
    mp.set_start_method("spawn")

# TODO: Implicit pool of workers ?


def task(fun):
    def wrapper(args, kwargs, queue):
        queue.put(fun(*args, **kwargs))

    def start(*args, **kwargs):
        queue = mp.Queue()  # Wait, Process can manage a function
        # which is not importable (?!?). Ah, no, won't work with say
        # "spawn" start method (only with forks). And of course
        # wouldn't work with in a distributed setting.
        # The error is: 
        #     AttributeError: Can't pickle local object 'task.<locals>.wrapper'
        p = mp.Process(target=wrapper, args=(args, kwargs, queue))
        p.start()
        return queue  # TODO: return something that "waits" instead?

    return start


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

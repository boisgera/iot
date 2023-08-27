import math
import multiprocessing as mp

N = 500_000

def f(x):
    for i in range(N):
        x = (x + i) % math.pi
    return x

def wrapper(x, queue):
    queue.put(f(x))

if __name__ == "__main__":
    data = range(100)
    queue = mp.Queue()
    processes = [mp.Process(target=wrapper, args=(x, queue)) for x in data]
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    print(max(*[queue.get() for p in processes]))

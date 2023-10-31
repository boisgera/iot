import multiprocessing as mp

inner_queue = mp.Queue()

def printer(queue):
    while True:
        print(queue.get())

p1  = mp.Process(target=printer, args=(inner_queue,)).start()

outer_queue = mp.Queue()

def answerer(queue):
    while True:
        _inner_queue = queue.get()
        _inner_queue.put(42)

p2 = mp.Process(target=answerer, args=(outer_queue,)).start()

outer_queue.put(inner_queue)

p2.join()
p1.join()
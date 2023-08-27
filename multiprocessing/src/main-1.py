import math

N = 500_000

def f(x):
    for i in range(N):
        x = (x + i) % math.pi
    return x

if __name__ == "__main__":
    print(max(*[f(x) for x in range(100)]))

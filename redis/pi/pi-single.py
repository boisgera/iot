import numpy as np
import numpy.random as npr

N = 80_000_000 # 640 Mo data

partial_results = []

def step():
    x = npr.random(N)
    y = npr.random(N)
    t =  x * x + y * y <= 1.0
    return 4 * t.mean()

while True:
    partial_results.append(step())
    p = 3.15 / 4
    q = (1 - 3.14/4)
    n = N * len(partial_results)
    sigma = 4 * np.sqrt(p * q / n)
    pi_approx = np.mean(partial_results)
    print(f"{pi_approx:.17f} {abs(pi_approx - np.pi):.2g} {3.0*sigma:.2g}")
    # print(f"pi = {pi_approx} ± {3.0*sigma:.3g}" + \
    #   f"    (check: {pi_approx-3.0*sigma <= np.pi <= pi_approx+3.0*sigma})")
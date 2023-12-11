import math
import time

from core import asyncify

sqrt = asyncify(math.sqrt)

p = sqrt(4.0)

print("zzz...")
time.sleep(1.0)

print(p())


import sys
import time
import multiprocessing.shared_memory as sm

import numpy as np

create = False
if len(sys.argv) >= 2:
    create = sys.argv[1] == "--create"

memory = sm.SharedMemory("shared-buffer", create=create, size=8)
array = np.asarray(memory.buf, dtype=np.int64)

for i in range(100_000_000):
    array[0] += 1
    array[0] -= 1

print(f"{array[0] = }")

time.sleep(60.0)

# if create:
#     time.sleep(60.0)
#     memory.close()
#     memory.unlink()
# else:
#     memory.close()





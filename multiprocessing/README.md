# Multiprocessing

Somehow, manage to measure and stress and optimize for many ressources:

  - CPU load
  - Memory
  - Filesystem
  - Network
  - External ressources

**TODO:**

  - start a "function" on another process 
    (use a ressource-neutral `time.sleep()`)

  - pass arguments (wait time?)

  - see that the main exit at once ; explain how to wait for completion

  - how to get a return value if needed (`queue`, use a wrapper).

  - think about an interface to "wrap" a function to have
    same process / other process and blocking / non-blocking interfaces?

  - explore limitations (pickling, importable functions, etc.)
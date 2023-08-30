# Python Standard Library
import json
import multiprocessing as mp
import webbrowser

# External Libraries
import bottle
import psutil
import typer

cli = typer.Typer()

# TODO:
#   - memory consumption
#   - cpu usage
#   - disk usage
#   - network usage

# TODO:
#   - textual top-like interface?
#   - API for getting process info (HTTP? Yes)
#   - Make as SPA on top of this API (same program).

# -------------------------------------------------------

# LINE_UP_CLEAR = '\033[1A\x1b[2K'

# filters = ["sh", "cpuUsage.sh", "sleep"]

# track = ["python"]


# processes = {}

# lines = 0

# while True:
#     print(lines * LINE_UP_CLEAR, end="")
#     check = processes.copy()
#     for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
#         info = proc.info
#         pid = info['pid']
#         name = info["name"]
#         if pid in processes:
#             del check[pid]
#             if info["name"] in track:
#                 print(f"Process: {info}")
#                 lines += 1
#         else:
#             if info["name"] not in filters:
#                 print(f"New process: {info}")
#                 lines += 1
#                 processes[pid] = info
#     for pid in check:
#         print(f"Process gone: {info}")
#         lines += 1
#         del processes[pid]
#     time.sleep(3)


@bottle.get("/<filepath:re:.*\.js>")
def js(filepath):
    return bottle.static_file(filepath, root=".")

@bottle.route("/")
def index():
    return bottle.static_file("index.html", root=".")

@bottle.route("/api")
def api():
    keys = ["pid", "name", "cpu_percent", "memory_percent"]
    stats = list(p.info for p in psutil.process_iter(keys))
    bottle.response.content_type = "application/json"
    return json.dumps(stats, indent=4, sort_keys=True)


@cli.command()
def main(host: str = "127.0.0.1", port: int = 8080, browser: bool = False):
    if browser:
        mp.Process(target=webbrowser.open, args=(f"http://{host}:{port}/",)).start()
    bottle.run(host=host, port=port)



if __name__ == "__main__":
    cli()

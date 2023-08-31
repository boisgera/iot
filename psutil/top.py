# Python Standard Library
import json
import webbrowser

# External Libraries
import bottle
import psutil
import typer

app = typer.Typer()


@bottle.route("/")
def api():
    keys = ["pid", "ppid", "name", "cpu_num", "cpu_percent", "memory_percent"]
    stats = list(p.info for p in psutil.process_iter(keys))
    bottle.response.content_type = "application/json"
    out = json.dumps(stats, indent=4, sort_keys=True) + "\n"
    return out


@app.command()
def main(host: str = "127.0.0.1", port: int = 8000, browser: bool = False):
    if browser:
        webbrowser.open(f"http://{host}:{port}")
    bottle.run(host=host, port=port)


if __name__ == "__main__":
    app()

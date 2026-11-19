#!/usr/bin/python3
"""
dockerd-sim.py - a READ-ONLY Docker API mock listening on a unix socket.

Training goal: prove that /var/run/docker.sock == root on a real box.
This mock only implements the read path of the Docker API:

  GET  /version, /_ping, /info, /containers/json
  POST /containers/create   {"Image":"alpine","Cmd":["cat","/host/flag.txt"],
                             "Binds":["/:/host"]}
  POST /containers/{id}/start
  GET  /containers/{id}/logs
  POST /containers/{id}/wait
  DELETE /containers/{id}

Safety model (deliberate, so this challenge can never become a real escape):

  * The only bind source accepted is "/", which is mapped to the daemon's
    own read-only "host root view" (/var/lib/dockersim/hostroot).
  * Cmd is an allow-list of read-only tools: cat, ls, id, whoami, uname.
    Nothing is ever executed - there is no subprocess in this program.
  * Every path argument is resolved and must stay inside the host root view;
    "..", absolute host paths and symlink tricks are rejected.
  * The host root view is root:root 0700, so a normal user cannot read it
    directly; only the daemon (running as root) can serve it.
"""

import json
import os
import re
import socketserver
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler

SOCK = "/var/run/docker.sock"
HOSTVIEW = "/var/lib/dockersim/hostroot"
STATE = {}
LOCK = threading.Lock()
SERVER_ID = uuid.uuid4().hex

ALLOWED = {"cat", "ls", "id", "whoami", "uname"}
MAX_OUT = 64 * 1024


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%S.000000Z", time.gmtime())


class BadRequest(Exception):
    pass


def inside_hostview(path):
    """Return the real path if it stays inside the host root view, else None."""
    try:
        real = os.path.realpath(path)
    except Exception:
        return None
    base = os.path.realpath(HOSTVIEW)
    if real == base:
        return real
    if real.startswith(base + os.sep):
        return real
    return None


def normalize_bind(bind):
    if not isinstance(bind, str):
        raise BadRequest("binds must be strings")
    parts = bind.split(":")
    src = parts[0]
    dst = parts[1] if len(parts) > 1 else ""
    if src.rstrip("/") != "" or src in ("/", "//"):
        # only the host root may be bound
        if src.strip("/") == "":
            return HOSTVIEW, dst
    raise BadRequest("bind source %r rejected: only '/' is allowed" % src)


def translate(arg, binds):
    """Translate /host/flag.txt into the real path inside the host root view."""
    if not isinstance(arg, str):
        return None
    for real, dst in binds:
        d = "/" + dst.strip("/")
        if d == "/":
            return os.path.join(real, arg.lstrip("/"))
        if arg == d:
            return real
        if arg.startswith(d + "/"):
            return os.path.join(real, arg[len(d) + 1:])
    return None


def parse_cmd(cmd):
    if isinstance(cmd, str):
        cmd = ["/bin/sh", "-c", cmd]
    if not isinstance(cmd, list) or not cmd:
        raise BadRequest("Cmd must be a non-empty array")
    if not all(isinstance(a, str) for a in cmd):
        raise BadRequest("Cmd elements must be strings")
    prog = os.path.basename(cmd[0])
    if prog not in ALLOWED:
        raise BadRequest("command %r not permitted by this endpoint policy" % prog)
    return prog, cmd[1:]


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "Docker/24.0.7 (sim)"

    def log_message(self, fmt, *args):
        pass

    def _send(self, code, obj, ctype="application/json"):
        body = obj if isinstance(obj, bytes) else json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except Exception:
            pass

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n) if n else b""
        try:
            return json.loads(raw) if raw else {}
        except Exception:
            return {}

    def do_GET(self):
        p = self.path.split("?")[0]
        if p == "/_ping":
            return self._send(200, b"OK", "text/plain")
        if p == "/version":
            return self._send(200, {"Version": "24.0.7", "ApiVersion": "1.43",
                                    "KernelVersion": os.uname().release,
                                    "Os": "linux", "ID": SERVER_ID})
        if p == "/info":
            return self._send(200, {"ID": SERVER_ID, "Containers": len(STATE),
                                    "ServerVersion": "24.0.7"})
        if p == "/containers/json":
            with LOCK:
                return self._send(200, [{"Id": k, "Image": v["Image"], "Status": "running"}
                                        for k, v in STATE.items()])
        m = re.match(r"^/containers/([^/]+)/logs$", p)
        if m:
            c = STATE.get(m.group(1))
            if not c:
                return self._send(404, {"message": "No such container"})
            return self._send(200, c.get("out", "").encode(),
                              "application/vnd.docker.raw-stream")
        return self._send(404, {"message": "page not found"})

    def do_POST(self):
        p = self.path.split("?")[0]
        body = self._body()
        if p == "/containers/create":
            try:
                binds = [normalize_bind(b) for b in (body.get("Binds") or [])]
                prog, args = parse_cmd(body.get("Cmd") or ["id"])
            except BadRequest as e:
                return self._send(400, {"message": str(e)})
            cid = uuid.uuid4().hex[:12]
            with LOCK:
                STATE[cid] = {"Id": cid, "Image": body.get("Image", "alpine"),
                              "Prog": prog, "Args": args, "Binds": binds,
                              "Privileged": bool(body.get("Privileged", False)),
                              "Created": now(), "out": "", "rc": 0}
            return self._send(201, {"Id": cid, "Warnings": []})
        m = re.match(r"^/containers/([^/]+)/start$", p)
        if m:
            c = STATE.get(m.group(1))
            if not c:
                return self._send(404, {"message": "No such container"})
            c["out"], c["rc"] = self._run(c)
            return self._send(204, {})
        m = re.match(r"^/containers/([^/]+)/wait$", p)
        if m:
            c = STATE.get(m.group(1))
            return self._send(200, {"StatusCode": c.get("rc", 0) if c else 0})
        return self._send(404, {"message": "page not found"})

    def do_DELETE(self):
        m = re.match(r"^/containers/([^/]+)$", self.path.split("?")[0])
        if m:
            with LOCK:
                STATE.pop(m.group(1), None)
            return self._send(204, {})
        return self._send(404, {"message": "page not found"})

    def _run(self, c):
        out = []
        for real, dst in c.get("Binds", []):
            out.append("[sim] bind %s -> %s (read-only host root view)\n" % (real, "/" + dst.strip("/")))
        if c.get("Privileged"):
            out.append("[sim] privileged requested; this endpoint is read-only, no effect\n")
        prog, args = c.get("Prog"), c.get("Args") or []
        try:
            if prog in ("id", "whoami"):
                out.append("uid=0(root) gid=0(root) groups=0(root)\n" if prog == "id" else "root\n")
            elif prog == "uname":
                out.append("Linux\n")
            elif prog in ("cat", "ls"):
                if not args:
                    raise BadRequest("missing path")
                real = translate(args[0], c.get("Binds", []))
                if real is None:
                    out.append("%s: %s: No such file or directory\n" % (prog, args[0]))
                    return "".join(out)[:MAX_OUT], 1
                real = inside_hostview(real)
                if real is None:
                    out.append("%s: %s: Permission denied (outside container rootfs)\n" % (prog, args[0]))
                    return "".join(out)[:MAX_OUT], 1
                if prog == "cat":
                    if os.path.isdir(real):
                        out.append("cat: %s: Is a directory\n" % args[0])
                        return "".join(out)[:MAX_OUT], 1
                    with open(real, "rb") as f:
                        out.append(f.read(MAX_OUT).decode("utf-8", "replace"))
                else:
                    out.append("\n".join(sorted(os.listdir(real))) + "\n")
        except FileNotFoundError:
            out.append("%s: not found\n" % args[0])
            return "".join(out)[:MAX_OUT], 1
        except PermissionError:
            out.append("Permission denied\n")
            return "".join(out)[:MAX_OUT], 1
        except IsADirectoryError:
            out.append("Is a directory\n")
            return "".join(out)[:MAX_OUT], 1
        except BadRequest as e:
            out.append("[sim] error: %s\n" % e)
            return "".join(out)[:MAX_OUT], 1
        except Exception as e:
            out.append("[sim] error: %s\n" % e)
            return "".join(out)[:MAX_OUT], 1
        return "".join(out)[:MAX_OUT], 0


class Server(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True
    allow_reuse_address = True


def main():
    try:
        os.unlink(SOCK)
    except FileNotFoundError:
        pass
    srv = Server(SOCK, Handler)
    os.chmod(SOCK, 0o666)
    print("[dockerd-sim] listening on %s (read-only policy)" % SOCK, flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()

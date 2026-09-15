#!/usr/bin/env python3
"""Driver for renderdoc-mcp stdio server.

Sends one JSON line per request; reads one JSON line per response.
"""
import json
import subprocess
import sys
import time

MCP = r"I:\GitHubProject\renderdoc\renderdoc-mcp-cpp\bin\renderdoc-mcp.exe"


class MCPClient:
    def __init__(self, mcp_path=MCP):
        self.proc = subprocess.Popen(
            [mcp_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
        )
        self._next_id = 1
        self._init()

    def _init(self):
        r = self.request(
            "initialize",
            {"protocolVersion": "2025-03-26",
             "capabilities": {},
             "clientInfo": {"name": "dsh-driver", "version": "1.0"}},
            notify_first=False,
        )
        # send initialized notification
        self.send_notification("notifications/initialized")
        return r

    def send_notification(self, method):
        msg = {"jsonrpc": "2.0", "method": method}
        self._write(msg)

    def request(self, method, params=None, notify_first=True):
        mid = self._next_id
        self._next_id += 1
        msg = {"jsonrpc": "2.0", "id": mid, "method": method}
        if params is not None:
            msg["params"] = params
        self._write(msg)
        # read lines until we get our id
        while True:
            line = self._read()
            if line is None:
                raise RuntimeError("server closed")
            obj = json.loads(line)
            if obj.get("id") == mid:
                return obj

    def tools_call(self, name, arguments=None):
        if arguments is None:
            arguments = {}
        resp = self.request("tools/call", {"name": name, "arguments": arguments})
        if "error" in resp:
            raise RuntimeError(f"RPC error: {resp['error']}")
        result = resp.get("result", {})
        if result.get("isError"):
            content = result.get("content", [])
            text = "\n".join(c.get("text", "") for c in content if c.get("type") == "text")
            raise RuntimeError(f"tool error: {text}")
        content = result.get("content", [])
        text = "\n".join(c.get("text", "") for c in content if c.get("type") == "text")
        if text.strip():
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return text
        return result

    def _write(self, msg):
        data = (json.dumps(msg) + "\n").encode("utf-8")
        self.proc.stdin.write(data)
        self.proc.stdin.flush()

    def _read(self):
        line = self.proc.stdout.readline()
        if not line:
            return None
        return line.decode("utf-8").strip()

    def close(self):
        try:
            self.request("shutdown", notify_first=False)
        except Exception:
            pass
        self.proc.kill()


def main():
    c = MCPClient()
    try:
        method = sys.argv[1]
        if method == "list-tools":
            r = c.request("tools/list")
            for t in r["result"]["tools"]:
                print(t["name"])
        else:
            raise SystemExit(f"unknown method {method}")
    finally:
        c.close()


if __name__ == "__main__":
    main()

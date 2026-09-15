#!/usr/bin/env python3
"""Get shader disassembly/reflection at an event (no type param)."""
import json
import sys

from rdc_mcp import MCPClient


def main():
    cap = sys.argv[1]
    eid = int(sys.argv[2])
    stage = sys.argv[3] if len(sys.argv) > 3 else "vs"
    c = MCPClient()
    try:
        print("[open]", c.tools_call("open_capture", {"path": cap}))
        r = c.tools_call("get_shader", {"eventId": eid, "stage": stage})
        s = json.dumps(r, ensure_ascii=False)
        print(s[:6000])
    finally:
        c.close()


if __name__ == "__main__":
    main()

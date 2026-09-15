#!/usr/bin/env python3
"""Dump a specific variable's values from a cbuffer in a capture."""
import json
import sys

from rdc_mcp import MCPClient


def main():
    cap = sys.argv[1]
    eid = int(sys.argv[2])
    stage = sys.argv[3]
    index = int(sys.argv[4])
    names = sys.argv[5:]
    c = MCPClient()
    try:
        print("[open]", c.tools_call("open_capture", {"path": cap}))
        r = c.tools_call("get_cbuffer_contents",
                         {"stage": stage, "index": index, "eventId": eid})
        for v in r.get("variables", []):
            if not names or v["name"] in names:
                vals = v.get("floatValues") or v.get("intValues") or v.get("uintValues")
                print(f"{v['name']}: {vals}")
    finally:
        c.close()


if __name__ == "__main__":
    main()

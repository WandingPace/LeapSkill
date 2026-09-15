#!/usr/bin/env python3
"""Export render target at an event."""
import sys

from rdc_mcp import MCPClient


def main():
    cap = sys.argv[1]
    eid = int(sys.argv[2])
    outdir = sys.argv[3]
    idx = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    c = MCPClient()
    try:
        print("[open]", c.tools_call("open_capture", {"path": cap}))
        c.tools_call("goto_event", {"eventId": eid})
        r = c.tools_call("export_render_target", {"index": idx})
        print(r)
    finally:
        c.close()


if __name__ == "__main__":
    main()

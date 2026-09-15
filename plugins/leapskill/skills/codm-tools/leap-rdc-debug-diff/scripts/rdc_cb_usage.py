#!/usr/bin/env python3
"""Map cbuffer variable (reflection order) to actual register usage by
finding which register indices the PS disassembly actually reads.
"""
import re
import sys

from rdc_mcp import MCPClient


def main():
    cap = sys.argv[1]
    eid = int(sys.argv[2])
    stage = sys.argv[3] if len(sys.argv) > 3 else "ps"
    c = MCPClient()
    try:
        print("[open]", c.tools_call("open_capture", {"path": cap}))
        r = c.tools_call("get_shader", {"eventId": eid, "stage": stage})
        dis = r.get("disassembly", "")
        # find all cbN[idx] uses
        uses = {}
        for m in re.finditer(r"cb(\d+)\[(\d+)\]", dis):
            cb = int(m.group(1))
            idx = int(m.group(2))
            uses.setdefault(cb, set()).add(idx)
        for cb in sorted(uses):
            idxs = sorted(uses[cb])
            print(f"cbuffer{cb}: uses {len(idxs)} registers: {idxs}")
            print("  min..max:", min(idxs), "..", max(idxs))
    finally:
        c.close()


if __name__ == "__main__":
    main()

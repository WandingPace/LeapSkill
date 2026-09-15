#!/usr/bin/env python3
"""Map shader usage across draws in a capture."""
import json
import sys

from rdc_mcp import MCPClient


def main():
    cap = sys.argv[1]
    stage = sys.argv[2] if len(sys.argv) > 2 else "vs"
    c = MCPClient()
    try:
        print("[open]", c.tools_call("open_capture", {"path": cap}))
        draws = c.tools_call("list_draws", {}).get("draws", [])
        # Group draws by shader
        groups = {}
        for d in draws:
            eid = d.get("eventId")
            if not eid:
                continue
            try:
                sh = c.tools_call("get_shader", {"eventId": eid, "stage": stage})
                rid = sh.get("resourceId")
            except Exception:
                rid = None
            groups.setdefault(rid, []).append(eid)
        print(f"total draws: {len(draws)}, distinct {stage} shaders: {len(groups)}")
        for rid, eids in sorted(groups.items(), key=lambda kv: (kv[0] is None, len(kv[1])), reverse=True):
            print(f"  {rid}: {len(eids)} draws -> {eids[:12]}{'...' if len(eids)>12 else ''}")
    finally:
        c.close()


if __name__ == "__main__":
    main()

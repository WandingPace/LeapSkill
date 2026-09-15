#!/usr/bin/env python3
"""Find draws using a given shader resourceId in a capture and compare with another."""
import json
import sys

from rdc_mcp import MCPClient


def main():
    capA = sys.argv[1]
    shader_id = sys.argv[2]
    capB = sys.argv[3]
    cA = MCPClient()
    cB = MCPClient()
    try:
        print("[openA]", cA.tools_call("open_capture", {"path": capA}))
        print("[openB]", cB.tools_call("open_capture", {"path": capB}))
        drawsA = cA.tools_call("list_draws", {}).get("draws", [])
        drawsB = cB.tools_call("list_draws", {}).get("draws", [])
        # collect draws in A using the shader
        eidsA = []
        for d in drawsA:
            eid = d.get("eventId")
            if not eid:
                continue
            try:
                sh = cA.tools_call("get_shader", {"eventId": eid, "stage": "vs"})
                if sh.get("resourceId") == shader_id:
                    eidsA.append(eid)
            except Exception:
                pass
        eidsB = []
        for d in drawsB:
            eid = d.get("eventId")
            if not eid:
                continue
            try:
                sh = cB.tools_call("get_shader", {"eventId": eid, "stage": "vs"})
                if sh.get("resourceId") == shader_id:
                    eidsB.append(eid)
            except Exception:
                pass
        print(f"A draws with {shader_id}: {len(eidsA)} -> {eidsA[:20]}")
        print(f"B draws with {shader_id}: {len(eidsB)} -> {eidsB[:20]}")
    finally:
        cA.close()
        cB.close()


if __name__ == "__main__":
    main()

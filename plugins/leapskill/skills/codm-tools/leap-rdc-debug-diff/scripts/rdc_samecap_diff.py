#!/usr/bin/env python3
"""Compare cbuffers between two events in the SAME capture."""
import json
import sys

from rdc_mcp import MCPClient


def get_cb(c, stage, index, eid):
    return c.tools_call("get_cbuffer_contents",
                        {"stage": stage, "index": index, "eventId": eid})


def flatten(vars_, prefix=""):
    out = []
    for v in vars_:
        name = f"{prefix}.{v['name']}" if prefix else v["name"]
        if v.get("members"):
            out.extend(flatten(v["members"], name))
            continue
        vals = None
        for k in ("floatValues", "intValues", "uintValues", "values"):
            if k in v and v.get(k):
                vals = list(v[k])
                break
        out.append({"name": name, "values": vals})
    return out


def main():
    cap = sys.argv[1]
    eidA = int(sys.argv[2])
    eidB = int(sys.argv[3])
    stages = sys.argv[4].split(",") if len(sys.argv) > 4 else ["vs", "ps"]
    c = MCPClient()
    try:
        print("[open]", c.tools_call("open_capture", {"path": cap}))
        for stage in stages:
            la = c.tools_call("list_cbuffers", {"stage": stage, "eventId": eidA})
            lb = c.tools_call("list_cbuffers", {"stage": stage, "eventId": eidB})
            print(f"\n##### {stage} #####")
            for b in la.get("cbuffers", []):
                idx = b["index"]
                ca = get_cb(c, stage, idx, eidA)
                cb = get_cb(c, stage, idx, eidB)
                fa = {v["name"]: v for v in flatten(ca.get("variables", []))}
                fb = {v["name"]: v for v in flatten(cb.get("variables", []))}
                diffs = []
                for name in sorted(set(fa) | set(fb)):
                    if name not in fa or name not in fb:
                        diffs.append((name, fa.get(name, {}).get("values"), fb.get(name, {}).get("values")))
                    elif fa[name]["values"] != fb[name]["values"]:
                        diffs.append((name, fa[name]["values"], fb[name]["values"]))
                if diffs:
                    print(f"  cbuffer{idx} ({b.get('name')}): {len(diffs)} diffs")
                    for name, va, vb in diffs[:30]:
                        print(f"    {name}")
                        if va is not None: print(f"      A={va}")
                        if vb is not None: print(f"      B={vb}")
                else:
                    print(f"  cbuffer{idx} ({b.get('name')}): identical")
    finally:
        c.close()


if __name__ == "__main__":
    main()

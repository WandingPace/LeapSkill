#!/usr/bin/env python3
"""Compare cbuffer variable values between two captures at matching events.

Usage:
  python rdc_cbuffer_diff.py <capE> <eidE> <capC> <eidC> [--stage vs,ps] [--tol T] [--json out.json]
"""
import json
import sys

from rdc_mcp import MCPClient

TOL = 1e-4


def open_capture(c, path):
    return c.tools_call("open_capture", {"path": path})


def list_cb(c, stage, eid):
    return c.tools_call("list_cbuffers", {"stage": stage, "eventId": eid})


def get_cb(c, stage, index, eid):
    return c.tools_call("get_cbuffer_contents",
                        {"stage": stage, "index": index, "eventId": eid})


def flatten(vars_, prefix=""):
    out = []
    for v in vars_:
        name = f"{prefix}.{v['name']}" if prefix else v["name"]
        t = v.get("type", "")
        if v.get("members"):
            out.extend(flatten(v["members"], name))
            continue
        vals = None
        for k in ("floatValues", "intValues", "uintValues", "values"):
            if k in v and v.get(k):
                vals = list(v[k])
                break
        out.append({"name": name, "type": t, "values": vals})
    return out


def num_diff(a, b):
    if a is None or b is None:
        return True
    if len(a) != len(b):
        return True
    return any(abs(float(x) - float(y)) > TOL for x, y in zip(a, b))


def collect(c, cap, eid, stages):
    open_capture(c, cap)
    result = {}
    for stage in stages:
        blocks = list_cb(c, stage, eid)
        result[stage] = {}
        if blocks is None:
            result[stage]["error"] = "list failed"
            continue
        for b in blocks.get("cbuffers", []):
            idx = b["index"]
            contents = get_cb(c, stage, idx, eid)
            if contents is None:
                result[stage][idx] = {"name": b.get("name"), "error": "contents failed"}
                continue
            result[stage][idx] = {
                "name": b.get("name"),
                "byteSize": contents.get("byteSize"),
                "vars": flatten(contents.get("variables", [])),
            }
    return result


def main():
    global TOL
    capE, eidE, capC, eidC = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
    stages = ["vs", "ps"]
    json_out = None
    for i, a in enumerate(sys.argv):
        if a == "--stage" and i + 1 < len(sys.argv):
            stages = sys.argv[i + 1].split(",")
        if a == "--json" and i + 1 < len(sys.argv):
            json_out = sys.argv[i + 1]
        if a == "--tol" and i + 1 < len(sys.argv):
            TOL = float(sys.argv[i + 1])

    c = MCPClient()
    e = collect(c, capE, eidE, stages)
    c.close()
    c = MCPClient()
    cc = collect(c, capC, eidC, stages)
    c.close()

    report = {"captureE": capE, "eidE": eidE, "captureC": capC, "eidC": eidC,
              "tol": TOL, "stages": {}}
    n_diff = 0
    for stage in stages:
        if stage not in e or stage not in cc:
            continue
        blkE = e[stage]
        blkC = cc[stage]
        print(f"\n########## STAGE {stage} ##########")
        for idx in sorted(set(blkE) | set(blkC)):
            be = blkE.get(idx)
            bc = blkC.get(idx)
            if be is None or bc is None:
                print(f"  [cbuffer {idx}] MISSING in {'C' if be is None else 'E'}")
                continue
            print(f"\n-- {be['name']} (E={be.get('byteSize')}B C={bc.get('byteSize')}B) "
                  f"at {stage}[{idx}] --")
            ve = {v["name"]: v for v in be["vars"]}
            vc = {v["name"]: v for v in bc["vars"]}
            block_diff = 0
            for name in sorted(set(ve) | set(vc)):
                if name not in ve or name not in vc:
                    print(f"  {name}: MISSING in {'C' if name not in ve else 'E'}")
                    block_diff += 1
                    continue
                if num_diff(ve[name]["values"], vc[name]["values"]):
                    print(f"  {name}  E={ve[name]['values']}")
                    print(f"             C={vc[name]['values']}")
                    block_diff += 1
            if block_diff == 0:
                print("  (identical)")
            n_diff += block_diff
            report.setdefault("stages", {}).setdefault(stage, {})[idx] = {
                "name": be["name"], "diffVars": block_diff}

    print(f"\n===== TOTAL differing variables: {n_diff} =====")
    report["totalDiffVars"] = n_diff
    if json_out:
        with open(json_out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"[json] {json_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

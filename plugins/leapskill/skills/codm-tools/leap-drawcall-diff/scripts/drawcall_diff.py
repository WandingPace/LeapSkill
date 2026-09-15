#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODM DrawCallRecord 差异对比器
对比两个 DrawCallRecord_*.json，聚焦 mesh 渲染差异，默认忽略相机相关的 VP/投影矩阵等噪音。
仅使用标准库，无第三方依赖。
"""
import argparse
import json
import sys
from collections import Counter, OrderedDict

# ---------------------------------------------------------------------------
# 相机相关属性忽略规则
# ---------------------------------------------------------------------------
# 这些 key（不区分大小写子串匹配）在默认模式下不参与对比：
#  - VP/V/P 矩阵、投影矩阵、modelview 矩阵
#  - 相机位置/平面/正交参数
#  - 阴影相机（light shadow map）的 WorldToShadow VP 矩阵
CAMERA_RELATED_SUBSTRINGS = (
    "matrixvp", "matrixv", "matrixp", "matrixinvv", "matrixinvp",
    "cameraprojection", "camerainvprojection", "cameraworldclipplanes",
    "glstate_matrix_projection", "glstate_matrix_modelview0",
    "glstate_matrix_inv_trans_modelview0", "glstate_matrix_transpose_modelview0",
    "worldtoshadow", "stereomatrix", "stereocamera",
    "_worldspacecamerapos", "unity_orthoparams", "unity_frustumplanes",
    "unity_matrixmvp",
)

# mesh 类事件：参与 mesh 渲染差异对比
MESH_EVENT_TYPES = ("Mesh", "DynamicGeometry")


def is_camera_related(key, ignore_shadow=True):
    k = key.lower()
    for sub in CAMERA_RELATED_SUBSTRINGS:
        if not ignore_shadow and "worldtoshadow" in sub:
            continue
        if sub in k:
            return True
    return False


def load_records(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    records = []
    for frame in data.get("frames", []):
        fi = frame.get("frameIndex")
        for dc in frame.get("drawCalls", []):
            records.append((fi, dc))
    return data, records


def filter_mesh(records):
    return [(fi, dc) for fi, dc in records if dc.get("eventType") in MESH_EVENT_TYPES]


def norm_dict(d, ignore_shadow=True):
    """把属性 dict 归一化为可比较的 (key -> 规范值)，跳过相机相关项。"""
    out = OrderedDict()
    if not isinstance(d, dict):
        return out
    for k in sorted(d.keys()):
        if is_camera_related(k, ignore_shadow):
            continue
        out[k] = json.dumps(d[k], sort_keys=True, ensure_ascii=False)
    return out


def render_target_sig(dc):
    """渲染目标签名：color RTs + depth RT。"""
    crt = dc.get("colorRenderTargets") or []
    drt = dc.get("depthRenderTarget") or {}
    parts = []
    for rt in crt:
        parts.append("{name}:{w}x{h}:{format}:{dim}:{samples}".format(
            name=rt.get("name"), w=rt.get("width"), h=rt.get("height"),
            format=rt.get("format"), dim=rt.get("dimension"), samples=rt.get("samples")))
    if drt:
        parts.append("D:" + "{name}:{w}x{h}:{format}".format(
            name=drt.get("name"), w=drt.get("width"), h=drt.get("height"),
            format=drt.get("format")))
    return " | ".join(parts)


def group_key(dc):
    """mesh 渲染身份键：pass + mesh + shader + subset + passIndex。"""
    return (
        dc.get("eventName", ""),
        dc.get("meshName", ""),
        dc.get("shaderName", ""),
        dc.get("meshSubset", 0),
        dc.get("shaderPassIndex", 0),
    )


def build_groups(records):
    """按 group_key 聚合；返回 OrderedDict[key -> list of dc]，保持首次出现顺序。"""
    groups = OrderedDict()
    for _fi, dc in records:
        k = group_key(dc)
        groups.setdefault(k, []).append(dc)
    return groups


def scalar_changes(dcA, dcB, ignore_shadow=True):
    """比较单个 draw call 的标量字段，返回变化列表。"""
    fields = ("shaderName", "shaderKeywords", "batchBreakCause",
              "vertexCount", "indexCount", "triangleCount", "instanceCount",
              "meshSubset", "shaderPassIndex")
    diffs = []
    for f in fields:
        va, vb = dcA.get(f), dcB.get(f)
        if va != vb:
            diffs.append((f, va, vb))
    return diffs


def dict_changes(dcA, dcB, ignore_shadow=True):
    """比较 float/vector/matrix 属性，返回 (key, 旧值, 新值) 列表，跳过相机相关。"""
    out = []
    for section in ("floatProperties", "vectorProperties", "matrixProperties"):
        a = norm_dict(dcA.get(section), ignore_shadow)
        b = norm_dict(dcB.get(section), ignore_shadow)
        for k in sorted(set(a) | set(b)):
            va, vb = a.get(k, "<missing>"), b.get(k, "<missing>")
            if va != vb:
                out.append((k, va, vb, section))
    # 纹理
    ta = dcA.get("textureProperties") or {}
    tb = dcB.get("textureProperties") or {}
    for k in sorted(set(ta) | set(tb)):
        if ta.get(k) != tb.get(k):
            out.append((k, ta.get(k, "<missing>"), tb.get(k, "<missing>"), "textureProperties"))
    # 渲染目标
    if render_target_sig(dcA) != render_target_sig(dcB):
        out.append(("__renderTarget__", render_target_sig(dcA), render_target_sig(dcB), "renderTarget"))
    return out


def summarize(data, records, path):
    mesh = filter_mesh(records)
    evt = Counter(dc.get("eventType") for _fi, dc in records)
    passes = Counter(dc.get("eventName") for _fi, dc in mesh)
    tris = sum(dc.get("triangleCount", 0) for _fi, dc in mesh)
    lines = []
    lines.append("File: {}".format(path))
    lines.append("  exportTime      : {}".format(data.get("exportTime")))
    lines.append("  totalFrames     : {}".format(data.get("totalFrames")))
    lines.append("  totalDrawCalls  : {}".format(data.get("totalDrawCalls")))
    lines.append("  eventTypes      : {}".format(dict(evt)))
    lines.append("  mesh events     : {} (triangles={})".format(len(mesh), tris))
    lines.append("  unique passes   : {}".format(len(passes)))
    return "\n".join(lines)


def diff(recordsA, recordsB, ignore_shadow=True):
    meshA, meshB = filter_mesh(recordsA), filter_mesh(recordsB)
    groupsA, groupsB = build_groups(meshA), build_groups(meshB)

    result = {
        "summary": {
            "meshEventsA": len(meshA),
            "meshEventsB": len(meshB),
            "trisA": sum(dc.get("triangleCount", 0) for _f, dc in meshA),
            "trisB": sum(dc.get("triangleCount", 0) for _f, dc in meshB),
        },
        "passes": [],
        "added": [],
        "removed": [],
        "changed": [],
    }

    # 按 pass 统计 draw 数量变化
    passA = Counter(dc.get("eventName") for _f, dc in meshA)
    passB = Counter(dc.get("eventName") for _f, dc in meshB)
    for p in sorted(set(passA) | set(passB)):
        ca, cb = passA.get(p, 0), passB.get(p, 0)
        if ca != cb:
            result["passes"].append({"pass": p, "drawCallsA": ca, "drawCallsB": cb, "delta": cb - ca})

    keys = sorted(set(groupsA) | set(groupsB))
    for k in keys:
        gA, gB = groupsA.get(k, []), groupsB.get(k, [])
        base = {
            "pass": k[0], "meshName": k[1], "shaderName": k[2],
            "meshSubset": k[3], "shaderPassIndex": k[4],
        }
        if not gA:
            # 新增
            result["added"].append(dict(base, drawCalls=len(gB),
                                        triangles=sum(dc.get("triangleCount", 0) for dc in gB),
                                        renderer=gB[0].get("rendererName")))
        elif not gB:
            # 移除
            result["removed"].append(dict(base, drawCalls=len(gA),
                                          triangles=sum(dc.get("triangleCount", 0) for dc in gA),
                                          renderer=gA[0].get("rendererName")))
        else:
            # 都存在：对比次数、三角形、标量字段、属性
            entry = dict(base, drawCallsA=len(gA), drawCallsB=len(gB),
                         trisA=sum(dc.get("triangleCount", 0) for dc in gA),
                         trisB=sum(dc.get("triangleCount", 0) for dc in gB),
                         rendererA=gA[0].get("rendererName"),
                         rendererB=gB[0].get("rendererName"),
                         fieldChanges=[], propChanges=[])
            dcA, dcB = gA[0], gB[0]
            for f, va, vb in scalar_changes(dcA, dcB, ignore_shadow):
                entry["fieldChanges"].append({"field": f, "a": va, "b": vb})
            for kk, va, vb, sec in dict_changes(dcA, dcB, ignore_shadow):
                entry["propChanges"].append({"key": kk, "section": sec, "a": va, "b": vb})
            if entry["fieldChanges"] or entry["propChanges"] or len(gA) != len(gB):
                result["changed"].append(entry)

    # 排序：三角形变化大的排前面
    def tri_delta(e):
        return abs(e.get("trisB", 0) - e.get("trisA", 0))
    result["added"].sort(key=lambda e: -e["triangles"])
    result["removed"].sort(key=lambda e: -e["triangles"])
    result["changed"].sort(key=lambda e: -(abs(e["trisB"] - e["trisA"]) + len(e["propChanges"])))
    return result


def render_report(res, args):
    L = []
    s = res["summary"]
    L.append("=== Mesh 渲染差异报告 ===")
    L.append("mesh 事件数  : A={}  B={}  (delta {})".format(
        s["meshEventsA"], s["meshEventsB"], s["meshEventsB"] - s["meshEventsA"]))
    L.append("三角形总数  : A={}  B={}  (delta {})".format(
        s["trisA"], s["trisB"], s["trisB"] - s["trisA"]))
    L.append("")

    if res["passes"]:
        L.append("-- 按 pass 的 draw call 数量变化 --")
        for p in res["passes"]:
            L.append("  {delta:+d}  {pass}  (A={drawCallsA}, B={drawCallsB})".format(**p))
        L.append("")

    if res["removed"]:
        L.append("-- 被移除的 mesh ({} 个) --".format(len(res["removed"])))
        for e in res["removed"][:args.top]:
            L.append("  [-] {meshName}  <{shaderName}>  pass={pass}  draws={drawCalls} tris={triangles} renderer={renderer}".format(**e))
        if len(res["removed"]) > args.top:
            L.append("  ... 其余 {} 个未显示 (--top 调整)".format(len(res["removed"]) - args.top))
        L.append("")

    if res["added"]:
        L.append("-- 新增的 mesh ({} 个) --".format(len(res["added"])))
        for e in res["added"][:args.top]:
            L.append("  [+] {meshName}  <{shaderName}>  pass={pass}  draws={drawCalls} tris={triangles} renderer={renderer}".format(**e))
        if len(res["added"]) > args.top:
            L.append("  ... 其余 {} 个未显示 (--top 调整)".format(len(res["added"]) - args.top))
        L.append("")

    if res["changed"]:
        L.append("-- 变化的 mesh ({} 个) --".format(len(res["changed"])))
        for e in res["changed"][:args.top]:
            L.append("  [~] {meshName}  <{shaderName}>  pass={pass}  draws {drawCallsA}->{drawCallsB} tris {trisA}->{trisB}".format(**e))
            if e.get("rendererA") != e.get("rendererB"):
                L.append("      renderer: {rendererA} -> {rendererB}".format(**e))
            for fc in e["fieldChanges"]:
                L.append("      {field}: {a} -> {b}".format(**fc))
            for pc in e["propChanges"][:args.detail]:
                a = pc["a"] if len(pc["a"]) <= 80 else pc["a"][:77] + "..."
                b = pc["b"] if len(pc["b"]) <= 80 else pc["b"][:77] + "..."
                L.append("      [{section}] {key}: {a} -> {b}".format(
                    section=pc["section"], key=pc["key"], a=a, b=b))
            if len(e["propChanges"]) > args.detail:
                L.append("      ... 其余 {} 个属性变化未显示 (--detail 调整)".format(
                    len(e["propChanges"]) - args.detail))
            L.append("")
        if len(res["changed"]) > args.top:
            L.append("  ... 其余 {} 个未显示 (--top 调整)".format(len(res["changed"]) - args.top))

    if not res["passes"] and not res["removed"] and not res["added"] and not res["changed"]:
        L.append("未发现 mesh 渲染差异（相机相关属性已忽略）。")
    return "\n".join(L)


def _force_utf8_stdio():
    """确保 stdout/stderr 输出 UTF-8；避免中文在 GBK 控制台下乱码。"""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def main():
    _force_utf8_stdio()
    ap = argparse.ArgumentParser(description="对比两个 CODM DrawCallRecord JSON 的 mesh 渲染差异")
    ap.add_argument("file_a", help="基准 JSON 路径")
    ap.add_argument("file_b", help="对比 JSON 路径")
    ap.add_argument("--summary", action="store_true", help="只打印两份文件摘要")
    ap.add_argument("--pass", dest="pass_filter", default=None, help="只对比该 pass（eventName 子串匹配）")
    ap.add_argument("--mesh", dest="mesh_filter", default=None, help="只对比该 mesh（meshName/rendererName 子串匹配）")
    ap.add_argument("--top", type=int, default=30, help="报告中最多的 mesh 条目数 (默认 30)")
    ap.add_argument("--detail", type=int, default=12, help="每个 mesh 最多显示属性变化条数 (默认 12)")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出完整差异结果")
    ap.add_argument("--include-camera", action="store_true", help="也对比相机/VP 相关属性（默认忽略）")
    ap.add_argument("--include-shadow", action="store_true", help="也对比阴影 WorldToShadow 矩阵（默认忽略）")
    args = ap.parse_args()

    dataA, recA = load_records(args.file_a)
    dataB, recB = load_records(args.file_b)

    if args.summary:
        print(summarize(dataA, recA, args.file_a))
        print()
        print(summarize(dataB, recB, args.file_b))
        return

    ignore_shadow = not args.include_shadow

    # 过滤
    if args.pass_filter:
        recA = [(f, dc) for f, dc in recA if args.pass_filter in dc.get("eventName", "")]
        recB = [(f, dc) for f, dc in recB if args.pass_filter in dc.get("eventName", "")]
    if args.mesh_filter:
        def mf(dc):
            return args.mesh_filter in dc.get("meshName", "") or args.mesh_filter in dc.get("rendererName", "")
        recA = [(f, dc) for f, dc in recA if mf(dc)]
        recB = [(f, dc) for f, dc in recB if mf(dc)]

    res = diff(recA, recB, ignore_shadow)

    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(render_report(res, args))


if __name__ == "__main__":
    main()

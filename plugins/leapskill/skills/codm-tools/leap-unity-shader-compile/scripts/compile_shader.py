#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compile one Unity shader variant through UnityShaderCompiler.exe."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from usc_protocol import (
    GPU_SPIRV,
    PLATFORM_IDS,
    PROGRAM_FRAGMENT,
    PROGRAM_VERTEX,
    CompileResult,
    ProtocolError,
    UnityShaderCompiler,
)


DEFAULT_CODM_ROOT = os.environ.get("CODM_ROOT", r"I:\CODMCHN")
DEFAULT_COMPILER = os.environ.get(
    "UNITY_SHADER_COMPILER",
    r"G:\CODM_CHN\Engine\Unity564p4_Win64_Bin_QTS\WinUnity\Data\Tools64\UnityShaderCompiler.exe",
)
DEFAULT_DATA = os.environ.get(
    "UNITY_SHADER_DATA",
    r"G:\CODM_CHN\Engine\Unity564p4_Win64_Bin_QTS\WinUnity\Data",
)
DEFAULT_PLATFORMS = ("vulkan", "gles3", "d3d11")

OPEN_AFTER_COMPILE = (
    "metrics.json",
    "vulkan.disasm",
    "gles3.disasm",
    "d3d11.fs.disasm",
    "d3d11.vs.disasm",
)

SHADER_NAME_RE = re.compile(r'^\s*Shader\s+"([^"]+)"', re.MULTILINE)
LIGHTMODE_PASS = {
    "forwardbase": "UNITY_PASS_FORWARDBASE",
    "forwardadd": "UNITY_PASS_FORWARDADD",
    "shadowcaster": "UNITY_PASS_SHADOWCASTER",
    "meta": "UNITY_PASS_META",
    "deferred": "UNITY_PASS_DEFERRED",
    "prepassbase": "UNITY_PASS_PREPASSBASE",
    "prepassfinal": "UNITY_PASS_PREPASSFINAL",
}
COMMENT_LINE_RE = re.compile(r"//.*?$", re.MULTILINE)
BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)


def die(msg, code=1):
    sys.stderr.write(msg.rstrip() + "\n")
    sys.exit(code)


def strip_comments(text):
    text = BLOCK_COMMENT_RE.sub("", text)
    return COMMENT_LINE_RE.sub("", text)


def default_include_folders(codm_root, shader_dir, data_dir):
    folders = [
        shader_dir,
        codm_root,
        os.path.join(codm_root, "Assets", "Shaders", "Includes"),
        os.path.join(codm_root, "Assets", "Shaders"),
        os.path.join(data_dir, "CGIncludes"),
    ]
    out = []
    seen = set()
    for folder in folders:
        norm = os.path.normpath(folder)
        key = norm.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(norm)
    return out


def looks_like_shader_path(value):
    text = (value or "").strip().strip('"').strip("'")
    if not text:
        return False
    lowered = text.lower().replace("\\", "/")
    if lowered.endswith(".shader"):
        return True
    if os.path.isabs(text) or "/" in text or "\\" in text:
        return True
    if lowered.startswith("assets/"):
        return True
    return False


def candidate_shader_paths(codm_root, shader_arg):
    raw = (shader_arg or "").strip().strip('"').strip("'")
    if not raw:
        return []
    paths = []
    seen = set()

    def add(path):
        if not path:
            return
        abs_path = os.path.abspath(os.path.normpath(path))
        key = os.path.normcase(abs_path)
        if key in seen:
            return
        seen.add(key)
        paths.append(abs_path)

    add(raw)
    if not os.path.isabs(raw):
        add(os.path.join(os.getcwd(), raw))
        add(os.path.join(codm_root, raw))
        posix = raw.replace("\\", "/")
        if posix.lower().startswith("assets/"):
            add(os.path.join(codm_root, posix.replace("/", os.sep)))
    return paths


def find_shader_file(codm_root, shader_arg):
    wanted = (shader_arg or "").strip().strip('"').strip("'")
    if looks_like_shader_path(wanted):
        for candidate in candidate_shader_paths(codm_root, wanted):
            if os.path.isfile(candidate):
                return candidate
        die("shader file not found: %s" % shader_arg)
    if os.path.isfile(wanted):
        return os.path.abspath(wanted)
    shaders_root = os.path.join(codm_root, "Assets", "Shaders")
    hits = []
    for root, _dirs, files in os.walk(shaders_root):
        for name in files:
            if not name.lower().endswith(".shader"):
                continue
            path = os.path.join(root, name)
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    head = f.read(4096)
            except OSError:
                continue
            m = SHADER_NAME_RE.search(head)
            if m and m.group(1) == wanted:
                hits.append(path)
    if not hits:
        die("shader not found by name %r under %s" % (wanted, shaders_root))
    if len(hits) > 1:
        die("multiple shaders named %r:\n  %s" % (wanted, "\n  ".join(hits)))
    return hits[0]


def parse_variant_text(text):
    lines = [ln.strip() for ln in text.replace("\r\n", "\n").split("\n") if ln.strip()]
    shader = None
    pass_index = None
    keywords = []
    if not lines:
        return shader, pass_index, keywords
    first = lines[0]
    m = re.search(r"^(.*?),\s*pass\s*#\s*(\d+)\s*$", first, re.IGNORECASE)
    if m:
        shader = m.group(1).strip().strip('"').strip("'")
        pass_index = int(m.group(2))
        if len(lines) > 1:
            keywords = lines[1].split()
        return shader, pass_index, keywords
    if looks_like_shader_path(first):
        shader = first.strip('"').strip("'")
        if len(lines) > 1:
            keywords = lines[1].split()
        return shader, pass_index, keywords
    if len(lines) == 1 and " " in first and not first.lower().endswith(".shader"):
        keywords = first.split()
        return shader, pass_index, keywords
    return shader, pass_index, keywords


def parse_passes(preprocessed_text):
    text = strip_comments(preprocessed_text)
    passes = []
    i = 0
    n = len(text)
    sub_index = -1
    current_lod = None
    pass_in_sub = -1
    while i < n:
        if text.startswith("SubShader", i) and (i == 0 or not text[i - 1].isalnum()) and not (i + 9 < n and text[i + 9].isalnum()):
            sub_index += 1
            pass_in_sub = -1
            current_lod = None
            i += 9
            continue
        if text.startswith("LOD", i) and (i == 0 or not text[i - 1].isalnum()) and i + 3 < n and text[i + 3].isspace():
            m = re.match(r"LOD\s+(\d+)", text[i:])
            if m:
                current_lod = int(m.group(1))
                i += m.end()
                continue
        if text.startswith("Pass", i) and (i == 0 or not text[i - 1].isalnum()) and (i + 4 >= n or not text[i + 4].isalnum()):
            brace = text.find("{", i)
            if brace < 0:
                break
            end = match_brace(text, brace)
            block = text[brace + 1:end]
            pass_in_sub += 1
            name_m = re.search(r'\bName\s+"([^"]+)"', block)
            lm_m = re.search(r'LightMode"?\s*=\s*"([^"]+)"', block)
            gid_m = re.search(r"GpuProgramID\s+(\d+)", block)
            passes.append({
                "subshader": sub_index if sub_index >= 0 else 0,
                "pass": pass_in_sub,
                "lod": current_lod,
                "name": name_m.group(1) if name_m else "",
                "light_mode": lm_m.group(1) if lm_m else "",
                "snippet_id": int(gid_m.group(1)) if gid_m else None,
            })
            i = end + 1
            continue
        i += 1
    return passes


def match_brace(text, open_index):
    depth = 0
    for i in range(open_index, len(text)):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i
    raise ValueError("unbalanced braces in shader")


def select_pass(passes, pass_index, lod):
    if not passes:
        die("preprocess produced no CGPROGRAM passes")
    if lod is not None:
        group = [p for p in passes if p["lod"] == lod]
        if not group:
            die("no SubShader with LOD %s" % lod)
    else:
        first_sub = passes[0]["subshader"]
        group = [p for p in passes if p["subshader"] == first_sub]
    if pass_index < 0 or pass_index >= len(group):
        die("pass #%s out of range (0..%s)" % (pass_index, len(group) - 1))
    chosen = group[pass_index]
    if chosen["snippet_id"] is None:
        die("pass #%s has no GpuProgramID" % pass_index)
    return chosen


def inject_defines(code, lod, light_mode):
    lines = []
    if lod is not None:
        lines.append("#define SHADERLOD_%s" % lod)
        lines.append("#define SHADERLOD %s" % lod)
    define_name = LIGHTMODE_PASS.get((light_mode or "").lower())
    if define_name and define_name not in code:
        lines.append("#define %s" % define_name)
    if not lines:
        return code
    return "\n".join(lines) + "\n" + code


def normalize_platforms(raw):
    names = []
    for item in raw.replace(";", ",").split(","):
        name = item.strip().lower()
        if not name:
            continue
        if name == "gles":
            name = "gles3"
        if name == "dx11":
            name = "d3d11"
        if name not in ("vulkan", "gles3", "d3d11"):
            die("unsupported platform %r (v1: vulkan, gles3, d3d11)" % name)
        if name not in names:
            names.append(name)
    if not names:
        names = list(DEFAULT_PLATFORMS)
    return names


def count_samples(platform, disasm):
    text = disasm or ""
    if platform == "vulkan":
        pats = ("ImageSampleImplicitLod", "ImageSampleExplicitLod", "ImageSampleProj", "ImageSampleDref")
        return sum(text.count(p) for p in pats)
    if platform == "gles3":
        return len(re.findall(r"\btexture(?:Lod|Proj|Grad|Offset)?\s*\(", text) + re.findall(r"\btexelFetch\s*\(", text))
    if platform == "d3d11":
        return len(re.findall(r"\bsample(?:_l|_b|_c|_d|_c_lz)?\b", text, re.IGNORECASE) + re.findall(r"\btexld[alp]?\b", text, re.IGNORECASE))
    return 0


def unique(seq):
    out = []
    seen = set()
    for item in seq:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def metrics_from_compile(platform, stage, compiled, disasm):
    alu = tex = flow = temp = None
    if compiled.stats:
        alu, tex, flow, temp = compiled.stats
    return {
        "platform": platform,
        "stage": stage,
        "ok": compiled.ok,
        "gpu_type": compiled.gpu_type,
        "blob_size": len(compiled.blob or b""),
        "alu": alu,
        "tex": tex,
        "flow": flow,
        "temp_register": temp,
        "sample_count": count_samples(platform, disasm),
        "texbinds": unique(compiled.texbinds),
        "cbuffers": compiled.cbs,
        "errors": [e.format() for e in compiled.errors],
    }


def print_metrics(item):
    stats = "ALU=%s TEX=%s flow=%s temp=%s" % (
        item.get("alu"), item.get("tex"), item.get("flow"), item.get("temp_register")
    )
    print("%s/%s  ok=%s  blob=%s  samples=%s  %s" % (
        item["platform"], item["stage"], item["ok"], item["blob_size"], item["sample_count"], stats
    ))
    if item.get("texbinds"):
        print("  tex: %s" % ", ".join(item["texbinds"][:16]))
    if item.get("cbuffers"):
        print("  cb: %s" % "; ".join(item["cbuffers"][:6]))
    for err in item.get("errors") or []:
        print("  ERR %s" % err)


def write_bytes(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data or b"")


def write_text(path, text):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text or "")


def files_to_open(out_dir):
    files = []
    for name in OPEN_AFTER_COMPILE:
        path = os.path.join(out_dir, name)
        if os.path.isfile(path):
            files.append(path)
    return files


def open_outputs(out_dirs):
    opened = []
    notepad = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "notepad.exe")
    for out_dir in out_dirs:
        if not out_dir or not os.path.isdir(out_dir):
            continue
        try:
            os.startfile(out_dir)
            opened.append(out_dir)
        except OSError as ex:
            print("open folder failed: %s (%s)" % (out_dir, ex))
        for path in files_to_open(out_dir):
            try:
                if os.path.isfile(notepad):
                    subprocess.Popen([notepad, path])
                else:
                    os.startfile(path)
                opened.append(path)
            except OSError as ex:
                print("open file failed: %s (%s)" % (path, ex))
    if opened:
        print("opened %s" % "; ".join(opened))


def compile_platforms(client, code, input_path, keywords, platforms, out_dir, start_line=1):
    results = []
    for platform in platforms:
        plat_id = PLATFORM_IDS[platform]
        if platform in ("vulkan", "gles3"):
            compiled = client.compile_snippet(
                code, input_path, keywords, plat_id, PROGRAM_VERTEX,
                (1 << PROGRAM_VERTEX) | (1 << PROGRAM_FRAGMENT), start_line,
            )
            gpu_type = GPU_SPIRV if platform == "vulkan" else (compiled.gpu_type or 4)
            disasm = ""
            if compiled.blob:
                try:
                    disasm = client.disassemble(plat_id, gpu_type, (1 << PROGRAM_VERTEX) | (1 << PROGRAM_FRAGMENT), compiled.blob)
                except ProtocolError as ex:
                    disasm = "// disassemble failed: %s\n" % ex
                    if platform == "gles3":
                        try:
                            disasm = compiled.blob.decode("utf-8", errors="replace")
                        except Exception:
                            pass
            ext = "spv" if platform == "vulkan" else "glsl"
            write_bytes(os.path.join(out_dir, "%s.%s" % (platform, ext)), compiled.blob)
            write_text(os.path.join(out_dir, "%s.disasm" % platform), disasm)
            item = metrics_from_compile(platform, "vs+fs", compiled, disasm)
            results.append(item)
            print_metrics(item)
            continue

        for stage, ptype, mask, label in (
            ("vs", PROGRAM_VERTEX, 1 << PROGRAM_VERTEX, "vs"),
            ("fs", PROGRAM_FRAGMENT, 1 << PROGRAM_FRAGMENT, "fs"),
        ):
            compiled = client.compile_snippet(code, input_path, keywords, plat_id, ptype, mask, start_line)
            disasm = ""
            if compiled.blob:
                try:
                    disasm = client.disassemble(plat_id, compiled.gpu_type or 0, mask, compiled.blob)
                except ProtocolError as ex:
                    disasm = "// disassemble failed: %s\n" % ex
            write_bytes(os.path.join(out_dir, "d3d11.%s.bin" % label), compiled.blob)
            write_text(os.path.join(out_dir, "d3d11.%s.disasm" % label), disasm)
            item = metrics_from_compile(platform, stage, compiled, disasm)
            results.append(item)
            print_metrics(item)
    return results


def output_dir_for(shader_name, pass_index, keywords, explicit):
    if explicit:
        return os.path.abspath(explicit)
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", shader_name)[:80] or "shader"
    kw_hash = hashlib.sha1(" ".join(keywords).encode("utf-8")).hexdigest()[:10]
    return os.path.join(tempfile.gettempdir(), "usc_compile", slug, "pass%s" % pass_index, kw_hash)


def find_live_include(codm_root, src_path):
    basename = os.path.basename(src_path)
    shaders_root = os.path.join(codm_root, "Assets", "Shaders")
    hits = []
    for root, _dirs, files in os.walk(shaders_root):
        if basename in files:
            hits.append(os.path.join(root, basename))
    if not hits:
        die("live include %s not found under %s" % (basename, shaders_root))
    if len(hits) == 1:
        return hits[0]
    src_parent = os.path.basename(os.path.dirname(os.path.abspath(src_path))).lower()
    ranked = [h for h in hits if os.path.basename(os.path.dirname(h)).lower() == src_parent]
    if len(ranked) == 1:
        return ranked[0]
    die("multiple live includes named %s:\n  %s" % (basename, "\n  ".join(hits)))


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_smoke(client):
    code = (
        '#include "UnityCG.cginc"\n'
        "#pragma vertex vert\n"
        "#pragma fragment frag\n"
        "float4 vert(float4 v : POSITION) : SV_POSITION { return UnityObjectToClipPos(v); }\n"
        "fixed4 frag() : SV_Target { return 1; }\n"
    )
    compiled = client.compile_snippet(
        code, "Hidden/UscSmoke", [], PLATFORM_IDS["vulkan"], PROGRAM_VERTEX,
        (1 << PROGRAM_VERTEX) | (1 << PROGRAM_FRAGMENT), 1,
    )
    print("smoke vulkan ok=%s gpuType=%s blob=%s" % (compiled.ok, compiled.gpu_type, len(compiled.blob)))
    for err in compiled.errors:
        print("  ERR %s" % err.format())
    if not compiled.ok or not compiled.blob:
        die("smoke compile failed")
    disasm = client.disassemble(PLATFORM_IDS["vulkan"], GPU_SPIRV, 3, compiled.blob)
    print("smoke disasm len=%s" % len(disasm))


def build_parser():
    p = argparse.ArgumentParser(description="Compile a Unity 5.6 shader variant via UnityShaderCompiler.exe")
    p.add_argument("--shader", help="Shader name, absolute .shader path, or project-relative path")
    p.add_argument("--pass", dest="pass_index", type=int, default=None, help="Pass index inside the selected SubShader")
    p.add_argument("--lod", type=int, default=None, help="Select SubShader by LOD instead of the first one")
    p.add_argument("--keywords", default="", help="Space-separated keywords")
    p.add_argument("--variant", default="", help="FrameDebugger two-line text")
    p.add_argument("--variant-file", default="", help="File containing FrameDebugger two-line text")
    p.add_argument("--platform", default=",".join(DEFAULT_PLATFORMS), help="vulkan,gles3,d3d11")
    p.add_argument("--list", action="store_true", help="List passes after preprocess")
    p.add_argument("--diff", nargs=2, metavar=("A", "B"), help="Swap two cginc files and compare compiled metrics")
    p.add_argument("--out", default="", help="Output directory")
    p.add_argument("--codm-root", default=DEFAULT_CODM_ROOT)
    p.add_argument("--compiler", default=DEFAULT_COMPILER)
    p.add_argument("--data", default=DEFAULT_DATA)
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--debug", action="store_true")
    p.add_argument("--no-open", action="store_true", help="Do not open output folder/files after compile")
    p.add_argument("remainder", nargs=argparse.REMAINDER, help="Optional FrameDebugger text")
    return p


def resolve_inputs(args):
    shader = args.shader
    pass_index = args.pass_index
    keywords = args.keywords.split() if args.keywords else []
    blobs = []
    if args.variant:
        blobs.append(args.variant)
    if args.variant_file:
        with open(args.variant_file, "r", encoding="utf-8-sig") as f:
            blobs.append(f.read())
    if args.remainder:
        blobs.append(" ".join(args.remainder).replace("\\n", "\n"))
    for blob in blobs:
        s, p, k = parse_variant_text(blob)
        if s and not shader:
            shader = s
        if p is not None and pass_index is None:
            pass_index = p
        if k and not keywords:
            keywords = k
    if pass_index is None:
        pass_index = 0
    return shader, pass_index, keywords


def compile_selected(client, pre, shader_path, shader_name, pass_index, lod, keywords, platforms, out_dir):
    chosen = select_pass(parse_passes(pre.shader_text), pass_index, lod)
    snippet = pre.snippets.get(chosen["snippet_id"])
    if snippet is None:
        die("snippet %s missing from preprocess" % chosen["snippet_id"])
    code = inject_defines(snippet.code, chosen["lod"], chosen["light_mode"])
    input_path = os.path.dirname(shader_path)
    print("shader=%s" % shader_name)
    print("file=%s" % shader_path)
    print("pass=#%s lod=%s name=%s lightMode=%s snippet=%s" % (
        chosen["pass"], chosen["lod"], chosen["name"] or "-", chosen["light_mode"] or "-", chosen["snippet_id"]
    ))
    print("keywords=%s" % (" ".join(keywords) if keywords else "<none>"))
    print("out=%s" % out_dir)
    metrics = compile_platforms(client, code, input_path, keywords, platforms, out_dir, snippet.start_line or 1)
    payload = {
        "shader": shader_name,
        "file": shader_path,
        "pass": chosen,
        "keywords": keywords,
        "platforms": platforms,
        "metrics": metrics,
    }
    write_text(os.path.join(out_dir, "metrics.json"), json.dumps(payload, indent=2, ensure_ascii=False))
    return payload


def main(argv=None):
    args = build_parser().parse_args(argv)
    platforms = normalize_platforms(args.platform)
    shader, pass_index, keywords = resolve_inputs(args)
    if args.smoke:
        includes = default_include_folders(args.codm_root, args.codm_root, args.data)
        with UnityShaderCompiler(args.compiler, args.data, includes, debug=args.debug) as client:
            run_smoke(client)
        return 0
    if not shader:
        die("need --shader or FrameDebugger text like 'CODStandard Dynamic, pass #0'")
    shader_path = find_shader_file(args.codm_root, shader)
    with open(shader_path, "r", encoding="utf-8", errors="replace") as f:
        shader_text = f.read()
    name_m = SHADER_NAME_RE.search(shader_text)
    shader_name = name_m.group(1) if name_m else os.path.splitext(os.path.basename(shader_path))[0]
    includes = default_include_folders(args.codm_root, os.path.dirname(shader_path), args.data)
    with UnityShaderCompiler(args.compiler, args.data, includes, debug=args.debug) as client:
        pre = client.preprocess(shader_text, os.path.dirname(shader_path))
        for err in pre.errors:
            if err.kind <= 0:
                continue
            print("PREPROCESS %s" % err.format())
        if args.list:
            passes = parse_passes(pre.shader_text)
            print("shader=%s" % shader_name)
            print("file=%s" % shader_path)
            print("sub  pass#  lod   name            lightMode       snippet")
            for item in passes:
                print("%3s  %5s  %-5s %-15s %-15s %s" % (
                    item["subshader"], item["pass"], item["lod"] if item["lod"] is not None else "-",
                    (item["name"] or "-")[:15], (item["light_mode"] or "-")[:15], item["snippet_id"]
                ))
            if not args.diff:
                return 0
        if args.diff:
            live = find_live_include(args.codm_root, args.diff[0])
            src_a, src_b = os.path.abspath(args.diff[0]), os.path.abspath(args.diff[1])
            backup = live + ".usc.bak"
            shutil.copy2(live, backup)
            original_hash = file_sha256(live)
            out_root = args.out or os.path.join(tempfile.gettempdir(), "usc_compile", "diff")
            try:
                print("diff live=%s" % live)
                shutil.copy2(src_a, live)
                print("----- A %s -----" % src_a)
                payload_a = compile_selected(
                    client, client.preprocess(shader_text, os.path.dirname(shader_path)),
                    shader_path, shader_name, pass_index, args.lod, keywords, platforms,
                    os.path.join(out_root, "A"),
                )
                shutil.copy2(src_b, live)
                print("----- B %s -----" % src_b)
                payload_b = compile_selected(
                    client, client.preprocess(shader_text, os.path.dirname(shader_path)),
                    shader_path, shader_name, pass_index, args.lod, keywords, platforms,
                    os.path.join(out_root, "B"),
                )
            finally:
                shutil.copy2(backup, live)
                os.remove(backup)
                restored = file_sha256(live)
                if restored != original_hash:
                    die("live include restore hash mismatch: %s" % live)
                print("restored %s" % live)
            print("----- DIFF A vs B -----")
            by_key_a = {(m["platform"], m["stage"]): m for m in payload_a["metrics"]}
            by_key_b = {(m["platform"], m["stage"]): m for m in payload_b["metrics"]}
            for key in sorted(set(by_key_a) | set(by_key_b)):
                a = by_key_a.get(key, {})
                b = by_key_b.get(key, {})
                def delta(field):
                    va, vb = a.get(field), b.get(field)
                    if va is None or vb is None:
                        return "%s->%s" % (va, vb)
                    return "%s (%+d)" % (vb, vb - va)
                print("%s/%s  samples %s  TEX %s  ALU %s  blob %s" % (
                    key[0], key[1], delta("sample_count"), delta("tex"), delta("alu"), delta("blob_size")
                ))
            if not args.no_open:
                open_outputs([os.path.join(out_root, "A"), os.path.join(out_root, "B")])
            return 0
        out_dir = output_dir_for(shader_name, pass_index, keywords, args.out)
        compile_selected(client, pre, shader_path, shader_name, pass_index, args.lod, keywords, platforms, out_dir)
        if not args.no_open:
            open_outputs([out_dir])
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ProtocolError, OSError, ValueError) as ex:
        die(str(ex))

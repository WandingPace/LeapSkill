#!/usr/bin/env python3
"""Check shader keywords against Unity shader source, materials, and variants.

The input file is expected to contain one shader keyword per non-empty line.
A keyword is considered defined when it appears in a supported
``#pragma multi_compile*`` / ``#pragma shader_feature*`` directive, a
``.mat`` material's ``m_ShaderKeywords`` field, or a ``.shadervariants``
``keywords`` entry.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


SHADER_SUFFIXES = {".shader", ".cginc", ".hlsl"}
MATERIAL_SUFFIX = ".mat"
VARIANT_SUFFIX = ".shadervariants"
KEYWORD_TOKEN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PRAGMA_RE = re.compile(
    r"^\s*#\s*pragma\s+"
    r"(?P<directive>multi_compile(?:_local)?|shader_feature(?:_local)?)\b"
    r"(?P<body>.*)$",
    re.IGNORECASE,
)
COMMENT_RE = re.compile(r"//.*$")
BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
IDENTIFIER_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")
MATERIAL_KEYWORDS_RE = re.compile(
    r"^\s*m_(?P<field>Shader|Valid)Keywords:\s*(?P<body>.*?)\s*$"
)
ENGINE_CPP_KEYWORD_RE = re.compile(
    r'(?:CreateBuiltin|keywords::Create)\s*\(\s*"(?P<keyword>[A-Za-z_][A-Za-z0-9_]*)"'
)
VARIANT_KEYWORDS_RE = re.compile(
    r"^(?P<indent>\s*)(?:-\s*)?keywords:\s*(?P<body>.*?)\s*$"
)
VARIANT_FIELD_RE = re.compile(
    r"^\s*(?:passType|maxlod|minlod|fblod|autoUnload)\s*:"
)
RG_LINE_RE = re.compile(r"^(?P<path>.+?):(?P<line>\d+):(?P<text>.*)$")
RG_LINE_NO_PATH_RE = re.compile(r"^(?P<line>\d+):(?P<text>.*)$")


# Unity 5.6 built-in keywords. Keep this deliberately explicit rather than
# treating every SHADOWS_*/LIGHTMAP_* name as built-in, because project shaders
# also define custom keywords with those prefixes.
BUILTIN_KEYWORDS = {
    "_ALPHABLEND_ON",
    "_ALPHAPREMULTIPLY_ON",
    "_ALPHATEST_ON",
    "_EMISSION",
    "_GLOSSYREFLECTIONS_OFF",
    "_DITHER_LOD",
    "_METALLICGLOSSMAP",
    "_NORMALMAP",
    "_PARALLAXMAP",
    "_SPECGLOSSMAP",
    "_SPECULARHIGHLIGHTS_OFF",
    "_SMOOTHNESS_TEXTURE_ALBEDO_CHANNEL_A",
    "DIRECTIONAL",
    "DIRECTIONAL_COOKIE",
    "DIRLIGHTMAP_COMBINED",
    "DIRLIGHTMAP_SEPARATE",
    "DYNAMICLIGHTMAP_ON",
    "FOG_EXP",
    "FOG_EXP2",
    "FOG_LINEAR",
    "INSTANCING_ON",
    "LIGHTMAP_ON",
    "LIGHTMAP_SHADOW_MIXING",
    "POINT",
    "POINT_COOKIE",
    "PROCEDURAL_INSTANCING_ON",
    "SHADOWS_CUBE",
    "SHADOWS_DEPTH",
    "SHADOWS_LIGHTMAP_SHADOWMASK_COMBINED",
    "SHADOWS_NATIVE",
    "SHADOWS_NOSS",
    "SHADOWS_SCREEN",
    "SHADOWS_SHADOWMASK",
    "SHADOWS_SOFT",
    "SHADOWS_SINGLE_CASCADE",
    "SHADOWS_SPLIT_SPHERES",
    "SOFTPARTICLES_ON",
    "SPOT",
    "STEREO_CUBEMAP_RENDER_ON",
    "STEREO_INSTANCING_ON",
    "STEREO_MULTIVIEW_ON",
    "VERTEX_ATTRIB_INSTANCING_ON",
    "UNITY_COLORSPACE_GAMMA",
    "UNITY_HDR_ON",
    "UNITY_NO_DXT5NM",
    "UNITY_SINGLE_PASS_STEREO",
    "UNITY_UI_ALPHACLIP",
    "UNITY_UI_CLIP_RECT",
    "VERTEXLIGHT_ON",
}

@dataclass(frozen=True)
class KeywordOccurrence:
    origin: str
    directive: str
    source: Path
    line: int


@dataclass(frozen=True)
class KeywordResult:
    keyword: str
    status: str
    occurrences: tuple[KeywordOccurrence, ...]
    references: tuple[KeywordOccurrence, ...] = ()


@dataclass(frozen=True)
class DeletedKeywordFile:
    source: Path
    origin: str
    removed_keywords: tuple[str, ...]


def parse_args() -> argparse.Namespace:
    repo_root = Path(os.environ.get("CODM_ROOT", r"I:\CODMCHN")).resolve()
    default_keyword_file = (
        repo_root / "Assets" / "Shaders" / "CODM" / "Standard" / "keyword.txt"
    )
    default_scan_root = repo_root / "Assets"

    parser = argparse.ArgumentParser(
        description=(
            "List keywords that have no shader pragma declaration but are "
            "present in materials or shader variant collections."
        )
    )
    parser.add_argument(
        "keyword_file",
        nargs="?",
        type=Path,
        default=default_keyword_file,
        help=f"keyword list (default: {default_keyword_file})",
    )
    parser.add_argument(
        "--scan-root",
        type=Path,
        default=default_scan_root,
        help=f"source root to scan (default: {default_scan_root})",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        help="optional CSV output path",
    )
    parser.add_argument(
        "--unity-cginclude",
        type=Path,
        help=(
            "optional Unity CGIncludes directory; adds discovered built-in "
            "keywords to the whitelist"
        ),
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="only print the summary and matched keywords",
    )
    parser.add_argument(
        "--no-materials",
        action="store_true",
        help="do not scan .mat files",
    )
    parser.add_argument(
        "--no-variants",
        action="store_true",
        help="do not scan .shadervariants files",
    )
    parser.add_argument(
        "--materials-only",
        action="store_true",
        help="only compare against material keywords",
    )
    parser.add_argument(
        "--variants-only",
        action="store_true",
        help="only compare against shader variant collection keywords",
    )
    parser.add_argument(
        "--shader-only",
        action="store_true",
        help="scan only shader source declarations",
    )
    parser.add_argument(
        "--rg",
        type=Path,
        help="optional ripgrep executable used for fast .mat scanning",
    )
    parser.add_argument(
        "--engine-root",
        type=Path,
        help=(
            "Unity engine source root (default: G:\\UnitySourceCODM when present)"
        ),
    )
    parser.add_argument(
        "--no-engine",
        action="store_true",
        help="skip engine keyword validation",
    )
    parser.add_argument(
        "--show-engine",
        action="store_true",
        help="print resource-only keywords that are also defined by the engine",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="delete unmatched keywords from material and variant resources",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="confirm actual deletion when --delete is used",
    )
    parser.add_argument(
        "--delete-report",
        type=Path,
        help="CSV path listing files changed by --delete",
    )
    parser.add_argument(
        "--all-occurrences",
        action="store_true",
        help="write every material/variant reference to CSV instead of one per origin",
    )
    return parser.parse_args()


def read_keywords(path: Path) -> list[str]:
    keywords: list[str] = []
    seen: set[str] = set()
    with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
        for line_number, raw_line in enumerate(handle, 1):
            keyword = raw_line.strip()
            if not keyword or keyword.startswith("#"):
                continue
            if keyword == "_":
                continue
            if not KEYWORD_TOKEN_RE.fullmatch(keyword):
                raise ValueError(
                    f"{path}:{line_number}: invalid keyword token: {keyword!r}"
                )
            if keyword not in seen:
                seen.add(keyword)
                keywords.append(keyword)
    return keywords


def iter_files_with_suffixes(root: Path, suffixes: set[str]):
    if root.is_file():
        if root.suffix.lower() in suffixes:
            yield root
        return

    ignored_directories = {".svn", ".git", "Library", "Temp", "obj"}
    for current_root, directory_names, file_names in os.walk(root):
        directory_names[:] = [
            name
            for name in directory_names
            if name not in ignored_directories and not name.startswith(".")
        ]
        current_path = Path(current_root)
        for file_name in file_names:
            path = current_path / file_name
            if path.suffix.lower() in suffixes:
                yield path


def iter_source_files(root: Path):
    yield from iter_files_with_suffixes(root, SHADER_SUFFIXES)


def resolve_ripgrep(path: Path | None) -> Path | None:
    if path:
        resolved = path.resolve()
        if resolved.is_file():
            return resolved
        return None

    from_path = shutil.which("rg")
    if from_path:
        return Path(from_path)

    project_rg = Path(
        r"C:\Users\leapliu\background_agent_cli\bin\rg.exe"
    )
    if project_rg.is_file():
        return project_rg
    return None


def run_rg_lines(
    rg_path: Path,
    root: Path,
    globs: list[str],
    expressions: list[str],
) -> list[tuple[Path, int, str]]:
    command = [
        str(rg_path),
        "-n",
        "--no-heading",
        "--color",
        "never",
    ]
    for glob in globs:
        command.extend(["-g", glob])
    for expression in expressions:
        command.extend(["-e", expression])
    command.append(str(root))

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert process.stdout is not None
    lines: list[tuple[Path, int, str]] = []
    for raw_line in process.stdout:
        cleaned = raw_line.rstrip("\r\n")
        match = RG_LINE_RE.match(cleaned)
        if match:
            lines.append(
                (
                    Path(match.group("path")),
                    int(match.group("line")),
                    match.group("text"),
                )
            )
            continue
        match = RG_LINE_NO_PATH_RE.match(cleaned)
        if match:
            lines.append(
                (
                    root,
                    int(match.group("line")),
                    match.group("text"),
                )
            )
    stderr = process.communicate(timeout=60)[1].strip()
    if process.returncode not in (0, 1):
        raise RuntimeError(stderr or f"rg exited with {process.returncode}")
    return lines


def parse_material_line(
    declarations: dict[str, list[KeywordOccurrence]],
    source: Path,
    line_number: int,
    text: str,
) -> None:
    match = MATERIAL_KEYWORDS_RE.match(text)
    if not match:
        return

    body = match.group("body").strip()
    if not body or body == "[]":
        return
    for token in body.split():
        if set(token) == {"_"} or not KEYWORD_TOKEN_RE.fullmatch(token):
            continue
        declarations.setdefault(token, []).append(
            KeywordOccurrence(
                origin="material",
                directive=f"m_{match.group('field')}Keywords",
                source=source,
                line=line_number,
            )
        )


def collect_material_keywords(
    root: Path,
    rg_path: Path | None,
) -> dict[str, list[KeywordOccurrence]]:
    declarations: dict[str, list[KeywordOccurrence]] = {}

    if rg_path and root.is_dir():
        try:
            for source, line_number, text in run_rg_lines(
                rg_path,
                root,
                ["*.mat"],
                [r"m_(?:Shader|Valid)Keywords:"],
            ):
                parse_material_line(
                    declarations,
                    source,
                    line_number,
                    text,
                )
            return declarations
        except (OSError, subprocess.SubprocessError, RuntimeError) as exc:
            print(
                f"warning: ripgrep material scan failed, falling back: {exc}",
                file=sys.stderr,
            )
            declarations.clear()

    for source in iter_material_files(root):
        try:
            with source.open("r", encoding="utf-8-sig", errors="replace") as handle:
                for line_number, raw_line in enumerate(handle, 1):
                    parse_material_line(
                        declarations,
                        source,
                        line_number,
                        raw_line,
                    )
        except OSError as exc:
            print(f"warning: cannot read {source}: {exc}", file=sys.stderr)

    return declarations


def iter_material_files(root: Path):
    yield from iter_files_with_suffixes(root, {MATERIAL_SUFFIX})


def collect_variant_keywords(
    root: Path,
    rg_path: Path | None,
) -> dict[str, list[KeywordOccurrence]]:
    declarations: dict[str, list[KeywordOccurrence]] = {}

    if rg_path:
        hits = run_rg_lines(
            rg_path,
            root,
            ["*.shadervariants"],
            [r"^\s*(?:-\s*)?keywords:"],
        )
        lines: list[tuple[Path, int, str]] = []
        grouped: dict[Path, list[tuple[int, str]]] = {}
        for source, line_number, text in hits:
            grouped.setdefault(source, []).append((line_number, text))

        for source, source_hits in grouped.items():
            try:
                with source.open(
                    "r", encoding="utf-8-sig", errors="replace"
                ) as handle:
                    source_lines = handle.readlines()
            except OSError as exc:
                print(f"warning: cannot read {source}: {exc}", file=sys.stderr)
                continue

            for line_number, text in source_hits:
                lines.append((source, line_number, text))
                current_line = source_lines[line_number - 1]
                current_indent = len(current_line) - len(current_line.lstrip())
                index = line_number
                while index < len(source_lines):
                    continuation = source_lines[index]
                    if VARIANT_FIELD_RE.match(continuation):
                        break
                    if (
                        continuation.strip()
                        and not continuation.lstrip().startswith("#")
                        and len(continuation) - len(continuation.lstrip())
                        > current_indent
                    ):
                        lines.append((source, line_number, continuation))
                    else:
                        break
                    index += 1
    else:
        lines = []
        for source in iter_files_with_suffixes(root, {VARIANT_SUFFIX}):
            try:
                with source.open(
                    "r", encoding="utf-8-sig", errors="replace"
                ) as handle:
                    keyword_line: int | None = None
                    for line_number, raw_line in enumerate(handle, 1):
                        match = VARIANT_KEYWORDS_RE.match(raw_line.rstrip("\r\n"))
                        if match:
                            keyword_line = line_number
                            lines.append((source, line_number, raw_line))
                            continue
                        if keyword_line is None:
                            continue
                        if VARIANT_FIELD_RE.match(raw_line):
                            keyword_line = None
                            continue
                        if raw_line.strip() and not raw_line.lstrip().startswith(
                            "#"
                        ):
                            lines.append((source, keyword_line, raw_line))
            except OSError as exc:
                print(f"warning: cannot read {source}: {exc}", file=sys.stderr)

    for source, line_number, raw_line in lines:
        match = VARIANT_KEYWORDS_RE.match(raw_line.rstrip("\r\n"))
        if match:
            body = match.group("body")
        else:
            body = raw_line
        for token in body.split():
            if set(token) == {"_"} or not KEYWORD_TOKEN_RE.fullmatch(token):
                continue
            declarations.setdefault(token, []).append(
                KeywordOccurrence(
                    origin="variant",
                    directive="keywords",
                    source=source,
                    line=line_number,
                )
            )

    return declarations


def merge_declarations(
    target: dict[str, list[KeywordOccurrence]],
    source: dict[str, list[KeywordOccurrence]],
) -> None:
    for keyword, occurrences in source.items():
        target.setdefault(keyword, []).extend(occurrences)


def collect_shader_keywords(
    root: Path,
) -> tuple[
    dict[str, list[KeywordOccurrence]],
    dict[str, list[KeywordOccurrence]],
]:
    declarations: dict[str, list[KeywordOccurrence]] = {}
    references: dict[str, list[KeywordOccurrence]] = {}
    condition_re = re.compile(r"^\s*#\s*(?:if|ifdef|ifndef|elif)\b(.*)$")

    for source in iter_source_files(root):
        try:
            with source.open("r", encoding="utf-8-sig", errors="replace") as handle:
                for line_number, raw_line in enumerate(handle, 1):
                    line = COMMENT_RE.sub("", raw_line)
                    pragma_match = PRAGMA_RE.match(line)
                    if pragma_match:
                        directive = pragma_match.group("directive")
                        tokens = pragma_match.group("body").split()
                        for token in tokens:
                            if set(token) == {"_"} or not KEYWORD_TOKEN_RE.fullmatch(
                                token
                            ):
                                continue
                            declarations.setdefault(token, []).append(
                                KeywordOccurrence(
                                    origin="pragma",
                                    directive=directive,
                                    source=source,
                                    line=line_number,
                                )
                            )

                    uncommented = BLOCK_COMMENT_RE.sub("", line)
                    condition_match = condition_re.match(uncommented)
                    if not condition_match:
                        continue
                    for token in IDENTIFIER_RE.findall(condition_match.group(1)):
                        references.setdefault(token, []).append(
                            KeywordOccurrence(
                                origin="conditional",
                                directive="conditional",
                                source=source,
                                line=line_number,
                            )
                        )
        except OSError as exc:
            print(f"warning: cannot read {source}: {exc}", file=sys.stderr)

    return declarations, references


def collect_shader_keywords_with_rg(
    root: Path,
    rg_path: Path,
) -> tuple[
    dict[str, list[KeywordOccurrence]],
    dict[str, list[KeywordOccurrence]],
]:
    declarations: dict[str, list[KeywordOccurrence]] = {}
    references: dict[str, list[KeywordOccurrence]] = {}
    condition_re = re.compile(r"^\s*#\s*(?:if|ifdef|ifndef|elif)\b(.*)$")

    for source, line_number, text in run_rg_lines(
        rg_path,
        root,
        ["*.shader", "*.cginc", "*.hlsl"],
        [
            r"^\s*#\s*pragma\s+(multi_compile|shader_feature)",
            r"^\s*#\s*(if|ifdef|ifndef|elif)\b",
        ],
    ):
        line = COMMENT_RE.sub("", text)
        pragma_match = PRAGMA_RE.match(line)
        if pragma_match:
            directive = pragma_match.group("directive")
            for token in pragma_match.group("body").split():
                if set(token) == {"_"} or not KEYWORD_TOKEN_RE.fullmatch(token):
                    continue
                declarations.setdefault(token, []).append(
                    KeywordOccurrence(
                        origin="pragma",
                        directive=directive,
                        source=source,
                        line=line_number,
                    )
                )

        condition_match = condition_re.match(line)
        if not condition_match:
            continue
        for token in IDENTIFIER_RE.findall(condition_match.group(1)):
                        references.setdefault(token, []).append(
                KeywordOccurrence(
                    origin="conditional",
                    directive="conditional",
                    source=source,
                    line=line_number,
                )
            )

    return declarations, references


def is_builtin_keyword(keyword: str) -> bool:
    return keyword in BUILTIN_KEYWORDS


def load_unity_cginclude_keywords(root: Path) -> set[str]:
    """Best-effort extraction from a Unity CGIncludes directory.

    This is intentionally opt-in because the project targets Unity 5.6 and a
    newer locally installed Unity may define a different keyword set.
    """

    if not root.is_dir():
        raise ValueError(f"Unity CGIncludes directory not found: {root}")

    keywords: set[str] = set()
    for source in iter_source_files(root):
        try:
            with source.open("r", encoding="utf-8-sig", errors="replace") as handle:
                for raw_line in handle:
                    line = COMMENT_RE.sub("", raw_line)
                    match = PRAGMA_RE.match(line)
                    if not match:
                        continue
                    tokens = match.group("body").split()
                    if not tokens:
                        continue
                    for token in tokens:
                        if set(token) != {"_"} and KEYWORD_TOKEN_RE.fullmatch(token):
                            keywords.add(token)
        except OSError as exc:
            print(f"warning: cannot read {source}: {exc}", file=sys.stderr)
    return keywords


def collect_engine_keywords(
    engine_root: Path,
    rg_path: Path | None,
) -> dict[str, list[KeywordOccurrence]]:
    declarations: dict[str, list[KeywordOccurrence]] = {}
    shader_keywords_cpp = engine_root / "Runtime" / "Shaders" / "ShaderKeywords.cpp"

    if shader_keywords_cpp.is_file():
        try:
            with shader_keywords_cpp.open(
                "r", encoding="utf-8-sig", errors="replace"
            ) as handle:
                for line_number, raw_line in enumerate(handle, 1):
                    line = COMMENT_RE.sub("", raw_line)
                    match = ENGINE_CPP_KEYWORD_RE.search(line)
                    if not match:
                        continue
                    keyword = match.group("keyword")
                    declarations.setdefault(keyword, []).append(
                        KeywordOccurrence(
                            origin="engine-builtin",
                            directive="CreateBuiltin",
                            source=shader_keywords_cpp,
                            line=line_number,
                        )
                    )
        except OSError as exc:
            print(f"warning: cannot read {shader_keywords_cpp}: {exc}", file=sys.stderr)

    engine_shader_roots = [
        engine_root / "Shaders",
        engine_root / "External" / "Resources",
    ]
    for root in engine_shader_roots:
        if not root.is_dir():
            continue
        try:
            if rg_path:
                hits = run_rg_lines(
                    rg_path,
                    root,
                    ["*.shader", "*.cginc", "*.hlsl"],
                    [r"^\s*#\s*pragma\s+(multi_compile|shader_feature)"],
                )
            else:
                hits = []
                for source in iter_source_files(root):
                    try:
                        with source.open(
                            "r", encoding="utf-8-sig", errors="replace"
                        ) as handle:
                            for line_number, raw_line in enumerate(handle, 1):
                                if PRAGMA_RE.match(COMMENT_RE.sub("", raw_line)):
                                    hits.append((source, line_number, raw_line))
                    except OSError as exc:
                        print(
                            f"warning: cannot read {source}: {exc}",
                            file=sys.stderr,
                        )

            for source, line_number, text in hits:
                pragma_match = PRAGMA_RE.match(COMMENT_RE.sub("", text))
                if not pragma_match:
                    continue
                for token in pragma_match.group("body").split():
                    if set(token) == {"_"} or not KEYWORD_TOKEN_RE.fullmatch(token):
                        continue
                    declarations.setdefault(token, []).append(
                        KeywordOccurrence(
                            origin="engine-shader",
                            directive=pragma_match.group("directive"),
                            source=source,
                            line=line_number,
                        )
                    )
        except (OSError, subprocess.SubprocessError, RuntimeError) as exc:
            print(f"warning: engine keyword scan failed for {root}: {exc}", file=sys.stderr)

    return declarations


def find_engine_references(
    engine_root: Path,
    rg_path: Path | None,
    keywords: set[str],
) -> dict[str, KeywordOccurrence]:
    if not keywords:
        return {}

    references: dict[str, KeywordOccurrence] = {}
    roots = [engine_root / "Runtime", engine_root / "Shaders"]
    expressions = [re.escape(keyword) for keyword in sorted(keywords)]
    for root in roots:
        if not root.is_dir():
            continue
        try:
            if rg_path:
                hits = run_rg_lines(
                    rg_path,
                    root,
                    ["*.cpp", "*.h", "*.cginc", "*.hlsl", "*.shader"],
                    expressions,
                )
            else:
                hits = []
                for source in iter_files_with_suffixes(
                    root, {".cpp", ".h", ".cginc", ".hlsl", ".shader"}
                ):
                    try:
                        with source.open(
                            "r", encoding="utf-8-sig", errors="replace"
                        ) as handle:
                            for line_number, raw_line in enumerate(handle, 1):
                                for keyword in keywords:
                                    if keyword in raw_line:
                                        hits.append(
                                            (source, line_number, raw_line)
                                        )
                                        break
                    except OSError:
                        continue
        except (OSError, subprocess.SubprocessError, RuntimeError) as exc:
            print(
                f"warning: engine reference scan failed for {root}: {exc}",
                file=sys.stderr,
            )
            continue

        for source, line_number, text in hits:
            for keyword in keywords:
                if keyword in references:
                    continue
                if re.search(rf"\b{re.escape(keyword)}\b", text):
                    references[keyword] = KeywordOccurrence(
                        origin="engine-reference",
                        directive="reference",
                        source=source,
                        line=line_number,
                    )

    return references


def relative_display_path(path: Path, base: Path) -> str:
    try:
        return str(path.resolve().relative_to(base.resolve()))
    except (OSError, ValueError):
        return str(path)


def write_csv(
    path: Path,
    results: list[KeywordResult],
    base: Path,
    all_occurrences: bool,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["keyword", "status", "origin", "directive", "source", "line"])
        for result in results:
            if not result.occurrences:
                writer.writerow([result.keyword, result.status, "", "", "", ""])
                continue
            occurrences = result.occurrences
            if not all_occurrences:
                first_by_origin: dict[str, KeywordOccurrence] = {}
                for occurrence in occurrences:
                    first_by_origin.setdefault(occurrence.origin, occurrence)
                occurrences = tuple(first_by_origin.values())
            for occurrence in occurrences:
                writer.writerow(
                    [
                        result.keyword,
                        result.status,
                        occurrence.origin,
                        occurrence.directive,
                        relative_display_path(occurrence.source, base),
                        occurrence.line,
                    ]
                )


def write_delete_report(
    path: Path,
    deleted_files: list[DeletedKeywordFile],
    base: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["source", "origin", "removed_keywords", "count"])
        for deleted in deleted_files:
            writer.writerow(
                [
                    relative_display_path(deleted.source, base),
                    deleted.origin,
                    " ".join(deleted.removed_keywords),
                    len(deleted.removed_keywords),
                ]
            )


def remove_keywords_from_material(
    source: Path,
    keywords: set[str],
) -> list[str]:
    raw = source.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    original = raw.decode("utf-8-sig")
    lines = original.splitlines(keepends=True)
    removed_keywords: list[str] = []

    for index, raw_line in enumerate(lines):
        line = raw_line.rstrip("\r\n")
        match = MATERIAL_KEYWORDS_RE.match(line)
        if not match:
            continue
        body = match.group("body").strip()
        if not body or body == "[]":
            continue
        tokens = body.split()
        kept = [token for token in tokens if token not in keywords]
        removed_keywords.extend(token for token in tokens if token in keywords)
        if len(kept) == len(tokens):
            continue
        lines[index] = (
            f"  m_{match.group('field')}Keywords: "
            + " ".join(kept)
            + ("\n" if raw_line.endswith("\n") else "")
        )

    if removed_keywords:
        output = "".join(lines).encode("utf-8")
        if has_bom:
            output = b"\xef\xbb\xbf" + output
        source.write_bytes(output)
    return removed_keywords


def remove_keywords_from_variant(
    source: Path,
    keywords: set[str],
) -> list[str]:
    raw = source.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    original = raw.decode("utf-8-sig")
    lines = original.splitlines(keepends=True)
    removed_keywords: list[str] = []
    index = 0

    while index < len(lines):
        raw_line = lines[index]
        line = raw_line.rstrip("\r\n")
        match = VARIANT_KEYWORDS_RE.match(line)
        if not match:
            index += 1
            continue

        prefix = "        - keywords: "
        continuation_prefix = "            "
        tokens = match.group("body").split()
        kept = [token for token in tokens if token not in keywords]
        removed_keywords.extend(token for token in tokens if token in keywords)
        lines[index] = prefix + " ".join(kept) + ("\n" if raw_line.endswith("\n") else "")

        next_index = index + 1
        while next_index < len(lines):
            continuation_raw = lines[next_index]
            continuation = continuation_raw.rstrip("\r\n")
            if VARIANT_FIELD_RE.match(continuation):
                break
            if (
                not continuation.strip()
                or continuation.lstrip().startswith("#")
                or len(continuation) - len(continuation.lstrip())
                <= len(line) - len(line.lstrip())
            ):
                break
            continuation_tokens = continuation.split()
            continuation_kept = [
                token for token in continuation_tokens if token not in keywords
            ]
            removed_keywords.extend(
                token for token in continuation_tokens if token in keywords
            )
            if continuation_kept:
                lines[next_index] = (
                    continuation_prefix
                    + " ".join(continuation_kept)
                    + ("\n" if continuation_raw.endswith("\n") else "")
                )
                next_index += 1
            else:
                del lines[next_index]
        index = next_index

    if removed_keywords:
        output = "".join(lines).encode("utf-8")
        if has_bom:
            output = b"\xef\xbb\xbf" + output
        source.write_bytes(output)
    return removed_keywords


def delete_unmatched_keywords(
    results: list[KeywordResult],
    scan_root: Path,
) -> tuple[list[DeletedKeywordFile], int]:
    keywords = {result.keyword for result in results}
    if not keywords:
        return [], 0

    sources: dict[Path, str] = {}
    for result in results:
        for occurrence in result.occurrences:
            if occurrence.origin in {"material", "variant"}:
                sources[occurrence.source] = occurrence.origin

    deleted_files: list[DeletedKeywordFile] = []
    removed_count = 0
    for source, origin in sorted(sources.items()):
        try:
            if origin == "material":
                removed_keywords = remove_keywords_from_material(source, keywords)
            else:
                removed_keywords = remove_keywords_from_variant(source, keywords)
        except OSError as exc:
            print(f"error: cannot update {source}: {exc}", file=sys.stderr)
            continue
        if removed_keywords:
            unique_removed = tuple(sorted(set(removed_keywords)))
            removed_count += len(removed_keywords)
            deleted_files.append(
                DeletedKeywordFile(
                    source=source,
                    origin=origin,
                    removed_keywords=unique_removed,
                )
            )

    return deleted_files, removed_count


def main() -> int:
    args = parse_args()
    keyword_file = args.keyword_file.resolve()
    scan_root = args.scan_root.resolve()

    if not keyword_file.is_file():
        print(f"error: keyword file not found: {keyword_file}", file=sys.stderr)
        return 2
    if not scan_root.exists():
        print(f"error: scan root not found: {scan_root}", file=sys.stderr)
        return 2

    keywords = read_keywords(keyword_file)
    rg_path = resolve_ripgrep(args.rg)
    if rg_path:
        shader_declarations, _ = collect_shader_keywords_with_rg(
            scan_root,
            rg_path,
        )
    else:
        shader_declarations, _ = collect_shader_keywords(scan_root)

    material_declarations: dict[str, list[KeywordOccurrence]] = {}
    variant_declarations: dict[str, list[KeywordOccurrence]] = {}
    if args.materials_only and args.variants_only:
        print(
            "error: --materials-only and --variants-only cannot be combined",
            file=sys.stderr,
        )
        return 2
    if not (args.no_materials or args.shader_only or args.variants_only):
        material_declarations = collect_material_keywords(
            scan_root,
            rg_path,
        )
    if not (args.no_variants or args.shader_only or args.materials_only):
        variant_declarations = collect_variant_keywords(
            scan_root,
            rg_path,
        )

    unity_keywords: set[str] = set()
    if args.unity_cginclude:
        try:
            unity_keywords = load_unity_cginclude_keywords(
                args.unity_cginclude.resolve()
            )
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

    resource_only: list[KeywordResult] = []
    for keyword in keywords:
        if keyword in shader_declarations:
            continue
        if is_builtin_keyword(keyword) or keyword in unity_keywords:
            continue

        resource_occurrences = tuple(
            [
                *material_declarations.get(keyword, []),
                *variant_declarations.get(keyword, []),
            ]
        )
        if not resource_occurrences:
            continue

        resource_only.append(
            KeywordResult(
                keyword=keyword,
                status="resource-only",
                occurrences=resource_occurrences,
            )
        )

    engine_declarations: dict[str, list[KeywordOccurrence]] = {}
    engine_root = (
        args.engine_root.resolve()
        if args.engine_root
        else Path(r"G:\UnitySourceCODM")
    )
    if not args.no_engine and engine_root.is_dir():
        engine_declarations = collect_engine_keywords(engine_root, rg_path)

    engine_matched = [
        result for result in resource_only if result.keyword in engine_declarations
    ]
    unmatched = [
        result for result in resource_only if result.keyword not in engine_declarations
    ]
    engine_references: dict[str, KeywordOccurrence] = {}
    if args.show_engine and not args.no_engine and engine_root.is_dir():
        engine_references = find_engine_references(
            engine_root,
            rg_path,
            {result.keyword for result in unmatched},
        )

    if not args.quiet:
        print(f"Keyword file : {keyword_file}")
        print(f"Scan root    : {scan_root}")
        print(f"Keywords     : {len(keywords)}")
        print(f"Shader-only  : {len(shader_declarations)}")
        print(f"Resource-only: {len(resource_only)}")
        if not args.no_engine and engine_root.is_dir():
            print(f"Engine-known : {len(engine_matched)}")
            print(f"Unmatched    : {len(unmatched)}")
        if unity_keywords:
            print(f"Unity hints  : {len(unity_keywords)} keywords loaded")
        print()

    if unmatched:
        print("Keywords not defined by shader, engine, or built-in whitelist:")
        for result in unmatched:
            occurrence = result.occurrences[0]
            try:
                source_path = occurrence.source.resolve().relative_to(
                    scan_root.resolve()
                )
            except ValueError:
                source_path = occurrence.source
            print(
                f"  {result.keyword}  "
                f"[{occurrence.origin}] ({source_path}:{occurrence.line})"
            )

    if args.show_engine and engine_references:
        print()
        print("Unmatched keywords that also appear as engine text references:")
        for keyword, reference in sorted(engine_references.items()):
            try:
                source_path = reference.source.resolve().relative_to(
                    engine_root.resolve()
                )
            except ValueError:
                source_path = reference.source
            print(f"  {keyword}  ({source_path}:{reference.line})")
    elif not args.quiet:
        print("Keywords not defined by shader, engine, or built-in whitelist: none")

    if args.show_engine and engine_matched:
        print()
        print("Resource-only keywords that are defined by the engine:")
        for result in engine_matched:
            occurrence = engine_declarations[result.keyword][0]
            try:
                source_path = occurrence.source.resolve().relative_to(
                    engine_root.resolve()
                )
            except ValueError:
                source_path = occurrence.source
            print(
                f"  {result.keyword}  "
                f"[{occurrence.origin}] ({source_path}:{occurrence.line})"
            )

    deleted = False
    if args.delete:
        if not args.yes:
            print()
            print(
                "Delete requested but not applied; pass --yes to modify "
                "material/variant resources."
            )
        else:
            deleted_files, removed_entries = delete_unmatched_keywords(
                unmatched,
                scan_root,
            )
            deleted = True
            print()
            print(
                "Deleted resource keywords: "
                f"files={len(deleted_files)}, entries={removed_entries}"
            )
            if args.delete_report:
                write_delete_report(
                    args.delete_report.resolve(),
                    deleted_files,
                    Path.cwd(),
                )
                print(f"Delete report: {args.delete_report.resolve()}")

    if args.csv:
        write_csv(
            args.csv.resolve(),
            unmatched,
            Path.cwd(),
            args.all_occurrences,
        )
        print()
        print(f"CSV          : {args.csv.resolve()}")

    if deleted:
        return 0
    return 1 if unmatched else 0


if __name__ == "__main__":
    raise SystemExit(main())


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Socket client for Unity 5.6 UnityShaderCompiler.exe."""

from __future__ import annotations

import os
import socket
import struct
import subprocess
import tempfile
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


MAGIC = 201508070
PLATFORM_COUNT = 20

PLATFORM_IDS = {
    "opengl": 0,
    "d3d9": 1,
    "d3d11": 4,
    "gles": 9,
    "gles2": 5,
    "gles3": 9,
    "metal": 14,
    "glcore": 15,
    "vulkan": 18,
}

PROGRAM_VERTEX = 0
PROGRAM_FRAGMENT = 1
LANGUAGE_CG = 0
GPU_SPIRV = 25


class ProtocolError(RuntimeError):
    pass


@dataclass
class CompilerError:
    kind: int
    platform: int
    line: int
    file: str
    message: str

    def format(self) -> str:
        loc = self.file or "<compiler>"
        return "%s(%s): %s" % (loc, self.line, self.message.replace("\n", " | "))


@dataclass
class Snippet:
    snippet_id: int
    platform_mask: int
    types_mask: int
    language: int
    start_line: int
    code: str


@dataclass
class PreprocessResult:
    ok: bool
    had_surface: bool
    shader_text: str
    snippets: Dict[int, Snippet] = field(default_factory=dict)
    errors: List[CompilerError] = field(default_factory=list)


@dataclass
class CompileResult:
    ok: bool
    gpu_type: int
    blob: bytes
    errors: List[CompilerError] = field(default_factory=list)
    stats: Optional[Tuple[int, int, int, int]] = None
    texbinds: List[str] = field(default_factory=list)
    cbs: List[str] = field(default_factory=list)
    constants: List[str] = field(default_factory=list)
    reflection: List[str] = field(default_factory=list)


class UnityShaderCompiler:
    def __init__(self, compiler_exe, data_dir, include_folders, debug=False):
        self.compiler_exe = compiler_exe
        self.data_dir = data_dir
        self.include_folders = include_folders
        self.debug = debug
        self._proc = None
        self._sock = None
        self._log_path = ""

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False

    def _log(self, msg):
        if self.debug:
            print(msg, flush=True)

    def start(self):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        listener.settimeout(30)
        port = listener.getsockname()[1]
        self._log_path = os.path.join(tempfile.gettempdir(), "usc_%s.log" % port)
        playback = self.data_dir.replace("\\", "/") + "/PlaybackEngines"
        args = [self.compiler_exe, self.data_dir, self._log_path, str(port), playback]
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
        self._proc = subprocess.Popen(
            args,
            cwd=os.path.dirname(self.compiler_exe),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
        )
        conn, _addr = listener.accept()
        listener.close()
        conn.settimeout(180)
        self._sock = conn
        self._initialize()

    def close(self):
        try:
            if self._sock is not None:
                self._send_line("c:shutdown")
        except Exception:
            pass
        try:
            if self._sock is not None:
                self._sock.close()
        except Exception:
            pass
        self._sock = None
        if self._proc is not None:
            try:
                self._proc.wait(timeout=5)
            except Exception:
                try:
                    self._proc.kill()
                except Exception:
                    pass
            self._proc = None

    def compiler_log(self):
        try:
            with open(self._log_path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except OSError:
            return ""

    def _send_line(self, text):
        data = text.encode("utf-8")
        self._send_frame(data)
        if self.debug:
            shown = text if len(text) <= 80 else text[:80] + "..."
            self._log(">> %s (bytes=%s)" % (shown, len(data)))

    def _send_buf(self, data):
        self._send_frame(data)

    def _send_frame(self, data):
        self._sock.sendall(struct.pack("<II", MAGIC, len(data)) + data)

    def _send_int(self, value):
        self._send_line(str(int(value)))

    def _recv_exact(self, n):
        buf = bytearray()
        while len(buf) < n:
            chunk = self._sock.recv(n - len(buf))
            if not chunk:
                raise ProtocolError("compiler closed the socket")
            buf.extend(chunk)
        return bytes(buf)

    def _recv_frame(self):
        window = bytearray()
        while True:
            b = self._sock.recv(1)
            if not b:
                raise ProtocolError("compiler closed the socket")
            window += b
            if len(window) > 4:
                window = window[-4:]
            if len(window) == 4 and struct.unpack_from("<I", window, 0)[0] == MAGIC:
                length = struct.unpack("<I", self._recv_exact(4))[0]
                if length < 0:
                    raise ProtocolError("negative frame length")
                return b"" if length == 0 else self._recv_exact(length)

    def _read_line(self):
        text = self._recv_frame().decode("utf-8", errors="replace")
        if self.debug:
            shown = text if len(text) <= 120 else text[:120] + "..."
            self._log("<< [len=%s] %s" % (len(text), shown))
        return text

    def _read_buf(self):
        return self._recv_frame()

    def _initialize(self):
        self._send_line("c:initializeCompiler")
        self._send_int(len(self.include_folders))
        for folder in self.include_folders:
            self._send_line(folder)
        plat = self._read_line()
        self._log("platforms mask line=%s" % plat)
        for _ in range(PLATFORM_COUNT * 2):
            self._read_line()

    def _read_error(self, header):
        parts = header.split()
        kind = int(parts[1]) if len(parts) > 1 else 0
        plat = int(parts[2]) if len(parts) > 2 else -1
        line = int(parts[3]) if len(parts) > 3 else -1
        file_name = self._read_line()
        message = self._read_line()
        return CompilerError(kind, plat, line, file_name, message)

    def preprocess(self, shader_text, input_path):
        self._send_line("c:preprocess")
        self._send_line(shader_text)
        self._send_line(input_path)
        self._send_line("0")
        result = PreprocessResult(ok=False, had_surface=False, shader_text="")
        while True:
            line = self._read_line()
            if line.startswith("err:"):
                result.errors.append(self._read_error(line))
                continue
            if line.startswith("snip:"):
                parts = line.split()
                code = self._read_line()
                snippet = Snippet(
                    snippet_id=int(parts[1]),
                    platform_mask=int(parts[2]),
                    types_mask=int(parts[4]),
                    language=int(parts[5]),
                    start_line=int(parts[10]),
                    code=code,
                )
                result.snippets[snippet.snippet_id] = snippet
                continue
            if line.startswith("keywordsUser:") or line.startswith("keywordsBuiltin:"):
                count = int(line.split()[3])
                for _ in range(count):
                    self._read_line()
                continue
            if line.startswith("keywordsEnd:"):
                self._read_line()
                self._read_line()
                self._read_line()
                kw_count = int(self._read_line() or "0")
                for _ in range(kw_count):
                    self._read_line()
                    self._read_line()
                continue
            if line.startswith("shader:"):
                parts = line.split()
                result.ok = len(parts) > 1 and parts[1] == "1"
                result.had_surface = len(parts) > 2 and parts[2] == "1"
                result.shader_text = self._read_line()
                return result

    def compile_snippet(self, code, input_path, keywords, platform, program_type, program_mask, start_line=1):
        self._send_line("c:compileSnippet")
        self._send_line(code)
        self._send_line(input_path)
        self._send_int(0)
        self._send_int(len(keywords))
        for kw in keywords:
            self._send_line(kw)
        self._send_int(0)
        self._send_int(LANGUAGE_CG)
        self._send_int(program_type)
        self._send_int(platform)
        self._send_int(0)
        self._send_int(program_mask)
        self._send_int(start_line)

        result = CompileResult(ok=False, gpu_type=0, blob=b"")
        while True:
            line = self._read_line()
            if not line:
                continue
            if line.startswith("err:"):
                result.errors.append(self._read_error(line))
                continue
            if line.startswith("stats:"):
                parts = line.split()
                if len(parts) == 5:
                    result.stats = (int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4]))
                result.reflection.append(line)
                continue
            if line.startswith("texbind:"):
                toks = line.split()
                result.texbinds.append(toks[1] if len(toks) > 1 else line)
                result.reflection.append(line)
                continue
            if line.startswith("cb:"):
                result.cbs.append(line)
                result.reflection.append(line)
                continue
            if line.startswith("const:"):
                toks = line.split()
                result.constants.append(toks[1] if len(toks) > 1 else line)
                result.reflection.append(line)
                continue
            if line.startswith("shader:"):
                parts = line.split()
                result.ok = len(parts) > 1 and parts[1] == "1"
                result.gpu_type = int(self._read_line() or "0")
                result.blob = self._read_buf()
                return result
            result.reflection.append(line)

    def disassemble(self, platform, gpu_type, program_mask, blob):
        self._send_line("c:disassembleShader")
        self._send_int(platform)
        self._send_int(gpu_type)
        self._send_int(program_mask)
        self._send_buf(blob)
        while True:
            line = self._read_line()
            if line.startswith("err:"):
                err = self._read_error(line)
                raise ProtocolError("disassemble error: %s" % err.format())
            if line.startswith("disasm:"):
                return self._read_line()

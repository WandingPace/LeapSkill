#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SVN 差异解析器
用于解析 SVN diff 输出，提取修改的 C# 方法
"""

import subprocess
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class ModifiedMethod:
    """修改的方法信息"""
    class_name: str
    namespace: str
    method_name: str
    method_signature: str
    method_body: str
    file_path: str
    line_start: int
    line_end: int


@dataclass
class SvnLogEntry:
    """SVN 日志条目"""
    revision: str
    author: str
    date: str
    message: str
    changed_files: List[str]


def run_svn_command(args: list, cwd: str = None) -> Tuple[int, str, str]:
    """执行 SVN 命令"""
    try:
        result = subprocess.run(
            ["svn"] + args,
            capture_output=True,
            text=True,
            cwd=cwd,
            encoding="utf-8",
            errors="replace"
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)


def get_latest_svn_log(client_path: str) -> Optional[SvnLogEntry]:
    """获取最近一次 SVN 提交记录"""
    code, stdout, stderr = run_svn_command(["log", "-l", "1", "-v", "--xml", client_path])

    if code != 0:
        print(f"错误: 获取 SVN 日志失败 - {stderr}", file=sys.stderr)
        return None

    try:
        root = ET.fromstring(stdout)
        entry = root.find(".//logentry")
        if entry is None:
            return None

        revision = entry.get("revision", "")
        author = entry.findtext("author", "")
        date = entry.findtext("date", "")
        message = entry.findtext("msg", "")

        # 获取修改的文件
        changed_files = []
        paths_elem = entry.find("paths")
        if paths_elem is not None:
            for path_elem in paths_elem.findall("path"):
                file_path = path_elem.text or ""
                # 只关注 .cs 文件
                if file_path.endswith(".cs"):
                    changed_files.append(file_path)

        return SvnLogEntry(
            revision=revision,
            author=author,
            date=date,
            message=message.strip() if message else "",
            changed_files=changed_files
        )
    except ET.ParseError as e:
        print(f"错误: 解析 SVN 日志失败 - {e}", file=sys.stderr)
        return None


def get_file_diff(file_path: str, revision: str) -> str:
    """获取文件在指定版本的差异"""
    prev_rev = str(int(revision) - 1)
    code, stdout, stderr = run_svn_command([
        "diff", "-r", f"{prev_rev}:{revision}", file_path
    ])

    if code != 0:
        print(f"警告: 获取差异失败 {file_path} - {stderr}", file=sys.stderr)
        return ""

    return stdout


def get_file_content(file_path: str, revision: str = None) -> str:
    """获取文件内容"""
    args = ["cat"]
    if revision:
        args.extend(["-r", revision])
    args.append(file_path)

    code, stdout, stderr = run_svn_command(args)
    if code != 0:
        return ""
    return stdout


def parse_diff_hunks(diff_content: str) -> List[Tuple[int, int, List[str]]]:
    """解析 diff 输出，提取修改的行范围

    Returns:
        List of (start_line, end_line, changed_lines)
    """
    hunks = []
    current_hunk = None
    current_lines = []

    for line in diff_content.split("\n"):
        # 匹配 @@ -old_start,old_count +new_start,new_count @@
        hunk_match = re.match(r"^@@\s*-(\d+)(?:,\d+)?\s*\+(\d+)(?:,\d+)?\s*@@", line)
        if hunk_match:
            if current_hunk:
                hunks.append((current_hunk[0], current_hunk[1], current_lines))
            current_hunk = (int(hunk_match.group(2)), int(hunk_match.group(2)))
            current_lines = []
        elif current_hunk and (line.startswith("+") or line.startswith("-")):
            current_lines.append(line)

    if current_hunk:
        hunks.append((current_hunk[0], current_hunk[1] + len(current_lines), current_lines))

    return hunks


def find_method_at_line(content: str, target_line: int) -> Optional[Tuple[str, str, int, int]]:
    """在文件内容中找到包含指定行的方法

    Returns:
        (method_signature, method_body, start_line, end_line) or None
    """
    lines = content.split("\n")

    # 方法签名正则：匹配各种修饰符 + 返回类型 + 方法名 + 参数列表
    method_pattern = re.compile(
        r"^\s*(public|private|protected|internal|static|virtual|override|abstract|async|\s)+\s+"
        r"[\w<>\[\],\s]+\s+"  # 返回类型
        r"(\w+)\s*"  # 方法名
        r"\([^)]*\)"  # 参数列表
        r"\s*(?:where\s+\w+\s*:\s*\w+)?\s*$"  # 可选的泛型约束
    )

    # 向上搜索找方法签名
    method_start = -1
    method_name = ""
    method_sig = ""

    for i in range(min(target_line, len(lines) - 1), -1, -1):
        line = lines[i]
        match = method_pattern.match(line)
        if match:
            method_start = i
            method_name = match.group(2) if match.lastindex >= 2 else ""
            method_sig = line.strip()
            break
        # 如果遇到类定义或其他方法的结束，停止搜索
        if re.match(r"^\s*(class|struct|interface|enum)\s+", line):
            break

    if method_start < 0:
        return None

    # 向下搜索找方法结束（匹配大括号）
    brace_count = 0
    method_end = method_start
    in_method = False

    for i in range(method_start, len(lines)):
        line = lines[i]
        for char in line:
            if char == "{":
                brace_count += 1
                in_method = True
            elif char == "}":
                brace_count -= 1
                if in_method and brace_count == 0:
                    method_end = i
                    break
        if in_method and brace_count == 0:
            break

    method_body = "\n".join(lines[method_start:method_end + 1])
    return (method_sig, method_body, method_start + 1, method_end + 1)


def find_class_info(content: str, method_line: int) -> Tuple[str, str]:
    """查找方法所在的类名和命名空间

    Returns:
        (namespace, class_name)
    """
    lines = content.split("\n")
    namespace = ""
    class_name = ""

    for i in range(min(method_line, len(lines) - 1), -1, -1):
        line = lines[i].strip()

        # 查找类定义
        if not class_name:
            class_match = re.match(r"(?:public|private|protected|internal|\s)*(?:partial\s+)?class\s+(\w+)", line)
            if class_match:
                class_name = class_match.group(1)

        # 查找命名空间
        if not namespace:
            ns_match = re.match(r"namespace\s+([\w.]+)", line)
            if ns_match:
                namespace = ns_match.group(1)

        if namespace and class_name:
            break

    return (namespace, class_name)


def extract_modified_methods(client_path: str, log_entry: SvnLogEntry) -> List[ModifiedMethod]:
    """从 SVN 提交中提取所有修改的方法"""
    methods = []

    for cs_file in log_entry.changed_files:
        # 构建本地文件路径
        # SVN 路径通常是 /trunk/xxx/Client/xxx.cs，需要转换为本地路径
        local_path = cs_file
        if "/Client/" in cs_file:
            rel_path = cs_file.split("/Client/", 1)[-1]
            local_path = str(Path(client_path) / rel_path)

        # 获取文件差异
        diff_content = get_file_diff(local_path, log_entry.revision)
        if not diff_content:
            continue

        # 获取文件完整内容
        file_content = get_file_content(local_path, log_entry.revision)
        if not file_content:
            continue

        # 解析差异，找到修改的行
        hunks = parse_diff_hunks(diff_content)

        # 对每个修改区域，找到对应的方法
        processed_methods = set()
        for start_line, end_line, _ in hunks:
            method_info = find_method_at_line(file_content, start_line)
            if method_info:
                method_sig, method_body, m_start, m_end = method_info

                # 避免重复处理同一方法
                method_key = f"{local_path}:{m_start}"
                if method_key in processed_methods:
                    continue
                processed_methods.add(method_key)

                # 获取类信息
                namespace, class_name = find_class_info(file_content, m_start)

                # 从方法签名中提取方法名
                method_name_match = re.search(r"(\w+)\s*\(", method_sig)
                method_name = method_name_match.group(1) if method_name_match else ""

                methods.append(ModifiedMethod(
                    class_name=class_name,
                    namespace=namespace,
                    method_name=method_name,
                    method_signature=method_sig,
                    method_body=method_body,
                    file_path=local_path,
                    line_start=m_start,
                    line_end=m_end
                ))

    return methods


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="SVN 差异解析器")
    parser.add_argument("client_path", help="Client 目录路径")
    parser.add_argument("--output", "-o", help="输出文件路径")

    args = parser.parse_args()

    # 获取最新提交
    log_entry = get_latest_svn_log(args.client_path)
    if not log_entry:
        print("无法获取 SVN 日志")
        return

    print(f"SVN 版本: r{log_entry.revision}")
    print(f"提交者: {log_entry.author}")
    print(f"提交信息: {log_entry.message}")
    print(f"修改的 C# 文件: {len(log_entry.changed_files)}")

    if not log_entry.changed_files:
        print("没有修改的 C# 文件")
        return

    # 提取修改的方法
    methods = extract_modified_methods(args.client_path, log_entry)

    print(f"\n找到 {len(methods)} 个修改的方法:")
    for m in methods:
        print(f"  - {m.namespace}.{m.class_name}.{m.method_name}")
        print(f"    文件: {m.file_path}")
        print(f"    行: {m.line_start}-{m.line_end}")


if __name__ == "__main__":
    main()

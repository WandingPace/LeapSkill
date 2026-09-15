#!/usr/bin/env python3
"""
扫描SVN合并后的重复定义和冲突标记残留问题
适用于双向合并（主线合入分支 / 分支合入主线）

用法：
  python scan_duplicates.py              # 扫描所有已修改的 .cs 文件
  python scan_duplicates.py <dir>        # 扫描指定目录下已修改的 .cs 文件
  python scan_duplicates.py --all <dir>  # 扫描指定目录下所有 .cs 文件（不限于已修改）
"""
import re
import subprocess
import os
import sys
import argparse


def read_file_content(filepath):
    """读取文件内容，自动处理编码"""
    for enc in ['utf-8-sig', 'gbk', 'latin-1']:
        try:
            with open(filepath, 'r', encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    return None


def get_modified_cs_files(directory=None):
    """从 svn status 获取所有已修改的 .cs 文件"""
    try:
        cmd = ['svn', 'status']
        if directory:
            cmd.append(directory)
        result = subprocess.check_output(
            cmd, stderr=subprocess.DEVNULL
        ).decode('utf-8', 'ignore')
    except subprocess.CalledProcessError:
        print('ERROR: svn status failed')
        return []

    modified = []
    for line in result.splitlines():
        if line.startswith('M ') or line.startswith('A '):
            fp = line[8:].strip()
            if fp.endswith('.cs'):
                modified.append(fp)
    return modified


def get_all_cs_files(directory):
    """获取目录下所有 .cs 文件"""
    cs_files = []
    for root, dirs, files in os.walk(directory):
        # 跳过隐藏目录和常见非代码目录
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('Library', 'Temp', 'obj')]
        for f in files:
            if f.endswith('.cs'):
                cs_files.append(os.path.join(root, f))
    return cs_files


def scan_duplicate_definitions(files):
    """扫描重复的字段/属性定义"""
    dupes_found = []

    # 匹配字段定义的正则
    field_pattern = re.compile(
        r'(?:protected |public |private )?'
        r'(?:static )?'
        r'(?:readonly )?'
        r'(?:bool|int|float|uint|string|byte|UInt32|long|UInt64|double|short|ushort|char|decimal|Vector[234]|Color|Quaternion)\s+'
        r'(\w+)\s*[=;]'
    )

    for fp in files:
        if not os.path.exists(fp):
            continue

        content = read_file_content(fp)
        if content is None:
            continue

        # 收集所有字段定义
        definitions = {}
        for i, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('/*'):
                continue
            m = field_pattern.match(stripped)
            if m:
                name = m.group(1)
                if name not in definitions:
                    definitions[name] = []
                definitions[name].append(i)

        # 找出重复定义
        for name, lines in definitions.items():
            if len(lines) > 1:
                dupes_found.append(
                    f'{fp}: "{name}" defined {len(lines)} times (lines {", ".join(str(l) for l in lines)})'
                )

    return dupes_found


def scan_conflict_markers(files):
    """扫描冲突标记残留"""
    markers_found = []

    for fp in files:
        if not os.path.exists(fp):
            continue

        content = read_file_content(fp)
        if content is None:
            continue

        for i, line in enumerate(content.splitlines(), 1):
            if line.startswith('<<<<<<< .working') or line.startswith('>>>>>>> .merge-right'):
                markers_found.append(f'{fp}:{i}: {line.strip()}')
            elif line.startswith('||||||| .merge-left'):
                markers_found.append(f'{fp}:{i}: {line.strip()}')
            elif line.strip() == '=======':
                # 只在附近有其他冲突标记时才报告
                pass

    return markers_found


def scan_incomplete_methods(files):
    """扫描不完整的方法定义（缺少花括号）"""
    issues = []

    for fp in files:
        if not os.path.exists(fp):
            continue

        content = read_file_content(fp)
        if content is None:
            continue

        lines = content.splitlines()
        brace_depth = 0
        for i, line in enumerate(lines):
            brace_depth += line.count('{') - line.count('}')

        if brace_depth != 0:
            issues.append(f'{fp}: unbalanced braces (depth={brace_depth})')

    return issues


def main():
    parser = argparse.ArgumentParser(
        description='扫描SVN合并后的重复定义和冲突标记残留'
    )
    parser.add_argument('directory', nargs='?', default=None,
                        help='要扫描的目录（默认当前目录）')
    parser.add_argument('--all', action='store_true',
                        help='扫描所有 .cs 文件，不限于 svn 已修改的')
    args = parser.parse_args()

    # 获取文件列表
    if args.all and args.directory:
        files = get_all_cs_files(args.directory)
        print(f"Scanning ALL {len(files)} .cs files in {args.directory}...")
    else:
        files = get_modified_cs_files(args.directory)
        print(f"Scanning {len(files)} modified .cs files...")

    if not files:
        print("No .cs files to scan.")
        return

    # 1. 扫描重复定义
    print("\n=== Duplicate Definitions ===")
    dupes = scan_duplicate_definitions(files)
    if dupes:
        print(f"⚠️  Found {len(dupes)} duplicate definitions:")
        for d in sorted(set(dupes)):
            print(f"  {d}")
    else:
        print("✅ No duplicate definitions found")

    # 2. 扫描冲突标记残留
    print("\n=== Conflict Markers ===")
    markers = scan_conflict_markers(files)
    if markers:
        print(f"⚠️  Found {len(markers)} conflict markers:")
        for m in markers:
            print(f"  {m}")
    else:
        print("✅ No conflict markers found")

    # 3. 扫描不平衡的花括号
    print("\n=== Unbalanced Braces ===")
    brace_issues = scan_incomplete_methods(files)
    if brace_issues:
        print(f"⚠️  Found {len(brace_issues)} files with unbalanced braces:")
        for issue in brace_issues:
            print(f"  {issue}")
    else:
        print("✅ All files have balanced braces")

    # 汇总
    total_issues = len(dupes) + len(markers) + len(brace_issues)
    print(f"\n{'='*40}")
    if total_issues > 0:
        print(f"⚠️  Total: {total_issues} issues found")
    else:
        print("✅ All checks passed - no issues found")


if __name__ == '__main__':
    main()

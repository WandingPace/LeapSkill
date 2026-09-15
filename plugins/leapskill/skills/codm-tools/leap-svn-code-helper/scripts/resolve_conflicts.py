#!/usr/bin/env python3
"""
SVN合并冲突批量解决脚本
策略：保留目标分支(working)版本，追加源分支(merge-right)中base没有的新行
适用于双向合并（主线合入分支 / 分支合入主线）

用法：
  python resolve_conflicts.py <file1> <file2> ...
  python resolve_conflicts.py --all              # 处理当前目录下所有冲突文件
  python resolve_conflicts.py --all --dry-run    # 只预览，不实际修改文件
  python resolve_conflicts.py --all --resolve    # 解决冲突后自动执行 svn resolved
"""
import re
import sys
import os
import subprocess
import argparse

CONFLICT_PATTERN = (
    r'<<<<<<< \.working\n(.*?)'
    r'\|\|\|\|\|\|\| \.merge-left\.r\d+\n(.*?)'
    r'=======\n(.*?)'
    r'>>>>>>> \.merge-right\.r\d+'
)


def read_file(filepath):
    """读取文件，自动处理编码"""
    for enc in ['utf-8-sig', 'gbk', 'latin-1']:
        try:
            with open(filepath, 'r', encoding=enc) as f:
                return f.read(), enc.replace('-sig', '')
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise RuntimeError(f"Cannot decode {filepath}")


def resolve_conflict(match):
    """解决单个冲突块：保留目标版本 + 追加源分支独有的新行"""
    working = match.group(1)   # 目标分支版本（当前工作副本）
    base = match.group(2)      # 共同祖先版本（分支点）
    theirs = match.group(3)    # 源分支版本（要合入的修改）

    working_lines = [l for l in working.strip().split('\n') if l.strip()]
    theirs_lines = [l for l in theirs.strip().split('\n') if l.strip()]
    base_lines = [l for l in base.strip().split('\n') if l.strip()]

    working_set = set(l.strip() for l in working_lines)
    base_set = set(l.strip() for l in base_lines)

    # 找出源分支新增的行（在 theirs 中但不在 working 和 base 中）
    new_from_source = []
    for l in theirs_lines:
        stripped = l.strip()
        if stripped and stripped not in working_set and stripped not in base_set:
            new_from_source.append(l)

    result = working.rstrip()
    if new_from_source:
        result += '\n' + '\n'.join(new_from_source)

    return result


def process_file(filepath, dry_run=False):
    """处理单个文件的所有冲突"""
    content, enc = read_file(filepath)

    conflicts = list(re.finditer(CONFLICT_PATTERN, content, re.DOTALL))
    if not conflicts:
        print(f'  SKIP (no conflicts): {filepath}')
        return 0

    if dry_run:
        print(f'  DRY-RUN: {filepath} ({len(conflicts)} conflicts found)')
        return len(conflicts)

    new_content = re.sub(CONFLICT_PATTERN, resolve_conflict, content, flags=re.DOTALL)
    remaining = new_content.count('<<<<<<< .working')

    with open(filepath, 'w', encoding=enc) as f:
        f.write(new_content)

    status = 'OK' if remaining == 0 else f'PARTIAL ({remaining} remaining)'
    print(f'  {status}: {filepath} ({len(conflicts)} resolved)')
    return len(conflicts)


def svn_resolved(filepath):
    """执行 svn resolved 标记冲突已解决"""
    try:
        subprocess.run(['svn', 'resolved', filepath],
                       capture_output=True, timeout=30)
        print(f'  svn resolved: {filepath}')
    except Exception as e:
        print(f'  WARNING: svn resolved failed for {filepath}: {e}')


def get_conflicted_files():
    """从 svn status 获取所有冲突文件"""
    try:
        result = subprocess.check_output(
            ['svn', 'status'], stderr=subprocess.DEVNULL
        ).decode('utf-8', 'ignore')
    except subprocess.CalledProcessError:
        print('ERROR: svn status failed')
        return []

    files = []
    for line in result.splitlines():
        if line.startswith('C '):
            files.append(line[8:].strip())
    return files


def main():
    parser = argparse.ArgumentParser(
        description='SVN合并冲突批量解决脚本'
    )
    parser.add_argument('files', nargs='*', help='要处理的冲突文件列表')
    parser.add_argument('--all', action='store_true',
                        help='处理当前目录下所有冲突文件')
    parser.add_argument('--dry-run', action='store_true',
                        help='只预览，不实际修改文件')
    parser.add_argument('--resolve', action='store_true',
                        help='解决冲突后自动执行 svn resolved')
    args = parser.parse_args()

    if not args.all and not args.files:
        parser.print_help()
        sys.exit(1)

    if args.all:
        files = get_conflicted_files()
        print(f'Found {len(files)} conflicted files')
    else:
        files = args.files

    if not files:
        print('No conflicted files to process.')
        return

    total_resolved = 0
    total_files = 0

    for f in files:
        if not os.path.exists(f):
            print(f'  SKIP (not found): {f}')
            continue

        resolved = process_file(f, dry_run=args.dry_run)
        if resolved > 0:
            total_resolved += resolved
            total_files += 1
            if args.resolve and not args.dry_run:
                svn_resolved(f)

    action = 'found' if args.dry_run else 'resolved'
    print(f'\nTotal: {total_resolved} conflicts {action} in {total_files} files')


if __name__ == '__main__':
    main()

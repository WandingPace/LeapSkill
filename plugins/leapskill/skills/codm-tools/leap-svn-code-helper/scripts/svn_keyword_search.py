"""
svn_keyword_search.py - SVN commit keyword search tool
Search SVN commit history to find which revision introduced/removed a keyword in a file.

Usage:
    python svn_keyword_search.py <file_path> <keyword> [options]

Options:
    -n, --limit N       Max revisions to check (default: 100)
    -t, --timeout N     Timeout per SVN command in seconds (default: 20)
    --introduced-only   Only show revisions that introduced the keyword (added it)
    --all               Show all revisions containing the keyword (default)

Examples:
    python svn_keyword_search.py "I:\\CODMCHN\\Assets\\Scenes\\Map\\BR\\BR_RebirthIsland\\CLY_RebirthIsland_Main.unity" "ModelDirectionalLight"
    python svn_keyword_search.py "I:\\CODMCHN\\Assets\\Scripts\\Engine\\PlayerCamera.cs" "SomeMethod" -n 200
    python svn_keyword_search.py "I:\\CODMCHN\\Assets\\Scripts\\Engine\\PlayerCamera.cs" "SomeMethod" --introduced-only
"""

import subprocess
import sys
import re
import argparse

DEFAULT_LIMIT = 100
DEFAULT_TIMEOUT = 20


def run_svn(args, timeout=DEFAULT_TIMEOUT):
    """Run an SVN command and return (stdout, stderr)."""
    cmd = ["svn"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=timeout)
        for enc in ("utf-8", "gbk", "latin-1"):
            try:
                stdout = result.stdout.decode(enc)
                stderr = result.stderr.decode(enc, errors="replace")
                return stdout, stderr
            except Exception:
                continue
        return result.stdout.decode("latin-1"), ""
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] Command timed out: {' '.join(cmd)}")
        return "", "timeout"
    except Exception as e:
        print(f"[ERROR] Failed to run command: {' '.join(cmd)}\n{e}")
        return "", str(e)


def get_revisions(file_path, limit):
    """Get SVN log for a file. Returns list of (rev, author, date, msg)."""
    print(f"[INFO] Fetching latest {limit} revisions...")
    stdout, stderr = run_svn(["log", "-l", str(limit), file_path])
    if not stdout:
        print(f"[ERROR] svn log failed: {stderr}")
        return []

    revisions = []
    pattern = re.compile(r"^r(\d+)\s*\|\s*(\S+)\s*\|\s*([^|]+)\|")
    lines = stdout.splitlines()
    i = 0
    while i < len(lines):
        m = pattern.match(lines[i])
        if m:
            rev = m.group(1)
            author = m.group(2)
            date = m.group(3).strip()
            msg_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith("---"):
                line = lines[i].strip()
                if line and not line.startswith("Changed paths:") and not lines[i].startswith("   "):
                    msg_lines.append(line)
                i += 1
            msg = " ".join(msg_lines).strip()
            revisions.append((rev, author, date, msg))
        else:
            i += 1
    return revisions


def cat_file(file_path, rev, timeout=DEFAULT_TIMEOUT):
    """Fetch file content at a specific revision via svn cat."""
    stdout, stderr = run_svn(["cat", "-r", rev, file_path], timeout=timeout)
    if stderr == "timeout":
        return None, True   # content, is_timeout
    return stdout, False


def search(file_path, keyword, limit=DEFAULT_LIMIT, timeout=DEFAULT_TIMEOUT, introduced_only=False):
    """
    Main search logic.
    Returns list of dicts with keys: rev, author, date, msg, count, change_type
    """
    print(f"{'='*60}")
    print(f"File    : {file_path}")
    print(f"Keyword : {keyword}")
    print(f"Limit   : {limit} revisions")
    print(f"{'='*60}\n")

    revisions = get_revisions(file_path, limit)
    if not revisions:
        print("[WARN] No revisions found.")
        return []

    print(f"[INFO] {len(revisions)} revisions retrieved. Checking content via svn cat...\n")

    found = []
    prev_has_keyword = None

    for idx, (rev, author, date, msg) in enumerate(revisions):
        print(f"[{idx+1}/{len(revisions)}] r{rev} ({author}, {date[:20]}) ...", end=" ", flush=True)
        content, timed_out = cat_file(file_path, rev, timeout=timeout)

        if timed_out:
            print("⏱ Timeout, skipped")
            prev_has_keyword = None
            continue
        if content is None:
            print("❌ Failed to fetch")
            prev_has_keyword = None
            continue

        has_keyword = keyword in content

        # Determine change type
        if has_keyword:
            if prev_has_keyword is False:
                change_type = "➕ Added"
            elif prev_has_keyword is None:
                change_type = "✅ Present (first checked)"
            else:
                change_type = "✅ Present (unchanged)"
        else:
            if prev_has_keyword is True:
                change_type = "➖ Removed"
            else:
                change_type = "—"

        if has_keyword or (prev_has_keyword is True and not has_keyword):
            print(change_type)
        else:
            print("—")

        if has_keyword:
            count = content.count(keyword)
            found.append({
                "rev": rev,
                "author": author,
                "date": date.strip(),
                "msg": msg,
                "count": count,
                "change_type": change_type,
            })

        prev_has_keyword = has_keyword

    return found


def print_results(found, keyword, total_checked, introduced_only=False):
    """Print search results in a formatted summary."""
    print(f"\n{'='*60}")

    introduced = [f for f in found if "Added" in f["change_type"] or "first" in f["change_type"]]

    if not found:
        print(f"❌ Keyword [{keyword}] not found in the last {total_checked} revisions.")
        print(f"{'='*60}")
        return

    if not introduced_only:
        print(f"✅ {len(found)} revision(s) contain [{keyword}]\n")

    if introduced:
        print(f"🔍 Revision(s) that INTRODUCED [{keyword}]:")
        for item in introduced:
            print(f"  Revision : r{item['rev']}")
            print(f"  Author   : {item['author']}")
            print(f"  Date     : {item['date']}")
            print(f"  Message  : {item['msg']}")
            print(f"  Count    : {item['count']} occurrence(s)")
            print()

    if not introduced_only:
        print(f"📋 All revisions containing [{keyword}] (newest first):")
        for item in found:
            print(f"  r{item['rev']} | {item['author']:15s} | {item['date'][:20]} | {item['change_type']} | {item['msg'][:60]}")

    print(f"{'='*60}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Search SVN commit history to find which revision introduced/removed a keyword in a file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("file_path", help="Local path to the SVN-managed file")
    parser.add_argument("keyword", help="Keyword to search for in file content")
    parser.add_argument(
        "-n", "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        metavar="N",
        help=f"Max number of revisions to check (default: {DEFAULT_LIMIT})",
    )
    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        metavar="SEC",
        help=f"Timeout per SVN command in seconds (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--introduced-only",
        action="store_true",
        help="Only show revisions that introduced (added) the keyword",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    found = search(
        file_path=args.file_path,
        keyword=args.keyword,
        limit=args.limit,
        timeout=args.timeout,
        introduced_only=args.introduced_only,
    )
    print_results(found, args.keyword, args.limit, introduced_only=args.introduced_only)


if __name__ == "__main__":
    main()

## Cursor Cloud specific instructions

LeapSkill is a static Cursor/Codex/CodeBuddy skill plugin. There is no package manager, lockfile, dev server, database, Docker service, or lint/test runner. Dependency refresh is a no-op; Python helpers use the standard library only.

Structure checks live in `README.md` (`find` of `SKILL.md`, plus description frontmatter). Expect 55 skills, and every path in `plugins/leapskill/.cursor-plugin/plugin.json` must have a `SKILL.md`. Syntax-check helpers with `python3 -m compileall -q plugins`.

Scripts that run on this Linux VM without a Windows CODM checkout:

- `plugins/leapskill/skills/support/git-safety-guardrails/scripts/classify_git_command.py` prints JSON. Exit `0` means allow; exit `2` means review (force push, hard reset, and the other patterns in that file).
- `plugins/leapskill/skills/codm-tools/leap-drawcall-diff/scripts/drawcall_diff.py FILE_A FILE_B` compares two DrawCallRecord JSON files. Camera / VP matrices are ignored unless `--include-camera` is passed.
- `plugins/leapskill/skills/codm-tools/leap-shader-keyword-audit/scripts/shader_keyword_audit.py KEYWORDS --scan-root DIR --no-engine` audits a local shader/material tree. The default keyword path and scan root assume `I:\CODMCHN`. Exit code `1` means unmatched resource keywords were found; that is a successful audit, not a crash.

`leap-rdc-debug-diff`, `leap-unity-test-validation`, `leap-android-build-push`, `leap-render-validation`, and the SVN helpers shell out to Windows-only tools (`svn`, Unity, RenderDoc, `adb`) and hardcoded drive paths. They cannot be exercised here.

`docs/skill-flow-map.html` is a static page (no server). The map is drawn inside an iframe `srcdoc`. Headless Chrome’s screenshot of the outer file is blank; screenshot the decoded inner document, or open the file in a normal browser.

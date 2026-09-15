---
name: leap-quickcmd-compose
description: Dynamically discover and compose the user's PowerShell QuickCmd commands from H:\MyNote\Obsidian_data\assets\ps\QuickCmd.ps1. Use when the user asks in Chinese or English to execute one or more QuickCmd operations, including ordered workflows such as closing CODM and then fully updating the project. Always show the resolved qc-* invocation sequence before executing it.
---

# QuickCmd Compose

Use `scripts/quickcmd-runner.ps1` as the only execution entry point. Never duplicate or hard-code the command catalog from `QuickCmd.ps1` in this skill.

## Workflow

1. Run the runner with `-List -Json` before every requested workflow. This dot-sources the current `QuickCmd.ps1` and returns its live command catalog.
2. Map each user-requested action to a catalog entry using its display name and `qc-*` function name. Preserve the exact order stated by the user.
3. If an action has one clear match, continue without asking. Ask only when multiple live entries remain genuinely plausible or no entry matches.
4. Before execution, tell the user the exact sequence in one short line, for example: `调用顺序：qc-closeCODM -> qc-updateProject`.
5. Execute the sequence with one runner call and `-Commands`, preserving order. Do not use QuickCmd's interactive `c`/fzf picker.
6. Report each command's success or failure. Stop the sequence on the first failure unless the user explicitly requests best-effort continuation.

## Commands

List the current catalog:

```powershell
& "<skill-dir>\scripts\quickcmd-runner.ps1" -List -Json
```

Execute an ordered workflow:

```powershell
& "<skill-dir>\scripts\quickcmd-runner.ps1" -Commands qc-closeCODM,qc-updateProject
```

Use `-ContinueOnError` only when the user explicitly asks to continue after failures.

## Safety

- Treat the user's direct request to close, open, update, build, configure, or forward as authorization for the matching live QuickCmd entry.
- Do not silently add actions the user did not request.
- Never invoke a `qc-*` function that is absent from the live catalog.
- Keep execution visible: show the resolved sequence in chat and allow the runner to print command headers and native output.
- If loading the source file fails, stop and report the path/error; do not fall back to a stale catalog.

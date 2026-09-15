---
name: leap-drawio-clean-diagrams
description: Use when creating, editing, reviewing, previewing, or saving draw.io / diagrams.net class diagrams, flowcharts, sequence diagrams, architecture diagrams, or .drawio XML through mcp__drawio and the result must be readable, well laid out, and easy for humans to understand.
---

# draw.io Clean Diagrams

## Core principle

Model the diagram as a visual system, not as XML syntax. Before writing any
`mxCell`, decide the diagram's lanes, layers, reading direction, and edge
routes. Then generate XML that preserves that human-readable structure.

For `mcp__drawio.open_drawio_xml`, use `routing="libavoid"` whenever edges
would cross boxes or multiple connectors converge in a dense area.

## Workflow

1. Decide the reading direction:
   - **Flowchart:** top-to-bottom main path, labels on branch exits.
   - **Class diagram:** left-to-right dependency flow, inheritance parents on
     the top layer, aggregates/compositions kept near their owners.
   - **Sequence diagram:** left-to-right participants in first-appearance
     order, messages strictly top-to-bottom.
2. Reduce the model before drawing:
   - Show only classes that explain ownership, inheritance, or data flow.
   - Show only fields/methods that distinguish the class's responsibility.
   - Collapse boilerplate accessors into one line such as
     `Getters/Setters for config`.
3. Pick one layout pattern from `references/layout-patterns.md` and keep all
   nodes on its grid. Do not mix free placement, swimlanes, and table grids in
   one page.
4. Apply the matching construction rules in `references/layout-patterns.md`.
5. Build one `<mxGraphModel>` per page. For multiple diagrams, use one named
   page per diagram rather than merging unrelated views.
6. Run the final checklist in `references/layout-patterns.md` before presenting
   or saving the file.

## Tool routing

- **Required tool:** use the `mcp__drawio` namespace for draw.io operations;
  do not edit diagram files only as raw text or merely return XML.
- **Create / preview:** call `mcp__drawio.open_drawio_xml`; add
  `routing="libavoid"` for dense hand-placed diagrams.
- **Edit existing files:** first call `mcp__drawio.list_pages`, then read the
  target with `mcp__drawio.get_page`; produce the revised XML and write it back
  with `mcp__drawio.set_page`. Re-read the page after writing when the edit is
  structural.
- **Create a local multi-page `.drawio` file:** create the file with
  `apply_patch`, then use the MCP page APIs above for subsequent reads and
  edits. Never rewrite the whole multi-page file for one page-level edit.
- **Mermaid exception:** use `mcp__drawio.open_drawio_mermaid` only for a
  simple graph under roughly 12 nodes with no custom layout requirements.
- **Multi-page output:** use short page names: `Class`, `Flow`, `Sequence`,
  `Architecture`.

Do not add XML comments to generated draw.io XML.

## Readability contract

- Every node label is 1-6 words plus an optional concise detail line.
- A label explains the concept, not the implementation.
- An edge label is 1-3 words (`Yes`, `No`, `async`, `owns`, `calls`).
- Color encodes one stable meaning per diagram; add a small legend when two or
  more semantic colors are used.
- All text fits without overlap at the target page size.
- Keep at least 40px between unrelated boxes and 80px between semantic layers.

## Common mistakes

| Symptom | Correction |
|---|---|
| Boxes crowd one side | Rebalance columns and use the rigid grid |
| Arrows cross node bodies | Use `routing="libavoid"` or split a hub node |
| Inheritance edges zigzag | Put all parents on one top layer |
| Sequence messages overlap | Keep a 48px vertical slot per message |
| Class boxes become walls | Keep at most 6 fields plus 6 methods |
| Diagram needs scrolling to follow | Split into multiple named pages |

## Reference

Read `references/layout-patterns.md` for mandatory class, flow, sequence,
swimlane, and architecture construction rules, including geometry grids and
final checks.

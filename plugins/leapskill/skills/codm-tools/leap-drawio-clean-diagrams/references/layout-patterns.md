# Layout patterns

## Contents

- Shared grid
- Class diagrams
- Flowcharts
- Sequence diagrams
- Swimlane / actor flows
- Architecture and ownership diagrams
- Final checks

## Shared grid

Use this grid unless the user explicitly needs a different spatial structure.

- Column x = `40 + 200 * col`
- Row y = `40 + 140 * row`
- Process box: `160x60`; decision: `160x80`; class: `180x120`; note: `140x50`
- Reserve one empty grid lane between semantic groups.

Do not compute a full-page coordinate table in prose. Place cells directly and
keep them on this grid.

## Class diagrams

Use a three-layer layout:

1. **Top:** abstract parents and interfaces
2. **Middle:** concrete owners and controllers
3. **Bottom / right:** data, jobs, managers, and infrastructure

Rules:

- One class box has at most 6 fields and 6 methods.
- Place inheritance edges vertically, parent above child.
- Place aggregation/composition edges horizontally, owner left of part.
- Use one relation arrow for one relationship; do not duplicate associations.
- Route dependency edges around boxes with `routing="libavoid"`; do not thread
  them through class bodies.
- If one class connects to more than five others, add an intermediate hub or
  split the class into a second page.

Use standard UML notation:

- Inheritance / realization: hollow triangle arrowhead
- Composition: filled diamond at owner
- Aggregation: hollow diamond at owner
- Dependency: dashed open arrow
- Association: solid open arrow

Class style:

```xml
<mxCell id="classA" value="&lt;b&gt;ClassName&lt;/b&gt;&lt;hr&gt;+ field: Type&lt;br&gt;+ method(): Result"
  style="swimlane;fontSize=12;align=left;startSize=26;whiteSpace=wrap;html=1;"
  vertex="1" parent="1">
  <mxGeometry x="40" y="40" width="180" height="120" as="geometry" />
</mxCell>
```

Keep the class name row separated from members; do not make one giant text
label without visual hierarchy.

## Flowcharts

Use a vertical main path and horizontal branches.

- Main path: one column, top to bottom.
- Decisions: directly under the step that produces the question.
- Success path: continue downward; labels `Yes` / `OK`.
- Failure or alternate path: leave from the right, then route downward.
- Loop-back: leave the left side and travel up the outer margin.
- Parallel starts: split into equal columns, then join before the next stage.

Rules:

- One node expresses one action or decision.
- A decision has at most three outgoing branches.
- Use a rhombus only for a real branch, never for a stage title.
- Use `edgeStyle=orthogonalEdgeStyle;rounded=1`.
- Do not use diagonal edges.
- Do not cross the main path with an alternate path.
- If the main path changes column more than twice, simplify the model or split
  stages into subgraphs.

Fan-out anchors:

- Left target: `entryX=0.25`
- Center target: `entryX=0.5`
- Right target: `entryX=0.75`
- Source exits from `exitX=0.5,exitY=1` unless geometry requires side exits

## Sequence diagrams

Participants:

- Order left to right by first appearance in the interaction.
- Put external actors at the far left.
- Put queues, schedulers, or infrastructure at the far right.
- Use consistent participant width, preferably `140`.
- Keep 80-120px between lifeline centers.

Messages:

- Reserve a 48px vertical slot per message.
- Messages only go downward in time.
- Put self-messages on the participant's own lifeline with a short right-side
  return stub.
- Use dashed open arrows for returns.
- Group a coherent phase (`Validation`, `Prepare`, `Dispatch`, `Consume`) in an
  activation rectangle; do not create a block for every two messages.
- Use `autonumber` semantics in labels only when ordering is not already clear.

Construction:

```xml
<mxCell id="participant" value="Name"
  style="shape=umlLifeline;perimeter=lifelinePerimeter;size=24;html=1;"
  vertex="1" parent="1">
  <mxGeometry x="40" y="40" width="140" height="760" as="geometry" />
</mxCell>
```

Messages may use fixed source and target points on lifeline centers. Keep
arrow labels above the line and never overlap activation bars.

## Swimlane / actor flows

Use flat lanes when one axis explains ownership or responsibility.

- Lane height: 150; lane title area: 110 for vertical lane titles.
- Node position inside lane: `x=120 + 180*col`, `y=45`.
- Do not nest swimlanes.
- Keep one row of nodes per lane; a lane is a responsibility strip, not a
  box container for arbitrary content.
- Cross-lane edges use `parent="1"`.

Use a cross-functional table only when both actor and phase must be visible.

## Architecture and ownership diagrams

Use containers for real ownership boundaries:

- External actors stay outside implementation containers.
- One container per deployable service, module, engine subsystem, or runtime
   boundary.
- Use `swimlane;startSize=24` for nested containers.
- Prefer one gateway / broker / manager hub when many edges converge.
- Put data stores on the right or bottom edge.
- Avoid drawing every dependency; show relationships that explain ownership,
  lifecycle, or primary data flow.

## Final checks

Before delivering:

- [ ] Diagram creation/editing went through `mcp__drawio` tools.
- [ ] The diagram has one obvious reading direction.
- [ ] Every visible label is readable and non-overlapping.
- [ ] No edge crosses through a node body.
- [ ] No unrelated boxes overlap.
- [ ] Each decision branch is labeled.
- [ ] One semantic color system is used consistently.
- [ ] Dense diagrams were previewed with `routing="libavoid"`.
- [ ] Multi-view models use one named page per view.
- [ ] Existing `.drawio` page edits used `list_pages` → `get_page` →
      `set_page`, preserving unrelated pages.

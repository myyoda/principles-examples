---
title: "Examples"
description: "Concrete examples demonstrating STAMPED principles in practice"
---

This section collects concrete, runnable examples that illustrate the
[STAMPED principles]({{< ref "stamped_principles" >}}) in action. Each
example focuses on a specific practice or workflow and shows how it
contributes to sound dataset version control.

## Taxonomy tags

Every example is tagged along four dimensions:

- **[STAMPED principles]({{< ref "stamped_principles" >}})** -- which of the seven principles
  ([Self-containment]({{< ref "stamped_principles/s" >}}), [Tracking]({{< ref "stamped_principles/t" >}}), [Actionability]({{< ref "stamped_principles/a" >}}), [Modularity]({{< ref "stamped_principles/m" >}}), [Portability]({{< ref "stamped_principles/p" >}}),
  [Ephemerality]({{< ref "stamped_principles/e" >}}), [Distributability]({{< ref "stamped_principles/d" >}})) the example demonstrates.
- **[FAIR mapping]({{< ref "fair_principles" >}})** -- which FAIR goals
  ([Findable]({{< ref "fair_principles/f" >}}), [Accessible]({{< ref "fair_principles/a" >}}), [Interoperable]({{< ref "fair_principles/i" >}}), [Reusable]({{< ref "fair_principles/r" >}})) the practice helps
  achieve.
- **[Instrumentation level]({{< ref "instrumentation_levels" >}})** -- how much tooling the example requires, from
  plain conventions to infrastructure-dependent workflows.
- **[Aspirational goals]({{< ref "aspirations" >}})** -- higher-level objectives the practice serves,
  such as [reproducibility]({{< ref "aspirations/reproducibility" >}}), [rigor]({{< ref "aspirations/rigor" >}}), or [transparency]({{< ref "aspirations/transparency" >}}).

Most examples carry tags in several dimensions, because good practices tend
to serve multiple goals at once.

## Browsing

You can explore the examples in several ways:

- **Scroll below** to see the full list on this page.
- **Use the navigation** to filter by any single taxonomy -- for example,
  view all examples related to the Tracking principle or all examples at a
  particular instrumentation level.
- **Use the search bar** to find examples by keyword.

## Difficulty range

Examples are arranged to cover a spectrum of complexity:

- **Beginner** -- simple conventions and [directory layouts]({{< ref "instrumentation_levels/data-organization" >}}) that require no
  special tools.
- **Intermediate** -- practices that use lightweight scripts, checksums, or
  standard [Git features]({{< ref "instrumentation_levels/tool" >}}).
- **Advanced** -- [workflows]({{< ref "instrumentation_levels/workflow" >}}) involving specialized tools (DataLad, DVC,
  Git-annex) or multi-step pipelines demonstrating several [patterns]({{< ref "instrumentation_levels/pattern" >}})
  together.

Pick the level that matches your current setup and expand from there.

## Example states

Each example has a `state` field in its front matter indicating its editorial status:

| State | Meaning |
|---|---|
| `uncurated-ai` | AI-generated draft that has not yet been reviewed by a human. Details may be inaccurate or incomplete. |
| `wip` | Work in progress — under active development, content may be incomplete or change significantly. |
| `final` | Reviewed, curated, and ready for use. No banner is shown. |

Examples without a `state` field (or with `state: final`) are considered ready.

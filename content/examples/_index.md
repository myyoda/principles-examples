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

- **STAMPED principles** -- which of the seven principles
  (Self-containment, Tracking, Actionability, Modularity, Portability,
  Ephemerality, Distributability) the example demonstrates.
- **FAIR mapping** -- which [FAIR]({{< ref "fair_principles" >}}) goals
  (Findable, Accessible, Interoperable, Reusable) the practice helps
  achieve.
- **Instrumentation level** -- how much tooling the example requires, from
  plain conventions to infrastructure-dependent workflows.
- **Aspirational goals** -- higher-level objectives the practice serves,
  such as reproducibility, collaboration, or scalability.

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

- **Beginner** -- simple conventions and directory layouts that require no
  special tools.
- **Intermediate** -- practices that use lightweight scripts, checksums, or
  standard Git features.
- **Advanced** -- workflows involving specialized tools (DataLad, DVC,
  Git-annex) or multi-step pipelines demonstrating several principles
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

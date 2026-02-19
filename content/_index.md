---
title: "STAMPED Principles — Examples"
description: "Concrete examples demonstrating the STAMPED principles for idiomatic dataset version control"
---

This site is a companion resource to our paper on idiomatic dataset version
control. It provides concrete, pragmatic examples that demonstrate the seven
**STAMPED** principles in practice -- from simple naming conventions to complex
multi-tool workflows.

## What is STAMPED?

STAMPED is an acronym for seven complementary principles that together describe
what it means to manage datasets as carefully as we manage source code:

| Principle | Core idea |
|---|---|
| **[S]({{< ref "stamped_principles/s" >}})** -- [Self-containment]({{< ref "stamped_principles/s" >}}) | A dataset carries everything needed to understand and use it -- metadata, provenance, and documentation travel with the data. |
| **[T]({{< ref "stamped_principles/t" >}})** -- [Tracking]({{< ref "stamped_principles/t" >}}) | Every change is tracked with full provenance: who, when, why, and how. |
| **[A]({{< ref "stamped_principles/a" >}})** -- [Actionability]({{< ref "stamped_principles/a" >}}) | Dataset operations are recorded in an executable form, not just documented. |
| **[M]({{< ref "stamped_principles/m" >}})** -- [Modularity]({{< ref "stamped_principles/m" >}}) | Datasets are composed from independent, reusable components that can be versioned separately. |
| **[P]({{< ref "stamped_principles/p" >}})** -- [Portability]({{< ref "stamped_principles/p" >}}) | The logical structure of a dataset is independent of where and how the data is physically stored. |
| **[E]({{< ref "stamped_principles/e" >}})** -- [Ephemerality]({{< ref "stamped_principles/e" >}}) | Derived and regenerable content is treated as ephemeral, keeping repositories lean and focused on irreplaceable data. |
| **[D]({{< ref "stamped_principles/d" >}})** -- [Distributability]({{< ref "stamped_principles/d" >}}) | Datasets support decentralized workflows -- cloning, forking, pushing, and pulling -- with efficient transfer. |

These principles are not independent checkboxes; they reinforce one another.
Self-containment makes portability practical, tracking enables actionability,
and modularity supports distributability.

## How examples are organized

Each example on this site is tagged along multiple dimensions so you can
explore the collection from whatever angle is most useful to you:

- **[STAMPED principles]({{< ref "stamped_principles" >}})** -- which of the seven principles does the example
  primarily demonstrate?
- **[FAIR mapping]({{< ref "fair_principles" >}})** -- which of the FAIR
  goals ([Findable]({{< ref "fair_principles/f" >}}), [Accessible]({{< ref "fair_principles/a" >}}), [Interoperable]({{< ref "fair_principles/i" >}}), [Reusable]({{< ref "fair_principles/r" >}})) does the practice
  help achieve?
- **[Instrumentation level]({{< ref "instrumentation_levels" >}})** -- how much tooling does the example require,
  from plain conventions that need no special software to workflows that
  depend on specific version-control infrastructure?
- **[Aspirational goals]({{< ref "aspirations" >}})** -- what higher-level objectives ([reproducibility]({{< ref "aspirations/reproducibility" >}}),
  [transparency]({{< ref "aspirations/transparency" >}}), [rigor]({{< ref "aspirations/rigor" >}}), [efficiency]({{< ref "aspirations/efficiency" >}})) does the practice serve?

## Get started

Head to the [Examples]({{< ref "examples" >}}) section to browse the full
collection. You can also explore by taxonomy using the footer links, or use
the search bar to find examples relevant to your needs.

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
| **S** -- Self-containment | A dataset carries everything needed to understand and use it -- metadata, provenance, and documentation travel with the data. |
| **T** -- Tracking | Every change is tracked with full provenance: who, when, why, and how. |
| **A** -- Actionability | Dataset operations are recorded in an executable form, not just documented. |
| **M** -- Modularity | Datasets are composed from independent, reusable components that can be versioned separately. |
| **P** -- Portability | The logical structure of a dataset is independent of where and how the data is physically stored. |
| **E** -- Ephemerality | Derived and regenerable content is treated as ephemeral, keeping repositories lean and focused on irreplaceable data. |
| **D** -- Distributability | Datasets support decentralized workflows -- cloning, forking, pushing, and pulling -- with efficient transfer. |

These principles are not independent checkboxes; they reinforce one another.
Self-containment makes portability practical, tracking enables actionability,
and modularity supports distributability.

## How examples are organized

Each example on this site is tagged along multiple dimensions so you can
explore the collection from whatever angle is most useful to you:

- **STAMPED principles** -- which of the seven principles does the example
  primarily demonstrate?
- **FAIR mapping** -- which of the [FAIR]({{< ref "fair_principles" >}})
  goals (Findable, Accessible, Interoperable, Reusable) does the practice
  help achieve?
- **Instrumentation level** -- how much tooling does the example require,
  from plain conventions that need no special software to workflows that
  depend on specific version-control infrastructure?
- **Aspirational goals** -- what higher-level objectives (reproducibility,
  collaboration, scalability, etc.) does the practice serve?

## Get started

Head to the [Examples]({{< ref "examples" >}}) section to browse the full
collection. You can also explore by taxonomy using the footer links, or use
the search bar to find examples relevant to your needs.

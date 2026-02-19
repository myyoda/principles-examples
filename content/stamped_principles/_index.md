---
title: "STAMPED Principles"
description: "The seven principles for idiomatic dataset version control"
---

The **STAMPED** principles provide a framework for evaluating and designing
dataset version control systems. Introduced in our paper on idiomatic dataset
version control, the acronym captures seven complementary principles that
together describe what it means to manage datasets as carefully as we manage
source code.

Each letter stands for one principle:

- **S -- [Self-containment](s/)**: A dataset should include everything needed
  to understand and use its contents -- metadata, provenance, and documentation
  travel with the data.

- **T -- [Tracking](t/)**: All changes should be tracked with full provenance,
  recording who made each change, when, why, and how.

- **A -- [Actionability](a/)**: Dataset operations should be executable, not
  just documented -- the actual commands and workflows are recorded in a
  re-executable form.

- **M -- [Modularity](m/)**: Datasets should be composable from independent,
  reusable components that can be independently versioned and maintained.

- **P -- [Portability](p/)**: The logical structure of a dataset should be
  independent of where and how the data is physically stored.

- **E -- [Ephemerality](e/)**: Derived and regenerable content should be
  treated as ephemeral, keeping repositories lean and focused on irreplaceable
  data.

- **D -- [Distributability](d/)**: Datasets should support decentralized
  workflows -- cloning, forking, pushing, and pulling -- with efficient
  transfer of only the changes needed.

These principles are not independent checkboxes; they reinforce one another.
Self-containment makes portability practical, tracking enables actionability,
and modularity supports distributability. The examples on this site illustrate
how concrete tools and workflows embody these principles in practice.

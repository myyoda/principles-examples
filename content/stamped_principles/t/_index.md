---
title: "T — Tracking"
description: "All changes to a dataset should be tracked with full provenance"
---

All changes to a dataset should be **tracked with full provenance**. Every
modification, addition, or deletion is recorded -- who made the change, when,
why, and how. This goes beyond simple version control to include the
computational provenance of derived data.

Tracking means that the history of a dataset is not just a sequence of
snapshots, but a rich record of the reasoning and processes behind each change.
When a file is updated, the commit message explains the intent; when a derived
file is produced, the command that generated it is recorded alongside the result.

This principle enables reproducibility at the dataset level. Given any past
version, you can understand not only what the data looked like, but the full
chain of decisions and transformations that brought it to that state.

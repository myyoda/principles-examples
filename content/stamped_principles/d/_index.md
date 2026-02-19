---
title: "D — Distributability"
description: "Datasets should be designed for distribution across locations and contributors"
---

Datasets should be designed for **distribution across locations and
contributors**. Like distributed version control for code, dataset version
control should support decentralized workflows -- cloning, forking, pushing,
pulling -- with efficient transfer of only the changes needed.

Distributability means that no single server or institution is the sole point of
access for a dataset. Contributors at different sites can maintain their own
copies, work independently, and synchronize changes when ready. This mirrors the
workflow that made Git successful for code collaboration, extended to the
challenges of large-file data management.

This principle supports both collaboration and resilience. Distributed copies
protect against data loss from any single point of failure, while decentralized
workflows allow teams to work without constant connectivity to a central server.
Efficient transfer mechanisms ensure that synchronization moves only the data
that has actually changed, keeping network costs practical even for large
datasets.

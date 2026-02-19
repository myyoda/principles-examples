---
title: "Reproducibility"
description: "The ability to reproduce results exactly -- re-running the same analysis on the same data yields identical outcomes"
---

Reproducibility is the cornerstone aspiration of scientific data management. A result is reproducible when re-running the same analysis on the same data yields identical outcomes. This requires:

- **Fixed inputs** -- The exact data used in an analysis must be identified and retrievable.
- **Captured computation** -- The code, software environment, parameters, and execution order must be recorded.
- **Deterministic execution** -- Given the same inputs and computation, the outputs must be the same.

STAMPED principles support reproducibility through version control (pinning exact states of data and code), provenance tracking (recording what was run and how), containerization (freezing computational environments), and modular dataset organization (making it possible to re-assemble all components of an analysis). When every element of an analysis is tracked and versioned, reproduction becomes a matter of checking out the right state and re-executing.

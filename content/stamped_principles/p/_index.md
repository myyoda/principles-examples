---
title: "P — Portability"
description: "Datasets should be portable across storage backends and infrastructure"
---

Datasets should be **portable across storage backends and infrastructure**. The
logical structure -- files, versions, metadata -- should be independent of where
and how the data is physically stored. Moving data between local disk,
institutional storage, and cloud should not require restructuring.

Portability decouples the identity of a dataset from the infrastructure that
hosts it. A dataset organized according to this principle can live on a
researcher's laptop during development, move to a high-performance cluster for
analysis, be archived in an institutional repository for long-term preservation,
and be mirrored to cloud storage for broad access -- all without changing its
internal organization.

This principle is especially important for longevity. Storage technologies and
institutional infrastructure change over time, but a portable dataset can
migrate between them without losing its structure, history, or meaning.

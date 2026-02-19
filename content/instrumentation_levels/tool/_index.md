---
title: "Tool"
description: "Specific software tools that implement data management principles -- single-purpose utilities"
---

The Tool instrumentation level involves adopting specific software that implements one or more data management principles. These are typically single-purpose utilities that address particular needs:

- **git** -- Version control for code and small files, providing history tracking and collaboration.
- **git-annex** -- Large file management integrated with git, enabling tracking of files without storing them directly in the repository.
- **DataLad** -- A data management tool built on git and git-annex that adds dataset nesting, provenance capture, and streamlined access to remote data.
- **containers (Docker, Singularity/Apptainer)** -- Computational environment encapsulation for reproducibility.
- **make, doit, snakemake** -- Build systems and task runners for automating data processing steps.

Adopting individual tools is a natural next step after establishing good data organization. Each tool addresses a specific gap -- version control, large file handling, environment reproducibility -- and can be introduced incrementally.

---
title: "M — Modularity"
description: "Datasets should be composable from independent, reusable components"
---

Datasets should be **composable from independent, reusable components**. A large
project dataset can nest smaller datasets as modules, each independently
versioned and maintained. This enables sharing common resources across projects
without duplication.

Modularity recognizes that real-world data management rarely involves a single
monolithic collection. A neuroimaging study might share a common set of
stimuli with other studies; a machine learning project might combine several
benchmark datasets with custom annotations. Rather than copying shared data into
each project, modular datasets link to their components while preserving each
component's independent identity and version history.

This principle supports both reuse and scalability. Individual components can be
updated, cited, and distributed on their own terms, while composite datasets
assemble them into coherent wholes.

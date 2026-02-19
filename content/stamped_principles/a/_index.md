---
title: "A — Actionability"
description: "Dataset operations should be executable, not just documented"
---

Dataset operations should be **executable, not just documented**. Rather than
describing how data was processed in a README, the actual commands and workflows
should be recorded in a form that can be re-executed. A dataset should carry its
own "recipes."

Actionability bridges the gap between documentation and reproducibility. A
README that says "we normalized the data using a custom Python script" is
informative; a dataset that contains the script, records the exact command that
was run, and can re-execute that command to regenerate the output is actionable.

This principle transforms datasets from passive archives into active,
reproducible artifacts. When provenance is recorded as executable steps rather
than prose descriptions, anyone with access to the dataset can verify or rebuild
its derived contents.

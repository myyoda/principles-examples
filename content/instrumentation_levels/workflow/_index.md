---
title: "Workflow"
description: "Multi-step pipelines combining tools into orchestrated sequences for data processing, analysis, and publication"
---

The Workflow instrumentation level combines multiple tools into coordinated, multi-step pipelines. Rather than using tools in isolation, workflows define how data flows through a sequence of processing, analysis, and publication steps.

Characteristics of workflow-level instrumentation:

- Multiple tools are chained together in a defined order.
- Inputs and outputs of each step are explicitly declared.
- Execution can be partially or fully automated.
- Provenance is captured across the entire pipeline, not just individual steps.
- Workflows can be re-run to reproduce results or updated when inputs change.

Examples include using DataLad's `run` and `rerun` commands to capture entire analysis pipelines, CI/CD systems that automatically validate data upon submission, and orchestration tools like Nextflow or Snakemake that manage complex dependency graphs across compute environments.

---
title: "About"
description: "About the STAMPED Principles Examples resource"
---

## Companion to the STAMPED paper

This site is the companion resource to our paper on idiomatic dataset version
control. While the paper develops the theoretical framework and evaluates
existing tools against it, this site provides the practical side: concrete,
runnable examples that show how the principles look when applied to real data
management tasks.

## STAMPED and YODA

The [YODA principles](https://handbook.datalad.org/en/latest/basics/101-127-yoda.html)
(YODA's Organigram on Data Analysis) established foundational conventions for
structuring DataLad datasets. STAMPED extends and generalizes those ideas
beyond any single tool:

- Where YODA focuses on DataLad dataset organization, STAMPED captures the
  underlying **principles** that make YODA effective and expresses them in a
  tool-agnostic way.
- STAMPED adds principles (such as Ephemerality and Distributability) that were
  implicit in YODA practice but not explicitly named.
- By decoupling the principles from a specific tool, STAMPED provides a
  vocabulary for evaluating *any* dataset management approach -- whether built
  on DataLad, DVC, Git LFS, Hugging Face Datasets, or plain Git with
  conventions.

## Multi-dimensional taxonomy

Examples on this site are organized along four independent dimensions:

1. **STAMPED principles** -- Self-containment, Tracking, Actionability,
   Modularity, Portability, Ephemerality, and Distributability.
2. **FAIR mapping** -- which of the FAIR goals (Findable, Accessible,
   Interoperable, Reusable) the practice supports.
3. **Instrumentation level** -- ranging from conventions that require no
   special tooling, through lightweight tools, to full version-control
   infrastructure.
4. **Aspirational goals** -- higher-level objectives such as reproducibility,
   collaboration, scalability, and long-term preservation.

An example may be tagged with multiple values in each dimension. A README
convention, for instance, supports Self-containment *and* Findability *and*
Reusability while requiring no special instrumentation.

## Range of examples

Examples span a wide range of complexity:

- **Simple conventions** -- directory layouts, naming schemes, README templates
  that require nothing more than discipline.
- **Lightweight practices** -- using checksums, manifests, or small scripts to
  add provenance without heavy infrastructure.
- **Tool-assisted workflows** -- leveraging Git, Git-annex, DataLad, DVC, or
  similar tools for automated tracking and distribution.
- **Advanced pipelines** -- multi-step, multi-tool workflows that demonstrate
  several STAMPED principles working together.

## Contributing

We welcome contributions of new examples, corrections, and improvements.
The source for this site lives at
<https://github.com/myyoda/principles-examples>. To contribute:

1. Fork the repository.
2. Add or edit example pages under `content/examples/`.
3. Tag your example with the appropriate STAMPED principles, FAIR mappings,
   instrumentation level, and aspirational goals in the front matter.
4. Open a pull request with a brief description of what the example
   demonstrates.

See the repository README for details on front-matter fields and the
taxonomy values available.

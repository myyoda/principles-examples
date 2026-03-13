---
title: "Walkthrough: stellar distances from Gaia parallax"
date: 2026-03-12
description: "A step-by-step walkthrough building a STAMPED research object that computes stellar distances from Gaia DR3 parallax data"
summary: "Incrementally builds a research object from a bare script to a tracked, portable, reproducible pipeline — motivated by real problems, not by acronym order."
tags: ["gaia", "parallax", "walkthrough", "python", "datalad", "make"]
stamped_principles: ["S", "T", "A", "M", "P", "E", "D"]
fair_principles: ["R", "A"]
instrumentation_levels: ["workflow"]
aspirations: ["reproducibility", "rigor", "transparency"]
params:
  tools: ["python", "git", "datalad", "make"]
  difficulty: "beginner"
  verified: true
---

## What we're building

Most research code starts the same way: a script that works, on your machine, right now.
That's not a problem — it's a starting point.

In this walkthrough we take a real analysis — computing distances to nearby stars from European Space Agency data — and turn it into something anyone can verify, reproduce, and build on.
No new frameworks to learn.
No heavyweight infrastructure.
Just a series of small, practical steps, each one solving a concrete problem you've probably already run into: "which version of the data did I use?", "why doesn't this run on my colleague's laptop?", "how do I prove these numbers are right?"

Along the way, we'll point out which STAMPED properties each step improves.
By the end, you'll have a research object that passes a from-scratch reproduction test in a throwaway directory — and you'll see that most of the steps are things you might already be doing, just named and organized.

**The science**: we compute the distance to 100 nearby stars using parallax measurements from the [Gaia DR3](https://www.cosmos.esa.int/web/gaia/dr3) catalog.
The math is one line: `distance_pc = 1000 / parallax_mas`.
The result is a CSV of stellar distances in parsecs — verified against Gaia's own pipeline estimates to within 0.3%.

The analysis is deliberately simple so the focus stays on *how* we organize, track, and share the work.

**Repository**: [TODO: link to GitHub repo]

## Steps

### 1. Proof of concept

Write a single Python script that queries the Gaia TAP API, fetches parallax for 100 nearby stars, computes `distance_pc = 1000 / parallax`, and writes a CSV.
Run it.
Get a result.
Done.

This is where most analyses live forever — and that's fine for exploration.
But what happens when you come back in six months and can't remember which query parameters you used?
When a collaborator asks "how do I run this?" and the answer is "well, first you need to install..."?
When a reviewer asks you to recompute with updated data?

Each step that follows addresses one of these failure modes.

*We committed this so you can see it, but in real life this might just be a loose file on your desktop.*

**Commit**: [`0d95ecc`](0d95ecc)

### 2. Gather everything under one roof

Put all files in a single project directory.

This sounds obvious, but it's the foundation everything else builds on.
Right now the script and its output are loose files — a collaborator would need to know which ones go together.
A project directory draws a boundary: everything inside is part of this work, and nothing outside should be needed.
STAMPED calls this the "don't look up" rule (S.1): a research object must never rely on implicit external state.

**Advances**: S (everything reachable from one root)

### 3. Organize into directories

Separate `code/`, `raw/`, `output/`.
Code is what you write.
Raw is what you fetch.
Output is what you compute.

This tells you the role of each file at a glance.
When something breaks, you know where to look.
We also split the monolithic script into two: one that fetches data, one that computes distances.
Each piece is now independently testable and replaceable — Modularity at its simplest.

**Advances**: M (logical separation of concerns), S (clearer boundary)

**Commit**: [`5d7c7fc`](5d7c7fc) (steps 2 and 3 combined)

### 4. Write a README

Explain what this project does, what the inputs and outputs are, and how to run it.

Without a README, the project is only usable by the person who wrote it — and only while they remember how.
A README makes it usable by anyone who can read.
This is the minimum viable Actionability (A.1): sufficient instructions to reproduce all results.

**Advances**: A (someone can now follow instructions to reproduce), S (project is self-describing)

**Commit**: [`7c92a7f`](7c92a7f)

### 5. Initialize version control

`git init`. Add everything. First commit.

From now on, every change is recorded: who, when, what, and (in the commit message) why.
You can always get back to any previous state.

Each commit hash is a fingerprint of the entire project state — not a label like "version 1.0" that two people could apply to different things, but a cryptographic checksum that two people with the same hash provably have the same content.
Version control is also the safety net that makes every subsequent step low-risk: if something goes wrong, you can always revert.

**Advances**: T (content identification, change history)

*In the companion repository, we initialized git from the start so each step has its own commit. In your own work, this is the point where you'd run `git init`.*

### 6. Write a Makefile

Encode the pipeline as `make` targets: `raw/gaia_nearby.csv` depends on `code/fetch_data.py`, `output/distances.csv` depends on `raw/gaia_nearby.csv` and `code/compute_distances.py`.
`make` runs the whole thing.

The README *says* how to run the pipeline.
The Makefile *does* it.
This is the jump from documented to executable — the Actionability spectrum in action (A.2).
Make also encodes dependencies: it knows what to re-run when an input changes, which is itself a lightweight form of provenance.

**Advances**: A (executable specification — not just documentation but a runnable recipe)

**Commit**: [`84ba4a5`](84ba4a5)

### 7. Add a test

Write a verification script that fetches independent reference distances from Gaia's GSP-Phot pipeline and compares them to our computed values.
`make test` runs it.
48 of 100 stars have reference values; all match within 0.3%.

A research object without verification asks others to trust the results.
A test makes the claim falsifiable — anyone can run `make test` and see for themselves.

An interesting detail: only 48 of our 100 stars have GSP-Phot distances, because Gaia's sophisticated pipeline doesn't produce estimates for every star.
Our simple one-line formula actually covers more stars than the pipeline does.

**Advances**: A (verifiable results, not just "trust me")

**Commit**: [`2a6cd40`](2a6cd40)

### 8. Declare dependencies

Add `pyproject.toml` listing the Python packages we use (`requests`).

Until now, the scripts used only Python's standard library.
When we rewrote the fetch script to use `requests` (cleaner API, better error handling), we introduced an external dependency.
Without declaring it, a fresh machine fails with `ModuleNotFoundError: No module named 'requests'` — a Portability failure that only surfaces when someone else tries to run the code.
`pyproject.toml` makes that assumption explicit.

**Advances**: P (host assumptions are now documented, not implicit)

**Commit**: [`ed1900b`](ed1900b)

### 9. Pin dependency versions

Generate `requirements.txt` with exact versions and cryptographic hashes using `pip-compile --generate-hashes`.

There's a big difference between `requests` (any version) and `requests==2.32.5 --hash=sha256:...` (this exact build).
The first is a declaration — it says what you need.
The second is a distribution-ready specification — it says exactly what bytes to install.
Hash pinning means that even if a package is re-uploaded with the same version number, the install will reject it rather than silently using different code.
This is where Portability meets Tracking: the environment specification itself is content-addressed.

**Advances**: P (reproducible environment), T (pinned versions are content-addressed)

**Commit**: [`4e63464`](4e63464)

### 10. Record provenance with datalad run

Wrap the fetch and analysis commands with `datalad run`, which records the exact command, inputs, and outputs as machine-readable metadata in each commit.

A regular git commit says "these files changed."
A `datalad run` commit says "these files changed *because this command was run with these inputs and produced these outputs*."
The run record is JSON embedded in the commit message — machine-readable, not just human-readable.
And because the record is executable, anyone can replay it with `datalad rerun`.

`datalad run` works on plain git repositories — no special dataset initialization or git-annex required.

**Advances**: T (programmatic provenance), A (provenance records are executable specifications)

**Commits**: [`28795f6`](28795f6) (fetch), [`277e8b7`](277e8b7) (compute)

### 11. Push to GitHub

`git push` to a public repository.
Now anyone can `git clone`, `pip install -r requirements.txt`, `make`, and reproduce the result.

Until this step, the research object was self-contained and reproducible — but only on your machine.
Publishing crosses the Distributability threshold (D.1): all components become persistently retrievable by others.

Note that GitHub is hosting, not archival.
For long-term persistence, the next step would be depositing on Zenodo or Software Heritage (see "Where to go from here").

**Advances**: D (persistently retrievable by others)

**Commit**: [TODO: after GitHub push]

### 12. Reproduce from scratch

Write a script that clones the repository into a fresh temp directory, installs dependencies, runs the pipeline, and runs the tests.
If it passes, the research object doesn't depend on anything from your machine — no accumulated state, no forgotten steps.
The temp directory is thrown away afterward.

This is the ultimate integration test for a research object.
Ephemeral reproduction exercises almost every STAMPED property at once: the project must be self-contained (S), the pipeline must actually run (A), it must work in a fresh environment (P), and there's no prior state to lean on (E).
If `reproduce_from_scratch.sh` passes, you have strong evidence that your research object is solid.
If it fails, the error message tells you which property broke.

This is the [ephemeral shell reproducer]({{< ref "examples/ephemeral-shell-reproducer" >}}) pattern applied to our own project.

**Advances**: E (results produced without prior state), A (reproduction is a single command), S (validates that nothing outside the boundary is needed)

**Commit**: [`362ad10`](362ad10)

## STAMPED scorecard

| Property | Where we ended up |
|---|---|
| **S** Self-contained | All code, data, and instructions under one root. README describes the project. |
| **T** Tracked | Git tracks all changes. `datalad run` records provenance per computation. Dependencies hash-pinned. |
| **A** Actionable | `make` reproduces results. `make test` verifies. `datalad rerun` replays provenance. README documents the workflow. |
| **M** Modular | code/, raw/, output/, test/ are logically separated. |
| **P** Portable | Dependencies declared in pyproject.toml, pinned in requirements.txt with hashes. No hardcoded paths. |
| **E** Ephemeral | Reproduction script runs the full pipeline in a fresh temp directory with no prior state. |
| **D** Distributable | Repository on GitHub. Anyone can clone and reproduce. |

## Where to go from here

Each STAMPED property is a spectrum.
We've built something solid, but there are natural next steps depending on what your project needs.

**Containers for portability and ephemerality**:
A Dockerfile (pinned by image digest) freezes the OS and Python version.
Running the pipeline inside a disposable container validates that the specifications are complete — if it works in a fresh container, it's not relying on anything from your machine.
See [Container venv overlay for Python development]({{< ref "examples/container-venv-overlay-development" >}}) for a detailed treatment of this pattern.

**CI for ephemeral validation**:
A GitHub Actions workflow that clones, installs, and runs `make test` on every push.
This catches environment drift automatically.

**Modularity via subdatasets**:
The raw data could live in its own DataLad subdataset, independently versioned and reusable.
A colleague running a different analysis on the same stars would `datalad install` the data module rather than re-fetching from the API.

**Reproducible re-execution**:
`datalad rerun` replays the recorded provenance.
If the raw data is updated (say, a new Gaia release), update the input, `datalad rerun`, and the outputs reflect the new data.
Branches can separate outputs produced from different input versions.

**Archival distribution**:
Deposit the repository on [Zenodo](https://zenodo.org/) for a DOI.
Push the container image to a registry.
Mirror data to multiple remotes so no single point of failure breaks reproducibility.

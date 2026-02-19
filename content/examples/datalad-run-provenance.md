---
title: "Recording Computational Provenance with datalad run"
date: 2026-02-19
description: "Using datalad run to automatically capture full computational provenance of data transformations"
summary: "Shows how datalad run wraps arbitrary commands to record inputs, outputs, and the exact command in machine-reexecutable form."
tags: ["datalad", "provenance", "reproducibility"]
stamped_principles: ["T", "A"]
fair_principles: ["R"]
instrumentation_levels: ["tool"]
aspirations: ["reproducibility", "transparency"]
params:
  tools: ["datalad", "git"]
  difficulty: "intermediate"
  verified: false
state: uncurated-ai
---

## The problem: undocumented transformations

A depressingly common scenario in data-intensive research looks like this:

1. A researcher downloads raw data into `data/raw/`.
2. They write a Python script that cleans and transforms it.
3. They run the script from the command line, perhaps tweaking flags along
   the way.
4. The cleaned output lands in `data/processed/`.
5. Six months later, a reviewer asks: "How exactly was the processed data
   generated?"

The researcher checks their notes.  The script is there, but which version
was actually run?  What arguments were passed?  Were the raw inputs the
same files that are in the repository now, or were they updated since then?
The answers are not recorded anywhere because the transformation was run
"by hand" -- outside the version control system.

This is a **provenance gap**: the data is versioned, but the *process*
that produced it is not.

## The solution: `datalad run` wraps commands with provenance

DataLad's `run` command solves this by acting as a thin wrapper around any
shell command.  Instead of running your script directly, you run it
*through* `datalad run`, which:

1. Records the exact command string.
2. Records which files were used as inputs.
3. Records which files were produced as outputs.
4. Executes the command.
5. Saves the result as a Git commit with a structured, machine-readable
   run record.

The result is a commit that is not merely "some files changed" but a
complete, re-executable recipe: what was run, on what, producing what.

## Concrete example: converting DICOM to NIfTI

Suppose you have a neuroimaging dataset following YODA conventions:

```
my-study/
  code/
    convert.py          # DICOM-to-NIfTI conversion script
  inputs/
    dicoms/             # raw DICOM files (submodule or subdataset)
      sub-01/
      sub-02/
  outputs/
    nifti/              # will hold converted NIfTI files
```

### Running without provenance (the old way)

```bash
python code/convert.py inputs/dicoms/ outputs/nifti/
git add outputs/nifti/
git commit -m "Convert DICOM to NIfTI"
```

This records *that* something changed, but not *how*.  The commit message
is prose, not a machine-readable recipe.

### Running with `datalad run` (the provenance-aware way)

```bash
datalad run \
  -m "Convert DICOM to NIfTI" \
  -i "inputs/dicoms/" \
  -o "outputs/nifti/" \
  "python code/convert.py inputs/dicoms/ outputs/nifti/"
```

Let us break down the flags:

| Flag | Purpose |
|------|---------|
| `-m "Convert DICOM to NIfTI"` | Human-readable commit message |
| `-i "inputs/dicoms/"` | Declare input files -- DataLad will `get` them if not yet available |
| `-o "outputs/nifti/"` | Declare output files -- DataLad will unlock them before the command runs and save them afterward |
| `"python code/convert.py ..."` | The actual command to execute |

DataLad executes the command, then creates a commit that bundles two
things: the usual file changes *and* a machine-readable run record.

## Anatomy of the resulting commit

After `datalad run` finishes, `git log -1` shows something like:

```
commit a1b2c3d4e5f6...
Author: Jane Researcher <jane@university.edu>
Date:   Wed Feb 19 14:30:00 2026 +0000

    [DATALAD RUNCMD] Convert DICOM to NIfTI

    === Do not change lines below ===
    {
     "chain": [],
     "cmd": "python code/convert.py inputs/dicoms/ outputs/nifti/",
     "dsid": "abcd1234-5678-...",
     "exit": 0,
     "extra_inputs": [],
     "inputs": ["inputs/dicoms/"],
     "outputs": ["outputs/nifti/"],
     "pwd": "."
    }
    ^^^ Do not change lines above ^^^
```

The block between the delimiters is a JSON run record embedded directly in
the commit message.  It contains:

| Field | Meaning |
|-------|---------|
| `cmd` | The exact command string that was executed |
| `inputs` | Files/directories the command read from |
| `outputs` | Files/directories the command wrote to |
| `exit` | The exit code of the command (0 = success) |
| `pwd` | The working directory relative to the dataset root |
| `dsid` | The unique identifier of the dataset |

This run record is what makes the commit **actionable** rather than merely
informative.  It is not just a note saying "files were converted" -- it is
a complete recipe that can be re-executed mechanically.

## How `datalad run` satisfies STAMPED principles

### Tracking (T)

The run record captures the full provenance chain:

- **What** was run: the exact command string.
- **On what inputs**: the declared input files.
- **Producing what outputs**: the declared output files.
- **With what result**: the exit code.
- **When**: the commit timestamp.
- **By whom**: the commit author.

This is far richer than a manual `git commit -m "processed data"`.

### Actionability (A)

Because the run record is structured and machine-readable, it is not just
documentation -- it is an executable specification.  DataLad can parse the
run record from any commit and re-execute the exact command using
`datalad rerun` (covered in a [separate example]({{< ref
"examples/datalad-rerun-actionability" >}})).

## Handling large files transparently

When DataLad is used with git-annex (its default configuration for binary
files), `datalad run` integrates seamlessly:

1. **Before execution**: `-i` flags trigger `datalad get` to ensure input
   files are present locally.  If they are stored in a remote annex, they
   are fetched on demand.
2. **Before execution**: `-o` flags trigger `datalad unlock` on output
   files so they can be overwritten.
3. **After execution**: DataLad adds the new/changed output files to
   git-annex and commits them.

This means `datalad run` works correctly even when your dataset is
partially cloned and most files exist only as lightweight annex pointers.

## A more complex example: multi-step pipeline

Real analyses often involve several steps.  Each step can be a separate
`datalad run` invocation, building a chain of provenance:

```bash
# Step 1: Preprocess raw data
datalad run \
  -m "Preprocess: normalize and filter" \
  -i "inputs/raw/*.csv" \
  -o "outputs/preprocessed/*.csv" \
  "python code/preprocess.py inputs/raw/ outputs/preprocessed/"

# Step 2: Run statistical analysis
datalad run \
  -m "Analyze: compute group statistics" \
  -i "outputs/preprocessed/*.csv" \
  -o "outputs/statistics/results.json" \
  "python code/analyze.py outputs/preprocessed/ outputs/statistics/results.json"

# Step 3: Generate figures
datalad run \
  -m "Plot: generate publication figures" \
  -i "outputs/statistics/results.json" \
  -o "outputs/figures/*.pdf" \
  "python code/plot.py outputs/statistics/results.json outputs/figures/"
```

Each step produces a commit with a run record.  The full pipeline is
captured in the Git history as a sequence of machine-readable,
re-executable steps.  A colleague can read the `git log` to understand
not just what files exist, but the exact chain of computations that
produced them.

## Practical tips

### Use glob patterns in `-i` and `-o`

DataLad supports glob patterns for input and output specifications.  This
is useful when you do not know the exact filenames in advance:

```bash
datalad run -i "inputs/scans/sub-*/*.dcm" -o "outputs/nifti/sub-*/*.nii.gz" ...
```

### Keep the command self-contained

The command string should be self-contained: it should not rely on shell
variables, aliases, or environment-specific paths.  Anyone re-running the
command on a different machine should get the same result (assuming the
same software versions).

Good:
```bash
datalad run -m "Convert" "python code/convert.py inputs/ outputs/"
```

Avoid:
```bash
datalad run -m "Convert" "$MY_SCRIPT $INPUT_DIR $OUTPUT_DIR"
```

### Declare all inputs and outputs explicitly

It is tempting to omit `-i` and `-o` and let DataLad simply commit
whatever changes.  This works mechanically but loses the key provenance
benefit: the run record will not list what the command consumed and
produced.  Always declare inputs and outputs explicitly for maximum
provenance value.

## Connection to `datalad rerun`

A `datalad run` commit is useful on its own as documentation, but its real
power is that it can be **re-executed** using `datalad rerun`.  This
enables verification ("do I get the same results?") and updating
("I changed an input; rerun the pipeline").  See the
[datalad rerun example]({{< ref "examples/datalad-rerun-actionability" >}})
for a detailed walkthrough of re-execution workflows.

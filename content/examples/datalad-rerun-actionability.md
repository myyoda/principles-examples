---
title: "Re-executing Computations with datalad rerun"
date: 2026-02-19
description: "Using datalad rerun to re-execute previously recorded computations for verification or updating"
summary: "Demonstrates how datalad rerun enables re-execution of previously recorded datalad run commands, turning provenance records into actionable recipes."
tags: ["datalad", "reproducibility", "re-execution"]
stamped_principles: ["A", "E"]
fair_principles: ["R"]
instrumentation_levels: ["tool"]
aspirations: ["reproducibility", "rigor"]
params:
  tools: ["datalad", "git"]
  difficulty: "intermediate"
  verified: false
state: uncurated-ai
---

## The problem: provenance as dead documentation

Many systems record provenance -- the chain of steps that produced a
result.  Workflow management tools generate DAGs, lab notebooks describe
procedures, README files list the commands that were run.  But in most
cases these records are **inert**: they describe what happened, but they
cannot *make it happen again*.

Consider a Git commit message that says:

```
Normalize and filter raw survey responses

Ran: python code/clean.py --threshold 0.05 inputs/raw/survey.csv outputs/clean/survey.csv
```

This is useful documentation, but it is just text.  To re-execute the
step, a human must read the message, extract the command, check that the
files are in place, and run it manually.  If the message has a typo, or
the file paths have changed, or the script has been updated, the re-execution
will silently produce different results -- or fail entirely.

The gap between "recorded provenance" and "executable provenance" is the
gap between documentation and actionability.

## The solution: `datalad rerun` turns records into actions

When a computation is recorded with `datalad run` (see the
[companion example]({{< ref "examples/datalad-run-provenance" >}})), the
resulting commit contains a machine-readable run record -- a JSON object
specifying the exact command, inputs, and outputs.  `datalad rerun` reads
this record and re-executes the command automatically:

```bash
datalad rerun <commit-hash>
```

That single command does all of the following:

1. **Parses** the run record from the specified commit.
2. **Gets** the declared input files (fetching from a remote annex if
   necessary).
3. **Unlocks** the declared output files so they can be overwritten.
4. **Executes** the recorded command string.
5. **Saves** the result as a new commit, linking back to the original
   run record.

No manual extraction of commands from commit messages.  No guessing about
file paths or flags.  The provenance record *is* the execution plan.

## Concrete example: verification workflow

Suppose your dataset has a commit from `datalad run` that generated
statistical results:

```bash
git log --oneline
# a1b2c3d (HEAD -> main) [DATALAD RUNCMD] Compute group statistics
# f6e5d4c Add preprocessed data
# 9a8b7c6 Initial commit
```

You want to verify that the results are reproducible.  First, inspect the
run record to understand what was recorded:

```bash
git log -1 --format=%B a1b2c3d
```

Output:

```
[DATALAD RUNCMD] Compute group statistics

=== Do not change lines below ===
{
 "cmd": "python code/analyze.py outputs/preprocessed/ outputs/statistics/results.json",
 "inputs": ["outputs/preprocessed/"],
 "outputs": ["outputs/statistics/results.json"],
 "exit": 0,
 "pwd": "."
}
^^^ Do not change lines above ^^^
```

Now re-execute:

```bash
datalad rerun a1b2c3d
```

DataLad fetches the inputs (if needed), runs the exact same command, and
commits the result.  If the output is identical to what was there before,
you have confirmed reproducibility.  If it differs, the `git diff` will
show you exactly what changed, pointing to non-determinism in the
computation or a change in the software environment.

### Checking for differences

After the rerun, compare the current output to the original:

```bash
# Did the rerun produce identical files?
git diff HEAD~1 -- outputs/statistics/results.json
```

If the diff is empty, the computation is reproducible.  If not, you have a
concrete starting point for investigation: the exact same command, on the
exact same inputs, produced different outputs.  That narrows the problem to
the software environment (library versions, random seeds, floating-point
ordering, etc.).

## Concrete example: updating workflow

A second powerful use of `datalad rerun` is propagating changes through a
pipeline.  Suppose the raw input data is corrected (a data entry error is
fixed).  You want to regenerate all downstream results:

```bash
git log --oneline
# b2c3d4e (HEAD -> main) [DATALAD RUNCMD] Generate figures
# a1b2c3d [DATALAD RUNCMD] Compute group statistics
# f6e5d4c [DATALAD RUNCMD] Preprocess raw data
# 9a8b7c6 Fix data entry error in raw/survey.csv
# 1234567 Add raw data
```

To re-execute the full pipeline from the preprocessing step onward:

```bash
datalad rerun --since 9a8b7c6
```

The `--since` flag tells DataLad to re-execute every `datalad run` commit
after the specified commit.  It will:

1. Rerun the preprocessing step (commit `f6e5d4c`).
2. Rerun the statistics computation (commit `a1b2c3d`).
3. Rerun the figure generation (commit `b2c3d4e`).

Each step uses the (now corrected) outputs of the previous step as its
inputs.  The entire pipeline is re-executed in order, and the results
reflect the corrected raw data.

## The difference between `datalad run` and `datalad rerun`

These two commands are complementary halves of the same workflow:

| Aspect | `datalad run` | `datalad rerun` |
|--------|---------------|-----------------|
| Purpose | Record a new computation | Re-execute a previously recorded computation |
| Input | A command typed by the user | A commit hash (or range) |
| Creates | A new commit with a run record | A new commit that re-executes an existing run record |
| When to use | First time you run a command | Verification, updating, or re-execution |

Think of `datalad run` as **recording** and `datalad rerun` as **playback**.
The recording captures the full specification; playback faithfully
reproduces it.

## Connection to Actionability (A)

The STAMPED **Actionability** principle states that dataset operations
should be executable, not just documented.  `datalad rerun` is the
mechanism that makes this principle concrete:

- A commit message that says "we ran script X" is **documentation**.
- A `datalad run` commit that contains a structured run record is
  **actionable documentation**.
- `datalad rerun` is the **action** -- it reads the documentation and
  executes it.

Without `datalad rerun`, run records would be valuable metadata but still
require manual interpretation.  With it, the entire provenance chain
becomes a push-button operation.

## Connection to Ephemerality (E)

The **Ephemerality** principle states that derived and regenerable content
should be treated as ephemeral.  `datalad rerun` is what makes this
practical:

- If every derived file was produced by a `datalad run` commit, then
  every derived file can be regenerated by `datalad rerun`.
- This means derived files do not need to be permanently stored -- they
  can be dropped from local storage (using `datalad drop`) and
  regenerated on demand.
- The repository stays lean: it stores the *recipes* (run records) rather
  than the *products* (large derived files).

The combination of `datalad run` (recording), `datalad rerun`
(re-execution), and `datalad drop` (reclaiming space) forms a complete
lifecycle for ephemeral data:

```
        run                    drop                   rerun
raw --> derived (committed) --> pointer only -------> derived (regenerated)
        [recipe recorded]      [space reclaimed]      [recipe re-executed]
```

## Practical considerations

### Software environment matters

`datalad rerun` re-executes the *command*, but it does not recreate the
*software environment*.  If you ran the original command with Python 3.10
and scikit-learn 1.2, but your current environment has Python 3.12 and
scikit-learn 1.4, the results may differ.

For full reproducibility, combine `datalad run` with environment capture:

- **Container images**: Use `datalad containers-run` to execute commands
  inside a Docker or Singularity container.  The container image is
  recorded in the run record alongside the command.
- **Lock files**: Track `requirements.txt` or `conda-lock.yml` in the
  repository so the exact package versions are part of the dataset's
  version history.

### Rerunning a single step vs. a range

```bash
# Re-execute a single recorded step
datalad rerun a1b2c3d

# Re-execute all recorded steps after a given commit
datalad rerun --since 9a8b7c6

# Re-execute all recorded steps in the entire history
datalad rerun --since ""
```

### Handling failures

If a rerun fails (non-zero exit code), DataLad will not commit the broken
output.  The working tree will contain the partial results, and you can
inspect what went wrong before deciding how to proceed.

### Combining with `--script`

You can extract the commands from a range of run records into a shell
script without executing them:

```bash
datalad rerun --since 9a8b7c6 --script pipeline.sh
```

This produces a standalone script containing the exact commands in order.
It is useful for review, for running on a cluster, or for porting to a
system where DataLad is not installed.

## Summary

`datalad rerun` closes the loop between provenance and action.  When
every data transformation is recorded with `datalad run`, the dataset's
history is not just a log of what happened -- it is a complete,
re-executable specification of how to produce the current state from
the original inputs.  This turns provenance from passive metadata into
an active tool for verification, updating, and space management.

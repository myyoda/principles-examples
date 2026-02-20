---
title: "Ephemeral Shell Scripts for Reproducing Issues"
date: 2026-02-19
description: "A pattern for writing minimal, self-contained shell scripts that reproduce software issues in temporary environments"
summary: "Distills a common practice among open-source developers: writing throwaway shell scripts that set up a fresh environment, reproduce a problem, and can be shared as actionable bug reports or starting points for test cases."
tags: ["shell", "posix", "reproducer", "bug-report", "testing"]
stamped_principles: ["S", "T", "A", "M", "P", "E", "D"]
fair_principles: ["R", "A"]
instrumentation_levels: ["pattern"]
aspirations: ["reproducibility", "rigor", "transparency"]
params:
  tools: ["sh", "awk", "datalad", "apptainer"]
  difficulty: "beginner"
  verified: false
state: wip
---

## The pattern

When a user encounters a bug or unexpected behavior in a command-line
tool, one of the most effective responses is to write a **minimal shell script**
that reproduces the problem from scratch.  The script creates a temporary
directory, sets up just enough state (repositories, files, configuration) to
trigger the issue, runs the offending commands, and exits.  The temporary
directory can then be inspected — or simply thrown away.

This pattern is ubiquitous in the git, git-annex, and DataLad communities.

## Anatomy of a reproducer script

### The skeleton

```sh
#!/bin/sh
# Reproducer for <tool> issue <#number>
# <one-line description of the problem>

set -eu

set -x
PS4='> '

cd "$(mktemp -d "${TMPDIR:-/tmp}/TOOL-XXXXXXX")"

# --- setup ---
# Create repos, files, configuration

# --- trigger ---
# Commands that demonstrate the issue

# --- inspect ---
# Show the unexpected state
```

### Key elements

**1. Shebang: `#!/bin/sh` (prefer POSIX)**

Use `#!/bin/sh` for maximum [portability]({{< ref "stamped_principles/p" >}}).
Only reach for `#!/bin/bash` when you genuinely need bash-specific features
(arrays, `[[ ]]`, process substitution).

**2. Strict error handling: `set -eu`**

- `-e` — exit immediately on any non-zero return.  If the setup steps fail,
  there is no point continuing to the "trigger" phase.
- `-u` — treat unset variables as errors.  Catches typos and missing
  configuration.

**3. Command tracing: `set -x` and `PS4='> '`**

`set -x` prints every command before it executes — invaluable when sharing
the script with someone who needs to see exactly what happened.  Always pair
it with an explicit `PS4` assignment:

```sh
set -x
PS4='> '
```

as `PS4` controls the prefix printed before each traced command (the default is
`+ `).  Setting it explicitly serves two purposes beyond readability:

- **[Reproducibility]({{< ref "aspirations/reproducibility" >}})** — the
  output is identical regardless of what the user's shell profile sets `PS4`
  to, making traces diffable across environments.
- **[Portability]({{< ref "stamped_principles/p" >}})** — some systems define
  `PS4` with shell-specific expansions (timestamps, function names) that can
  cause errors or garbled output when the script runs under a different shell.
  A simple literal value avoids this entirely.

Place `set -x` *after* `set -eu` so the trace starts once error handling is
active.  If a script invokes `bash -x script.sh` externally, having `PS4`
defined inside the script ensures consistent output regardless of how it was
launched.

**4. Ephemeral workspace: `mktemp -d`**

```sh
cd "$(mktemp -d "${TMPDIR:-/tmp}/dl-XXXXXXX")"
```

This is the core of [ephemerality]({{< ref "stamped_principles/e" >}}): every
run starts in a brand-new, empty directory.  Using `mktemp` rather than a
hardcoded path like `cd /tmp/mytest` is also a **security measure** — on
shared systems, a predictable path under `/tmp` is vulnerable to symlink
attacks where another user pre-creates a symlink pointing to a victim location.
`mktemp` generates an unpredictable name atomically.

The `${TMPDIR:-/tmp}` fallback respects system conventions across Linux and
macOS.  The prefix (`dl-`, `gx-`, `ann-`) identifies which tool the script
tests, making it easy to find (or clean up) leftover directories.

No `trap ... EXIT` cleanup is usually needed — `/tmp` is cleaned by the OS,
and you often *want* to inspect the result after a failure, and having `set -x`
visualizes initial `cd` path.

**5. Self-contained setup**

The script creates everything it needs from scratch: `git init`, `datalad
create`, `mkdir`, `echo content > file`.  It does not depend on pre-existing
repositories, databases, or files on the user's machine.  This makes the script
[self-contained]({{< ref "stamped_principles/s" >}}) — anyone with the
required tool installed can run it.

When a test *must* reference an external resource (a specific repository, a URL
serving a known file), prefer stable, version-pinned URLs:

```sh
# Pin to a specific commit — content will not change
url=https://raw.githubusercontent.com/datalad/datalad/0cb711ff/.../README.md
```

**6. Subshell isolation with `( ... )`**

```sh
(
  cd src
  git init
  git annex init
  echo 123 > file
  git annex add file && git commit -m "add file"
)
```

Parenthesized subshells keep `cd` side effects contained.  The main script
stays in the top-level temp directory, making it easy to work with multiple
repositories (a common need when reproducing push/pull/clone issues).

**7. Inline expected-failure guards**

```sh
if datalad push --to=target -r; then
    echo "Expected to fail, but succeeded"
    exit 1
fi
```

When the script *demonstrates* a failure, guarding the failing command
prevents `set -e` from aborting prematurely, while still clearly stating the
expectation.

## STAMPED analysis

| Property | How the pattern embodies it |
|---|---|
| [Self-contained]({{< ref "stamped_principles/s" >}}) | Everything needed is created inline — no external state required beyond the tool under test |
| [Tracked]({{< ref "stamped_principles/t" >}}) | The script *is* the record: copy-pasteable into an issue, attachable to a commit |
| [Actionable]({{< ref "stamped_principles/a" >}}) | Running the script *is* the reproduction — it is an executable specification of the bug, not a prose description |
| [Portable]({{< ref "stamped_principles/p" >}}) | POSIX sh + `mktemp` + `${TMPDIR:-/tmp}` works across Linux and macOS; explicit `PS4` avoids shell-specific trace behavior; no hardcoded paths |
| [Ephemeral]({{< ref "stamped_principles/e" >}}) | Each run operates in a fresh temp directory; the entire workspace can be discarded after inspection |

## From reproducer to test case

A reproducer script is often the **first draft of a regression test**.  The
progression is natural:

1. **Bug report** — paste the script into a GitHub issue.  Anyone can run it.
2. **Bisection driver** — wrap the script's exit code in `git bisect run` to
   find the introducing commit.
3. **Red/green test** — translate the shell commands into the project's test
   framework (e.g., pytest).  The setup phase becomes a fixture, the trigger
   becomes the test body, and the inspection becomes an assertion.

This progression from throwaway script to permanent test case mirrors the
Red/Green cycle of [TDD](https://en.wikipedia.org/wiki/Test-driven_development):
the reproducer is the "red" test that fails, the fix
makes it "green", and the test prevents regressions.

## Example scenarios

The scenarios below build progressively — each one adds STAMPED properties on
top of the previous, using the same scientific task: quality-control of
temperature sensor readings.

### Scenario 1: Self-contained data processing (S, E)

The simplest case: a single script that generates synthetic measurements,
computes per-sensor statistics, and checks them against a QC threshold.  It
requires only POSIX `sh` and `awk` — nothing else to install.

```sh
#!/bin/sh
# Sensor QC: compute per-sensor mean temperature, flag outliers
# Requires: sh, awk

set -eu

set -x
PS4='> '

cd "$(mktemp -d "${TMPDIR:-/tmp}/qc-XXXXXXX")"

# --- generate synthetic raw data ---
TAB="$(printf '\t')"
cat > measurements.tsv <<EOF
sensor_id${TAB}timestamp${TAB}temperature_C
TMP001${TAB}2026-01-15T08:00${TAB}21.3
TMP001${TAB}2026-01-15T12:00${TAB}23.7
TMP001${TAB}2026-01-15T16:00${TAB}22.1
TMP002${TAB}2026-01-15T08:00${TAB}19.8
TMP002${TAB}2026-01-15T12:00${TAB}25.4
TMP002${TAB}2026-01-15T16:00${TAB}24.2
TMP003${TAB}2026-01-15T08:00${TAB}20.5
TMP003${TAB}2026-01-15T12:00${TAB}22.8
TMP003${TAB}2026-01-15T16:00${TAB}21.1
EOF

THRESHOLD=23.0

# --- process: per-sensor mean ---
LC_ALL=C
export LC_ALL

awk -F'\t' 'NR>1 {sum[$1]+=$3; n[$1]++}
  END {for(s in sum) printf "%s\t%.2f\t%d\n", s, sum[s]/n[s], n[s]}' \
  measurements.tsv | sort -t"$TAB" -k1,1 > summary.tsv

# --- QC check ---
awk -F'\t' -v thresh="$THRESHOLD" '{
  status = ($2 > thresh) ? "WARNING" : "OK"
  printf "%s\t%s\tmean=%.2f\tn=%d\n", $1, status, $2, $3
}' summary.tsv > report.tsv

echo "=== QC Report ==="
cat report.tsv
```

This script is [self-contained]({{< ref "stamped_principles/s" >}}) (the data
is generated inline) and [ephemeral]({{< ref "stamped_principles/e" >}}) (runs
in a fresh temp directory).  Note the two portability safeguards:

- **`LC_ALL=C`** — forces consistent numeric formatting and sort collation
  regardless of the host locale.  Without it, a system with `LC_ALL=de_DE.UTF-8`
  might sort differently or misparse decimal points.
- **`TAB="$(printf '\t')"`** — POSIX-portable tab literal.  The tempting
  `$'\t'` syntax is a bash extension that silently breaks under `dash` (the
  default `/bin/sh` on Debian/Ubuntu).

Also note the explicit `| sort` after the `awk` aggregation.  The POSIX spec
states that `for (key in array)` iteration order in `awk` is
**implementation-defined** — `gawk`, `mawk`, and `busybox awk` produce
different orderings.  Piping through `sort` makes the output deterministic
regardless of which `awk` is installed.

#### What happens without these safeguards

A "naive" version that omits `LC_ALL`, uses `$'\t'`, and skips the `sort`
might work perfectly on the author's machine.  On a colleague's system it can
fail in two distinct ways:

1. **Silent divergence** — `awk` emits rows in a different order.  Both
   outputs contain the same numbers, but `diff` or `sha256sum` shows they
   differ.  Hours of debugging follow.
2. **Hard crash** — `dash` does not recognize `$'\t'`, so `sort -t$'\t'`
   receives a literal string and fails or sorts incorrectly.

Both failures are invisible during development on the author's machine and only
surface when someone else tries to reproduce.

### Scenario 2: Tracked provenance with `datalad run` (+ T, A)

The same analysis, but now the computation is recorded as a tracked,
re-executable step.  This adds
[tracking]({{< ref "stamped_principles/t" >}}) and
[actionability]({{< ref "stamped_principles/a" >}}) — anyone who clones the
dataset can inspect exactly what was run and `datalad rerun` it.

```sh
#!/bin/sh
# Sensor QC with tracked provenance via datalad run
# Requires: sh, awk, datalad

set -eu

set -x
PS4='> '

cd "$(mktemp -d "${TMPDIR:-/tmp}/qc-XXXXXXX")"

# --- setup: create a dataset and add raw data ---
datalad create -c text2git qc-analysis
cd qc-analysis

TAB="$(printf '\t')"
cat > measurements.tsv <<EOF
sensor_id${TAB}timestamp${TAB}temperature_C
TMP001${TAB}2026-01-15T08:00${TAB}21.3
TMP001${TAB}2026-01-15T12:00${TAB}23.7
TMP001${TAB}2026-01-15T16:00${TAB}22.1
TMP002${TAB}2026-01-15T08:00${TAB}19.8
TMP002${TAB}2026-01-15T12:00${TAB}25.4
TMP002${TAB}2026-01-15T16:00${TAB}24.2
TMP003${TAB}2026-01-15T08:00${TAB}20.5
TMP003${TAB}2026-01-15T12:00${TAB}22.8
TMP003${TAB}2026-01-15T16:00${TAB}21.1
EOF
datalad save -m "Add raw sensor measurements"

# --- write the analysis script ---
cat > run-qc.sh <<'SCRIPT'
#!/bin/sh
set -eu
LC_ALL=C; export LC_ALL
TAB="$(printf '\t')"
THRESHOLD=23.0
awk -F'\t' 'NR>1 {sum[$1]+=$3; n[$1]++}
  END {for(s in sum) printf "%s\t%.2f\t%d\n", s, sum[s]/n[s], n[s]}' \
  measurements.tsv | sort -t"$TAB" -k1,1 > summary.tsv
awk -F'\t' -v thresh="$THRESHOLD" '{
  status = ($2 > thresh) ? "WARNING" : "OK"
  printf "%s\t%s\tmean=%.2f\tn=%d\n", $1, status, $2, $3
}' summary.tsv > report.tsv
SCRIPT
chmod +x run-qc.sh
datalad save -m "Add QC analysis script"

# --- run with provenance tracking ---
datalad run \
  -m "Run sensor QC analysis" \
  --input measurements.tsv \
  --output summary.tsv \
  --output report.tsv \
  ./run-qc.sh

# --- inspect: the result is tracked ---
echo "=== QC Report ==="
cat report.tsv
echo ""
echo "=== Provenance (last commit) ==="
git log -1 --format="%B"
```

Now `report.tsv` is not just a file — it is a tracked artifact whose exact
provenance (input file, command, output) is recorded in the git history.
Running `datalad rerun` on the last commit will re-execute `run-qc.sh` and
verify that the output has not changed.

### Scenario 3: Containerized execution with cowsay (+ P)

To pin the computational environment and guarantee identical output on any
machine, we can run the analysis inside a container.  This scenario uses the
classic [`lolcow`](https://hub.docker.com/r/godlovedc/lolcow) container
available from Docker Hub (usable via
[Apptainer/Singularity](https://apptainer.org/)) to present the QC results
in style:

```sh
#!/bin/sh
# Sensor QC with containerized report via lolcow/cowsay
# Requires: sh, awk, apptainer (or singularity)

set -eu

set -x
PS4='> '

cd "$(mktemp -d "${TMPDIR:-/tmp}/qc-XXXXXXX")"

# Detect container runtime
if command -v apptainer >/dev/null 2>&1; then
  RUNNER=apptainer
elif command -v singularity >/dev/null 2>&1; then
  RUNNER=singularity
else
  echo "ERROR: apptainer or singularity required" >&2
  exit 1
fi

# --- pull the container image ---
$RUNNER pull docker://godlovedc/lolcow

# --- generate data and run QC (same as Scenario 1) ---
TAB="$(printf '\t')"
cat > measurements.tsv <<EOF
sensor_id${TAB}timestamp${TAB}temperature_C
TMP001${TAB}2026-01-15T08:00${TAB}21.3
TMP001${TAB}2026-01-15T12:00${TAB}23.7
TMP001${TAB}2026-01-15T16:00${TAB}22.1
TMP002${TAB}2026-01-15T08:00${TAB}19.8
TMP002${TAB}2026-01-15T12:00${TAB}25.4
TMP002${TAB}2026-01-15T16:00${TAB}24.2
TMP003${TAB}2026-01-15T08:00${TAB}20.5
TMP003${TAB}2026-01-15T12:00${TAB}22.8
TMP003${TAB}2026-01-15T16:00${TAB}21.1
EOF

LC_ALL=C; export LC_ALL
awk -F'\t' 'NR>1 {sum[$1]+=$3; n[$1]++}
  END {for(s in sum) printf "%s\t%.2f\t%d\n", s, sum[s]/n[s], n[s]}' \
  measurements.tsv | sort -t"$TAB" -k1,1 > summary.tsv

awk -F'\t' -v thresh=23.0 '{
  status = ($2 > thresh) ? "WARNING" : "OK"
  printf "%s %s (mean=%.2f, n=%d)\n", $1, status, $2, $3
}' summary.tsv > report.txt

# --- present the report inside the container ---
$RUNNER exec --cleanenv lolcow_latest.sif cowsay -f tux \
  "$(cat report.txt)"
```

The container image reference is specified but **not pinned** — `docker://godlovedc/lolcow`
resolves to the `latest` tag, which could change at any time.  The script
gains [portability]({{< ref "stamped_principles/p" >}}) (no longer depends on
whatever happens to be installed on the host), but it **loses properties** it
previously had:

- **S is weakened** — the script depends on Docker Hub being available and
  serving this specific image.  If the hub goes down or the image is removed,
  the script breaks.
- **T is weak** — we know we used "lolcow", but not *which exact version*.
  The `latest` tag is mutable; tomorrow's `latest` could contain different
  binaries.

This is a real trade-off: adding a container improved portability but
introduced an external, mutable dependency.

### Scenario 3b: Pinning the container by digest (recovering T)

A simple fix for the tracking problem: reference the image by its
content-addressed **digest** rather than a mutable tag.

The only line that changes from Scenario 3:

```sh
# Before (mutable tag — could change):
$RUNNER pull docker://godlovedc/lolcow

# After (pinned digest — immutable):
$RUNNER pull docker://godlovedc/lolcow@sha256:a692b57abc43035b197b10390ea2c12855d21649f2ea2cc28094d18b93360eeb
```

With a digest, two people running the script a year apart will pull
**byte-identical** image content — the registry is physically unable to serve
different bits for the same `sha256`.  This recovers
[tracking]({{< ref "stamped_principles/t" >}}): the provenance now records
exactly which environment was used, down to every library version.

But [self-containment]({{< ref "stamped_principles/s" >}}) is **still
missing**.  The image lives on Docker Hub, not inside our project.  If
`godlovedc` deletes the repository, or Docker Hub imposes pull rate limits, or
the network is simply unavailable (an air-gapped HPC cluster), the script
cannot obtain its dependency.  The digest is a precise *reference*, not a
local *copy*.

This is the gap that Scenario 4 closes.

### Scenario 4: Modular composition with sub-datasets (+ M, D, recovering S)

In a real project, raw data and container images typically live in separate
repositories that are composed together.  This final scenario uses DataLad
sub-datasets for [modularity]({{< ref "stamped_principles/m" >}}) and
[distributability]({{< ref "stamped_principles/d" >}}).  Critically, `datalad
containers-add` **downloads the image and stores it in git-annex** — the
container is now *inside* the dataset, content-addressed and distributable
alongside the data.  This recovers [self-containment]({{< ref
"stamped_principles/s" >}}) that was lost in Scenarios 3 and 3b:

```sh
#!/bin/sh
# Sensor QC with modular sub-datasets for data and containers
# Requires: sh, awk, datalad, datalad-container, apptainer/singularity

set -eu

set -x
PS4='> '

cd "$(mktemp -d "${TMPDIR:-/tmp}/qc-XXXXXXX")"

# --- setup: create the analysis superdataset ---
datalad create -c text2git qc-project
cd qc-project

# --- modular raw data as a sub-dataset ---
datalad create -d . -c text2git raw-data
TAB="$(printf '\t')"
cat > raw-data/measurements.tsv <<EOF
sensor_id${TAB}timestamp${TAB}temperature_C
TMP001${TAB}2026-01-15T08:00${TAB}21.3
TMP001${TAB}2026-01-15T12:00${TAB}23.7
TMP001${TAB}2026-01-15T16:00${TAB}22.1
TMP002${TAB}2026-01-15T08:00${TAB}19.8
TMP002${TAB}2026-01-15T12:00${TAB}25.4
TMP002${TAB}2026-01-15T16:00${TAB}24.2
TMP003${TAB}2026-01-15T08:00${TAB}20.5
TMP003${TAB}2026-01-15T12:00${TAB}22.8
TMP003${TAB}2026-01-15T16:00${TAB}21.1
EOF
datalad save -d raw-data -m "Add raw sensor measurements"
datalad save -m "Register raw-data sub-dataset"

# --- add a container for the report presentation ---
datalad containers-add lolcow \
  --url docker://godlovedc/lolcow \
  --call-fmt '{img} exec {img_dspath} {cmd}'

# --- write the analysis script ---
cat > run-qc.sh <<'SCRIPT'
#!/bin/sh
set -eu
LC_ALL=C; export LC_ALL
TAB="$(printf '\t')"
awk -F'\t' 'NR>1 {sum[$1]+=$3; n[$1]++}
  END {for(s in sum) printf "%s\t%.2f\t%d\n", s, sum[s]/n[s], n[s]}' \
  raw-data/measurements.tsv | sort -t"$TAB" -k1,1 > summary.tsv
awk -F'\t' -v thresh=23.0 '{
  status = ($2 > thresh) ? "WARNING" : "OK"
  printf "%s %s (mean=%.2f, n=%d)\n", $1, status, $2, $3
}' summary.tsv > report.txt
SCRIPT
chmod +x run-qc.sh
datalad save -m "Add QC analysis script"

# --- run with full provenance ---
datalad containers-run \
  -n lolcow \
  -m "Run sensor QC and present report" \
  --input raw-data/measurements.tsv \
  --output summary.tsv \
  --output report.txt \
  ./run-qc.sh

echo "=== QC Report ==="
cat report.txt
echo ""
echo "=== Dataset structure ==="
datalad subdatasets
```

This recovers the full STAMPED stack — including the properties that were lost
when we introduced an external container dependency in Scenarios 3/3b:

| Property | How it is realized |
|---|---|
| **S** — Self-contained | Raw data, analysis script, and container image all live *within* the dataset (git-annex stores the `.sif`). No external service needed to reproduce. |
| **T** — Tracked | `datalad containers-run` records input files, output files, container identity, and the exact command in a single commit |
| **A** — Actionable | `datalad rerun` re-executes the analysis; the provenance is not just metadata but a re-executable specification |
| **M** — Modular | Raw data is a separate sub-dataset, reusable across projects without duplication |
| **P** — Portable | The container pins the compute environment; POSIX shell + `LC_ALL=C` pins the script |
| **E** — Ephemeral | The entire analysis runs in a temp directory built from scratch |
| **D** — Distributable | Sub-datasets can be published independently; collaborators `datalad clone` + `datalad get` to obtain data and container on demand. Distribution can happen through multiple channels simultaneously (see below). |

**Distribution is not limited to a single channel.**  The same dataset can be
published to GitHub (git history + annex pointers), while the large files
(raw data, container image) are exported to an archival repository such as
Figshare via `datalad export-to-figshare` or pushed to any other
git-annex special remote (S3, rsync, OSF, etc.).  Crucially, git-annex records
each remote as an **availability source** within the dataset itself — a
`datalad get` will transparently try all known locations.  This means:

- If GitHub is reachable but Figshare is down, data is still obtainable (and
  vice versa).
- The Figshare deposit gets a **DOI**, making the dataset citable and
  discoverable independently of the git hosting.
- The availability information (which remotes hold which files) travels with
  the dataset — a fresh `datalad clone` inherits all known sources without
  additional configuration.

This multi-channel distribution with retained availability linkage is what
elevates D beyond "I can copy this somewhere": the research object *knows*
where its parts are available and can assemble itself from whichever sources
are reachable.

The progression across all four scenarios illustrates a general pattern: each
STAMPED property you add removes a class of failure, but introducing an
external dependency (the container) can *remove* properties you already had
(self-containment) unless you provision for it explicitly.

## Practical guidelines

1. **Name scripts after issue numbers**: `bug-3686.sh`, `gh-6296.sh`,
   `annex-4369.sh`.  When you return months later, the filename links directly
   to the discussion.

2. **Use a descriptive prefix in `mktemp`**: `dl-` for DataLad, `gx-` for
   git-annex, `ann-` for general annex tests.  This makes orphaned temp
   directories identifiable.

3. **Always set `PS4`**: Even if you omit `set -x` from the script itself,
   setting `PS4='> '` ensures consistent trace output when someone runs
   `bash -x script.sh` externally.

4. **Print version information early**: `git annex version | head -n 1` or
   `datalad --version` at the top helps recipients match your environment.

5. **Do not clean up on success**: Leave the temp directory intact so you (or
   the recipient) can inspect the state.  `/tmp` is cleaned on reboot.

6. **Keep scripts minimal**: Every line that is not strictly necessary to
   trigger the bug is noise.  Minimal scripts are easier to review, faster to
   bisect, and more likely to be turned into test cases.

7. **Test your own instructions**: After sharing a reproducer (e.g., in a
   GitHub issue), copy-paste the invocation instructions you gave the recipient
   and run them yourself on a different machine or in a fresh shell.  This
   catches implicit assumptions — a forgotten dependency, a path that only
   exists on your system, or a missing `chmod +x` — before someone else hits
   them.

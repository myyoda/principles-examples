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
  tools: ["sh", "awk", "make", "git", "singularity"]
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

The script creates everything it needs from scratch: `git init`, `mkdir`,
`echo content > file`.  It does not depend on pre-existing
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
  echo 123 > file
  git add file && git commit -m "add file"
)
```

Parenthesized subshells keep `cd` side effects contained.  The main script
stays in the top-level temp directory, making it easy to work with multiple
repositories (a common need when reproducing push/pull/clone issues).

**7. Inline expected-failure guards**

```sh
if git push origin main; then
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
# pragma: testrun scenario-1
# pragma: requires sh awk
# Sensor QC: compute per-sensor mean temperature, flag outliers

set -eu

set -x
PS4='> '

cd "$(mktemp -d "${TMPDIR:-/tmp}/qc-XXXXXXX")"

# --- generate synthetic raw data ---
cat > measurements.csv <<'EOF'
sensor_id,timestamp,temperature_C
TMP001,2026-01-15T08:00,21.3
TMP001,2026-01-15T12:00,23.7
TMP002,2026-01-15T08:00,25.4
EOF

THRESHOLD=23.0

# --- process: per-sensor mean ---
LC_ALL=C
export LC_ALL

awk -F, 'NR>1 {sum[$1]+=$3; n[$1]++}
  END {for(s in sum) printf "%s,%.2f,%d\n", s, sum[s]/n[s], n[s]}' \
  measurements.csv | sort -t, -k1,1 > summary.csv

# --- QC check ---
awk -F, -v thresh="$THRESHOLD" '{
  status = ($2 > thresh) ? "WARNING" : "OK"
  printf "%s,%s,mean=%.2f,n=%d\n", $1, status, $2, $3
}' summary.csv > report.csv

echo "=== QC Report ==="
cat report.csv
```

This script is [self-contained]({{< ref "stamped_principles/s" >}}) (the data
is generated inline) and [ephemeral]({{< ref "stamped_principles/e" >}}) (runs
in a fresh temp directory).  Note two portability safeguards:

- **`LC_ALL=C`** — forces consistent numeric formatting and sort collation
  regardless of the host locale.  Without it, a system with `LC_ALL=de_DE.UTF-8`
  might sort differently or misparse decimal points.
- **Explicit `| sort` after `awk` aggregation** — the POSIX spec states that
  `for (key in array)` iteration order in `awk` is **implementation-defined**.
  `gawk`, `mawk`, and `busybox awk` produce different orderings for the same
  input.  Piping through `sort` makes the output deterministic regardless of
  which `awk` is installed.

Using CSV (comma-separated) rather than TSV also simplifies the script — no
need to deal with tab literals, which require care in POSIX shell (the
`$'\t'` syntax is a bash extension that silently breaks under `dash`).

#### What happens without these safeguards

A "naive" version that omits `LC_ALL=C` and skips the `sort` might work
perfectly on the author's machine.  On a colleague's system it can fail in
two distinct ways:

1. **Silent divergence** — `awk` emits rows in a different order.  Both
   outputs contain the same numbers, but `diff` or `sha256sum` shows they
   differ.  Hours of debugging follow.
2. **Locale mismatch** — a German locale parses `23.7` differently, or
   `sort` collates strings in an unexpected order, producing subtly wrong
   results.

Both failures are invisible during development on the author's machine and only
surface when someone else tries to reproduce.

### Scenario 2: Makefile as actionable specification (+ T, A)

The same analysis, but now organized as a git repository with a `Makefile`
that declares the dependency graph.  This adds
[tracking]({{< ref "stamped_principles/t" >}}) (git records every change)
and [actionability]({{< ref "stamped_principles/a" >}}) (`make` re-derives
results from source).  No specialized tooling beyond `git` and `make`.

```sh
#!/bin/sh
# pragma: testrun scenario-2
# pragma: requires sh awk make git
# Sensor QC as a tracked, actionable git repository

set -eu

set -x
PS4='> '

cd "$(mktemp -d "${TMPDIR:-/tmp}/qc-XXXXXXX")"

git init qc-analysis
cd qc-analysis

# --- raw data ---
cat > measurements.csv <<'EOF'
sensor_id,timestamp,temperature_C
TMP001,2026-01-15T08:00,21.3
TMP001,2026-01-15T12:00,23.7
TMP002,2026-01-15T08:00,25.4
EOF

# --- analysis script ---
cat > run-qc.sh <<'SCRIPT'
#!/bin/sh
set -eu
LC_ALL=C; export LC_ALL
THRESHOLD=23.0
awk -F, 'NR>1 {sum[$1]+=$3; n[$1]++}
  END {for(s in sum) printf "%s,%.2f,%d\n", s, sum[s]/n[s], n[s]}' \
  measurements.csv | sort -t, -k1,1 > summary.csv
awk -F, -v thresh="$THRESHOLD" '{
  status = ($2 > thresh) ? "WARNING" : "OK"
  printf "%s,%s,mean=%.2f,n=%d\n", $1, status, $2, $3
}' summary.csv > report.csv
SCRIPT
chmod +x run-qc.sh

# --- Makefile: the actionable specification ---
cat > Makefile <<'MF'
.POSIX:

all: report.csv

report.csv summary.csv: measurements.csv run-qc.sh
	./run-qc.sh

clean:
	rm -f summary.csv report.csv

.PHONY: all clean
MF

# --- README: tell collaborators what to do ---
cat > README.md <<'README'
# Sensor QC Analysis

Run `make` to produce `report.csv` from `measurements.csv`.

Requires: POSIX sh, awk, make.
README

# --- .gitignore: outputs are derived, not tracked ---
cat > .gitignore <<'GI'
summary.csv
report.csv
GI

git add -A
git commit -m "Initial commit: sensor QC analysis"

# --- run it ---
make
echo "=== QC Report ==="
cat report.csv
echo ""
echo "=== Provenance: the Makefile + git log ==="
git log --oneline
```

The `Makefile` is the actionable specification: it declares that `report.csv`
depends on `measurements.csv` and `run-qc.sh`, and `make` will only re-run
the analysis when an input changes.  The `README.md` tells a collaborator
everything they need: run `make`.  Git tracks the full history.

This is a substantial improvement over a loose script: `git clone` + `make`
is all anyone needs to reproduce the result.  But `make` records *what*
to run, not *what environment* to run it in — the host's `awk` version is
still implicit.

### Scenario 3: Containerized execution with Alpine (+ P)

To pin the computational environment, we run the analysis inside a minimal
[Alpine Linux](https://hub.docker.com/_/alpine) container (~3 MB as a `.sif`
image).  Alpine includes BusyBox `awk` — exactly what our script needs,
nothing more.

The examples below use [Singularity](https://sylabs.io/singularity/) to pull
and execute the container.  The same approach works with
[Apptainer](https://apptainer.org/) (the open-source fork — just replace
`singularity` with `apptainer`), or with Docker/Podman if you prefer an
OCI-native workflow (`docker run --rm -v "$PWD:$PWD" -w "$PWD" alpine:3.21
./run-qc.sh`).

```sh
#!/bin/sh
# pragma: testrun scenario-3
# pragma: requires sh awk make git singularity
# pragma: timeout 120
# Sensor QC with containerized execution via Alpine

set -eu

set -x
PS4='> '

cd "$(mktemp -d "${TMPDIR:-/tmp}/qc-XXXXXXX")"

# --- pull a minimal container image ---
singularity pull docker://alpine:3.21

git init qc-analysis
cd qc-analysis

# --- same data and script as Scenario 2 ---
cat > measurements.csv <<'EOF'
sensor_id,timestamp,temperature_C
TMP001,2026-01-15T08:00,21.3
TMP001,2026-01-15T12:00,23.7
TMP002,2026-01-15T08:00,25.4
EOF

cat > run-qc.sh <<'SCRIPT'
#!/bin/sh
set -eu
LC_ALL=C; export LC_ALL
THRESHOLD=23.0
awk -F, 'NR>1 {sum[$1]+=$3; n[$1]++}
  END {for(s in sum) printf "%s,%.2f,%d\n", s, sum[s]/n[s], n[s]}' \
  measurements.csv | sort -t, -k1,1 > summary.csv
awk -F, -v thresh="$THRESHOLD" '{
  status = ($2 > thresh) ? "WARNING" : "OK"
  printf "%s,%s,mean=%.2f,n=%d\n", $1, status, $2, $3
}' summary.csv > report.csv
SCRIPT
chmod +x run-qc.sh

# --- Makefile: run inside the container ---
cat > Makefile <<'MF'
.POSIX:
SIF = ../alpine_3.21.sif

all: report.csv

report.csv summary.csv: measurements.csv run-qc.sh $(SIF)
	singularity exec --cleanenv $(SIF) ./run-qc.sh

clean:
	rm -f summary.csv report.csv

.PHONY: all clean
MF

cat > .gitignore <<'GI'
summary.csv
report.csv
GI

cat > README.md <<'README'
# Sensor QC Analysis (containerized)

Run `make` to produce `report.csv` from `measurements.csv`.

The analysis runs inside an Alpine Linux container to guarantee
identical results regardless of the host system's awk version.

Requires: POSIX sh, make, singularity (or apptainer).
The container image (`alpine_3.21.sif`) must be present in the
parent directory — see Makefile for details.
README

git add -A
git commit -m "Initial commit: containerized sensor QC"

# --- run it ---
make
echo "=== QC Report ==="
cat report.csv
```

Now every collaborator gets the same BusyBox `awk` regardless of whether their
host has `gawk`, `mawk`, or something else.  This demonstrates
[portability]({{< ref "stamped_principles/p" >}}): the script no longer
depends on whatever happens to be installed on the host.

But the container reference `docker://alpine:3.21` is **not pinned** —
the `3.21` tag is mutable (Alpine publishes point releases under the same
tag).  And the script **depends on Docker Hub being available**: if the
network is down or the registry is unavailable, the `pull` fails.

- **S is weakened** — the container lives on Docker Hub, not in our repository.
- **T is weak** — we know "Alpine 3.21" but not which exact build.

### Scenario 3b: Pinning the container by digest (recovering T)

A simple fix for the tracking problem: reference the image by its
content-addressed **digest** rather than a mutable tag.

The only line that changes from Scenario 3:

```sh
# Before (mutable tag — could change between builds):
singularity pull docker://alpine:3.21

# After (pinned digest — immutable):
singularity pull docker://alpine@sha256:a8560b36e8b8210634f77d9f7f9efd7ffa463e380b75e2e74aff4511df3ef88c
```

With a digest, two people running the script a year apart will pull
**byte-identical** image content — the registry is physically unable to serve
different bits for the same `sha256`.  This recovers
[tracking]({{< ref "stamped_principles/t" >}}): the provenance now records
exactly which environment was used, down to every library version.

But [self-containment]({{< ref "stamped_principles/s" >}}) is **still
missing**.  The image lives on Docker Hub, not inside our project.  If the
registry imposes pull rate limits, or the network is simply unavailable (an
air-gapped HPC cluster), the script cannot obtain its dependency.  The digest
is a precise *reference*, not a local *copy*.

This is the gap that Scenario 4 closes.

### Scenario 4: Container committed to git (recovering S, + M, D)

The Alpine `.sif` image is only ~3 MB — small enough to commit directly
to the git repository.  Now the container travels *with* the code and data.
No network access needed to reproduce.

```sh
#!/bin/sh
# pragma: testrun scenario-4
# pragma: requires sh make git singularity
# pragma: timeout 120
# Sensor QC: fully self-contained with container in git

set -eu

set -x
PS4='> '

cd "$(mktemp -d "${TMPDIR:-/tmp}/qc-XXXXXXX")"

# --- build the container image from a pinned digest ---
singularity pull docker://alpine@sha256:a8560b36e8b8210634f77d9f7f9efd7ffa463e380b75e2e74aff4511df3ef88c
mv alpine_latest.sif env.sif

git init qc-analysis
cd qc-analysis

# --- commit the container image into the repository ---
cp ../env.sif .
git add env.sif
git commit -m "Add Alpine container image (3 MB, pinned by digest)"

# --- raw data as a git submodule (modularity) ---
(
  cd ..
  git init --bare raw-data.git
  git clone raw-data.git raw-data-work
  cd raw-data-work
  cat > measurements.csv <<'EOF'
sensor_id,timestamp,temperature_C
TMP001,2026-01-15T08:00,21.3
TMP001,2026-01-15T12:00,23.7
TMP002,2026-01-15T08:00,25.4
EOF
  git add measurements.csv
  git commit -m "Add raw sensor measurements"
  git push
)
git submodule add ../raw-data.git raw-data

# --- analysis script ---
cat > run-qc.sh <<'SCRIPT'
#!/bin/sh
set -eu
LC_ALL=C; export LC_ALL
THRESHOLD=23.0
awk -F, 'NR>1 {sum[$1]+=$3; n[$1]++}
  END {for(s in sum) printf "%s,%.2f,%d\n", s, sum[s]/n[s], n[s]}' \
  raw-data/measurements.csv | sort -t, -k1,1 > summary.csv
awk -F, -v thresh="$THRESHOLD" '{
  status = ($2 > thresh) ? "WARNING" : "OK"
  printf "%s,%s,mean=%.2f,n=%d\n", $1, status, $2, $3
}' summary.csv > report.csv
SCRIPT
chmod +x run-qc.sh

# --- Makefile: run inside the local container ---
cat > Makefile <<'MF'
.POSIX:
SIF = env.sif

all: report.csv

report.csv summary.csv: raw-data/measurements.csv run-qc.sh $(SIF)
	singularity exec --cleanenv $(SIF) ./run-qc.sh

clean:
	rm -f summary.csv report.csv

.PHONY: all clean
MF

cat > .gitignore <<'GI'
summary.csv
report.csv
GI

cat > README.md <<'README'
# Sensor QC Analysis

Run `make` to produce `report.csv` from raw sensor measurements.

The analysis runs inside an Alpine Linux container (`env.sif`)
that is committed to this repository — no network access needed.
Raw data lives in the `raw-data/` git submodule.

    git clone --recurse-submodules <url>
    make

Requires: POSIX sh, make, singularity (or apptainer).
README

git add -A
git commit -m "Add analysis script, Makefile, and README"

# --- run it ---
make
echo "=== QC Report ==="
cat report.csv
echo ""
echo "=== Repository structure ==="
git submodule status
git log --oneline
```

This recovers the full STAMPED stack using only `git`, `make`, and
`singularity` — no specialized research data management tools required:

| Property | How it is realized |
|---|---|
| **S** — Self-contained | Container image (`env.sif`), analysis script, and Makefile are all committed to git. Raw data is pinned via a git submodule at a specific commit. `git clone --recurse-submodules` + `make` is all anyone needs. |
| **T** — Tracked | Git records every change to code, data (in the submodule), and even the container image. The Makefile declares the exact dependency graph. |
| **A** — Actionable | `make` re-derives results from source. The `README.md` tells a collaborator exactly what to run. |
| **M** — Modular | Raw data is a separate git repository included as a submodule — reusable in other projects, versioned independently. |
| **P** — Portable | The container pins the `awk` implementation; POSIX shell + `LC_ALL=C` pins the script behavior. |
| **E** — Ephemeral | The entire analysis runs in a temp directory built from scratch. |
| **D** — Distributable | Standard `git push` to any remote. The repository can be pushed to multiple hosts (GitHub, GitLab, institutional server) simultaneously. For archival, `git bundle` creates a single-file snapshot of the entire history. |

For projects where the data or container images outgrow what is practical to
commit to git directly, tools like [git-annex](https://git-annex.branchable.com/)
or [DataLad](https://www.datalad.org/) extend this pattern with
content-addressed storage and multi-remote availability tracking — the same
dataset can be distributed to GitHub, Figshare (with a DOI), S3, or
institutional archives, and the availability information (which remotes hold
which files) travels with the dataset so that a fresh clone can assemble itself
from whichever sources are reachable.

In particular,
[datalad-container](https://github.com/datalad/datalad-container) simplifies
container management within DataLad datasets: it maintains a local catalog of
container images (tracked by git-annex), and its `datalad containers-run`
command records which container was used for each computation — adding
container identity to the provenance chain automatically.

For neuroimaging and other scientific domains,
[ReproNim/containers](https://github.com/ReproNim/containers) provides a
ready-made DataLad dataset of popular containerized tools (FreeSurfer,
fMRIPrep, BIDS Apps, etc.).  It is itself a STAMPED research object: a
[modular]({{< ref "stamped_principles/m" >}}) collection that can be included
as a git submodule or DataLad sub-dataset, providing
[portable]({{< ref "stamped_principles/p" >}}) access to pinned container
versions without each project having to manage its own images.

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

4. **Print version information early**: `awk --version | head -n 1` or
   `git --version` at the top helps recipients match your environment.

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

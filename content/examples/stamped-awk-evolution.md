---
title: "From Script to STAMPED Research Object"
date: 2026-02-20
description: "Progressive evolution of a simple data analysis from throwaway script to fully STAMPED research object"
summary: "Four scenarios showing how to incrementally add STAMPED properties to a shell-based analysis using git, make, and singularity."
tags: ["shell", "posix", "awk", "make", "git", "singularity", "containers"]
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

## The task

Sum prices from a tiny CSV — a grocery receipt:

```csv
item,price
apples,1.50
bread,2.30
milk,3.20
```

Processing: `awk -F, 'NR>1 {sum+=$2} END {printf "%.2f\n", sum}' prices.csv`

Result: `7.00`

This is trivially understandable, yet enough to demonstrate every STAMPED
property across four progressive scenarios.  Each scenario script follows the
[ephemeral shell reproducer]({{< ref "examples/ephemeral-shell-reproducer" >}})
skeleton for portability.

## Scenario 1: Self-contained script (S, E)

The simplest case: a single script that creates the data inline, sums the
prices, and prints the total.  Requires only POSIX `sh` and `awk`.

```sh
#!/bin/sh
# pragma: testrun scenario-1
# pragma: requires sh awk
# Grocery receipt: sum prices from a CSV

set -eux
PS4='> '
cd "$(mktemp -d "${TMPDIR:-/tmp}/grocery-XXXXXXX")"

# --- generate data ---
cat > prices.csv <<'EOF'
item,price
apples,1.50
bread,2.30
milk,3.20
EOF

# --- process: sum the prices ---
export LC_ALL=C

awk -F, 'NR>1 {sum+=$2} END {printf "%.2f\n", sum}' prices.csv > total.txt

echo "=== Total ==="
cat total.txt
```

This script is [self-contained]({{< ref "stamped_principles/s" >}}) (the data
is generated inline) and [ephemeral]({{< ref "stamped_principles/e" >}}) (runs
in a fresh temp directory).

**Why `LC_ALL=C`?**  The decimal point is locale-dependent.  On a system with
`LC_ALL=de_DE.UTF-8`, `awk` might interpret `1.50` as `1` (treating `.` as a
thousands separator) or produce output with commas instead of periods.  Setting
`LC_ALL=C` forces POSIX numeric conventions — consistent behavior regardless
of the host locale.

Unlike the more complex aggregation patterns (e.g., per-group means with
`for (key in array)`), a simple `sum += $2` does not suffer from
implementation-defined iteration order, so no `| sort` is needed here.

## Scenario 2: Makefile as actionable specification (+ T, A)

The same analysis, but now organized as a git repository with a `Makefile`
that declares the dependency graph.  This adds
[tracking]({{< ref "stamped_principles/t" >}}) (git records every change)
and [actionability]({{< ref "stamped_principles/a" >}}) (`make` re-derives
results from source).

```sh
#!/bin/sh
# pragma: testrun scenario-2
# pragma: requires sh awk make git
# pragma: materialize grocery-analysis
# Grocery receipt as a tracked, actionable git repository

set -eux
PS4='> '
cd "$(mktemp -d "${TMPDIR:-/tmp}/grocery-XXXXXXX")"

git init grocery-analysis
cd grocery-analysis
git config user.email "demo@example.com"
git config user.name "Demo User"

# --- data ---
cat > prices.csv <<'EOF'
item,price
apples,1.50
bread,2.30
milk,3.20
EOF

# --- analysis script ---
cat > sum-prices.sh <<'SCRIPT'
#!/bin/sh
set -eu
export LC_ALL=C
awk -F, 'NR>1 {sum+=$2} END {printf "%.2f\n", sum}' prices.csv > total.txt
SCRIPT
chmod +x sum-prices.sh

# --- Makefile: the actionable specification ---
cat > Makefile <<'MF'
.POSIX:

all: total.txt

total.txt: prices.csv sum-prices.sh
	./sum-prices.sh

clean:
	rm -f total.txt

.PHONY: all clean
MF

# --- README ---
cat > README.md <<'README'
# Grocery Receipt Analysis

Run `make` to produce `total.txt` from `prices.csv`.

Requires: POSIX sh, awk, make.
README

# --- .gitignore: outputs are derived, not tracked ---
cat > .gitignore <<'GI'
total.txt
GI

git add -A
git commit -m "Initial commit: grocery receipt analysis"

# --- run it ---
make
echo "=== Total ==="
cat total.txt
echo ""
echo "=== Provenance: the Makefile + git log ==="
git log --oneline
```

The `Makefile` is the actionable specification: it declares that `total.txt`
depends on `prices.csv` and `sum-prices.sh`, and `make` will only re-run
the analysis when an input changes.  Git tracks the full history.

This is a substantial improvement over a loose script: `git clone` + `make`
is all anyone needs to reproduce the result.  But `make` records *what*
to run, not *what environment* to run it in — the host's `awk` version is
still implicit.

## Scenario 3: Containerized execution with Alpine (+ P)

To pin the computational environment, we run the analysis inside a minimal
[Alpine Linux](https://hub.docker.com/_/alpine) container (~3 MB as a `.sif`
image).  Alpine includes BusyBox `awk` — exactly what our script needs,
nothing more.

The examples below use [Singularity](https://sylabs.io/singularity/) to pull
and execute the container.  The same approach works with
[Apptainer](https://apptainer.org/) (the open-source fork — just replace
`singularity` with `apptainer`), or with Docker/Podman if you prefer an
OCI-native workflow (`docker run --rm -v "$PWD:$PWD" -w "$PWD" alpine:3.21
./sum-prices.sh`).

```sh
#!/bin/sh
# pragma: testrun scenario-3
# pragma: requires sh awk make git singularity
# pragma: timeout 120
# pragma: materialize grocery-analysis
# Grocery receipt with containerized execution via Alpine

set -eux
PS4='> '
cd "$(mktemp -d "${TMPDIR:-/tmp}/grocery-XXXXXXX")"

# --- pull a minimal container image ---
singularity pull docker://alpine:3.21

git init grocery-analysis
cd grocery-analysis
git config user.email "demo@example.com"
git config user.name "Demo User"

# --- same data and script as Scenario 2 ---
cat > prices.csv <<'EOF'
item,price
apples,1.50
bread,2.30
milk,3.20
EOF

cat > sum-prices.sh <<'SCRIPT'
#!/bin/sh
set -eu
export LC_ALL=C
awk -F, 'NR>1 {sum+=$2} END {printf "%.2f\n", sum}' prices.csv > total.txt
SCRIPT
chmod +x sum-prices.sh

# --- Makefile: run inside the container ---
cat > Makefile <<'MF'
.POSIX:
SIF = ../alpine_3.21.sif

all: total.txt

total.txt: prices.csv sum-prices.sh $(SIF)
	singularity exec --cleanenv $(SIF) ./sum-prices.sh

clean:
	rm -f total.txt

.PHONY: all clean
MF

cat > .gitignore <<'GI'
total.txt
GI

cat > README.md <<'README'
# Grocery Receipt Analysis (containerized)

Run `make` to produce `total.txt` from `prices.csv`.

The analysis runs inside an Alpine Linux container to guarantee
identical results regardless of the host system's awk version.

Requires: POSIX sh, make, singularity (or apptainer).
The container image (`alpine_3.21.sif`) must be present in the
parent directory — see Makefile for details.
README

git add -A
git commit -m "Initial commit: containerized grocery receipt analysis"

# --- run it ---
make
echo "=== Total ==="
cat total.txt
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

## Scenario 4: Container committed to git (recovering S, + M, D)

The Alpine `.sif` image is only ~3 MB — small enough to commit directly
to the git repository.  Now the container travels *with* the code and data.
No network access needed to reproduce.

```sh
#!/bin/sh
# pragma: testrun scenario-4
# pragma: requires sh make git singularity
# pragma: timeout 120
# pragma: materialize grocery-analysis
# pragma: materialize raw-data-work
# Grocery receipt: fully self-contained with container in git

set -eux
PS4='> '
cd "$(mktemp -d "${TMPDIR:-/tmp}/grocery-XXXXXXX")"

# --- build the container image from a pinned digest ---
singularity pull env.sif docker://alpine@sha256:a8560b36e8b8210634f77d9f7f9efd7ffa463e380b75e2e74aff4511df3ef88c

git init grocery-analysis
cd grocery-analysis
git config user.email "demo@example.com"
git config user.name "Demo User"

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
  git config user.email "demo@example.com"
  git config user.name "Demo User"
  cat > prices.csv <<'EOF'
item,price
apples,1.50
bread,2.30
milk,3.20
EOF
  git add prices.csv
  git commit -m "Add grocery prices"
  git push
)
# In a real project, use a proper URL (https://... or git@...:...).
# For this local demo, we must allow the file:// transport
# (restricted by default since Git 2.38.1, CVE-2022-39253).
git -c protocol.file.allow=always submodule add ../raw-data.git raw-data

# --- analysis script ---
cat > sum-prices.sh <<'SCRIPT'
#!/bin/sh
set -eu
export LC_ALL=C
awk -F, 'NR>1 {sum+=$2} END {printf "%.2f\n", sum}' raw-data/prices.csv > total.txt
SCRIPT
chmod +x sum-prices.sh

# --- Makefile: run inside the local container ---
cat > Makefile <<'MF'
.POSIX:
SIF = env.sif

all: total.txt

total.txt: raw-data/prices.csv sum-prices.sh $(SIF)
	singularity exec --cleanenv $(SIF) ./sum-prices.sh

clean:
	rm -f total.txt

.PHONY: all clean
MF

cat > .gitignore <<'GI'
total.txt
GI

cat > README.md <<'README'
# Grocery Receipt Analysis

Run `make` to produce `total.txt` from raw price data.

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
echo "=== Total ==="
cat total.txt
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

The progression across all four scenarios illustrates a general pattern: each
STAMPED property you add removes a class of failure, but introducing an
external dependency (the container) can *remove* properties you already had
(self-containment) unless you provision for it explicitly.

## Beyond git: scaling with git-annex and DataLad

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

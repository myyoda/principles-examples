---
title: "Ephemeral Shell Scripts for Reproducing Issues"
date: 2026-02-19
description: "A pattern for writing minimal, self-contained shell scripts that reproduce software issues in temporary environments"
summary: "Distills a common practice among open-source developers: writing throwaway shell scripts that set up a fresh environment, reproduce a problem, and can be shared as actionable bug reports or starting points for test cases."
tags: ["shell", "posix", "reproducer", "bug-report", "testing"]
stamped_principles: ["E", "A", "P", "S"]
fair_principles: ["R", "A"]
instrumentation_levels: ["data-organization"]
aspirations: ["reproducibility", "rigor", "transparency"]
params:
  tools: ["sh", "git"]
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


TODO: rework examples as a spectrum of STAMPED scenarios - from a simple self-contained script to a script producing a STAMPED object with its own provenance etc recorded; to the one including container one way or another; to the one modularly including some other module (like ///repronim/containers) or some original "sub-dataset".  I think  for container we could use some basic lolcow container which would produce us a nice "asciiart!"

### Scenario 1: git-annex fails to sync unlocked file content

A user reports that after unlocking a file, modifying it, and committing, `git
annex sync` does not transfer the new content to a sibling.

```sh
#!/bin/sh
# Reproducer for git-annex content sync issue with unlocked files

set -eu

set -x
PS4='> '

cd "$(mktemp -d "${TMPDIR:-/tmp}/gx-XXXXXXX")"

git init main
(
  cd main
  git annex init main
  echo "original" > data.txt
  git annex add data.txt && git commit -m "add data"

  git annex unlock data.txt
  echo "modified" >> data.txt
  git annex add data.txt && git commit -m "modify data"

  git clone . ../sibling
  git -C ../sibling annex init sibling
  git remote add sibling ../sibling

  git annex sync sibling
  git annex copy --to sibling --all
)

(
  cd sibling
  git annex sync
  # Does the sibling have both versions?
  git annex list
  # Can we get the content?
  git annex get data.txt
  cat data.txt
)
```

### Scenario 2: datalad save with nested subdatasets

A user finds that `datalad save -r` in a superdataset does not pick up changes
made in a sub-subdataset when the intermediate subdataset has not been
explicitly saved.

```sh
#!/bin/sh
# Reproducer for datalad recursive save with nested subdatasets

set -eu

set -x
PS4='> '

cd "$(mktemp -d "${TMPDIR:-/tmp}/dl-XXXXXXX")"

datalad create super
(
  cd super
  datalad create -d . middle
  datalad create -d middle middle/inner

  # Add file at the deepest level
  echo "deep content" > middle/inner/data.txt
  datalad save -d middle/inner -m "add data to inner"

  # middle is now dirty (inner's commit changed), but not saved
  # Does -r from super handle this?
  datalad status -r
  datalad save -r -m "save everything recursively"
  datalad status -r
)
```

### Scenario 3: portable checksum verification

Not all reproducers need DataLad or git-annex.  This scenario demonstrates
verifying file integrity using only POSIX tools — relevant for anyone
distributing datasets as tarballs.

```sh
#!/bin/sh
# Verify that a tarball's contents match a manifest of checksums
# Requires: sh, sha256sum (or shasum on macOS), tar

set -eu
cd "$(mktemp -d "${TMPDIR:-/tmp}/chk-XXXXXXX")"

# Detect checksum tool (portability across Linux/macOS)
if command -v sha256sum >/dev/null 2>&1; then
  SHA256="sha256sum"
elif command -v shasum >/dev/null 2>&1; then
  SHA256="shasum -a 256"
else
  echo "ERROR: no sha256 tool found" >&2
  exit 1
fi

# Create sample data and a manifest
mkdir -p dataset
echo "subject-01 measurement data" > dataset/sub-01.tsv
echo "subject-02 measurement data" > dataset/sub-02.tsv

# Generate manifest
(cd dataset && $SHA256 *.tsv) > CHECKSUMS.sha256

# Package
tar czf dataset.tar.gz dataset/ CHECKSUMS.sha256

# --- simulate receiving the tarball on another machine ---
mkdir -p received && cd received
tar xzf ../dataset.tar.gz

# Verify
(cd dataset && $SHA256 -c ../CHECKSUMS.sha256)
echo "All checksums verified."
```

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

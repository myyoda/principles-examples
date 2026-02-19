---
title: "Datasette and MVC Pattern for Actionable Data Exploration"
date: 2026-02-19
description: "Using datasette and the MVC pattern to make datasets directly explorable and queryable"
summary: "Shows how datasette turns static datasets into interactive, queryable web applications following an MVC-like pattern."
tags: ["datasette", "mvc", "data-exploration", "sqlite"]
stamped_principles: ["A", "S"]
fair_principles: ["A", "I"]
instrumentation_levels: ["pattern"]
aspirations: ["transparency", "efficiency"]
params:
  tools: ["datasette", "sqlite"]
  difficulty: "intermediate"
  verified: false
state: uncurated-ai
---

## The problem: datasets as inert files

Most research datasets are distributed as flat files -- CSVs, TSVs, JSON
dumps, or binary formats.  To explore them, a user must:

1. Download the files.
2. Write a script (often in Python or R) to load and query the data.
3. Figure out the schema by reading a README or inspecting column headers.
4. Iterate through increasingly complex queries as they form hypotheses.

Each of these steps is a barrier.  The dataset is **inert**: it does not
help the user understand its contents.  The first meaningful interaction
with the data requires writing code.

This is at odds with the **Actionability** principle, which says that
dataset operations should be executable, not just documented.  If
exploring a dataset requires writing bespoke scripts before even seeing
the data, the dataset is not actionable -- it is passive.

## The solution: datasette makes data instantly explorable

[Datasette](https://datasette.io/) is an open-source tool that takes a
SQLite database file and serves it as an interactive web application.
With a single command, it provides:

- A **browseable web UI** for every table, with sorting, filtering, and
  full-text search.
- A **SQL query interface** where users can write and share arbitrary
  queries.
- A **JSON API** for programmatic access to any query result.
- **Export to CSV, JSON, and other formats** directly from the browser.

The setup cost is minimal: one file (the SQLite database) and one command
(`datasette serve`).  There is no database server to configure, no ORM to
write, no web application framework to learn.

## The MVC analogy

Datasette naturally follows a Model-View-Controller (MVC) decomposition,
which helps explain why it works so well as a data exploration tool:

### Model: the SQLite database

The SQLite file *is* the model.  It contains the data, the schema (table
definitions, column types, indexes), and optionally metadata (views,
triggers, comments).

```
research.db
  |-- participants     (id, age, group, consent_date)
  |-- measurements     (participant_id, session, score, timestamp)
  |-- stimuli          (id, category, filename, duration_ms)
```

SQLite is a particularly good fit for the Self-containment principle:

- **Single file.** The entire database is one file.  No server process,
  no connection strings, no configuration.
- **Self-describing schema.** The table structure, column types, and
  relationships are embedded in the file.
- **Cross-platform.** SQLite files are portable across operating systems
  and architectures.
- **Versioned.** A SQLite file can be tracked in Git (for small datasets)
  or git-annex (for larger ones).

### View: the datasette web UI

Datasette generates a web interface automatically from the database
schema.  Each table gets a paginated, sortable, filterable page.  Each
row links to a detail view.  The SQL query page provides a scratchpad for
ad-hoc analysis.

This is the *view* layer: it presents the model's data in a human-readable
form without altering the underlying data.

### Controller: SQL queries and plugins

The *controller* layer is the SQL query interface, augmented by datasette
plugins.  Users interact with the data by:

- Applying column filters (translated to `WHERE` clauses).
- Sorting by columns (translated to `ORDER BY`).
- Writing custom SQL queries.
- Using plugins for specialized visualizations (maps, charts, dashboards).

The controller does not modify the data (datasette is read-only by
default).  It translates user intent into queries against the model and
passes the results to the view.

## Step-by-step: from CSV to explorable dataset

### 1. Prepare your data as CSV

Suppose you have a research dataset as CSV files:

```
data/
  participants.csv
  measurements.csv
  stimuli.csv
```

With `participants.csv` containing:

```csv
id,age,group,consent_date
P001,34,control,2025-06-15
P002,28,treatment,2025-06-16
P003,41,control,2025-06-17
P004,35,treatment,2025-06-18
...
```

### 2. Convert CSV to SQLite

Use the `sqlite-utils` companion tool (by the same author as datasette)
to import CSV files into a SQLite database:

```bash
pip install sqlite-utils

sqlite-utils insert research.db participants data/participants.csv --csv --detect-types
sqlite-utils insert research.db measurements data/measurements.csv --csv --detect-types
sqlite-utils insert research.db stimuli data/stimuli.csv --csv --detect-types
```

The `--detect-types` flag tells `sqlite-utils` to infer column types
(integer, float, text, date) rather than storing everything as text.

You can also add metadata to make the database more self-documenting:

```bash
# Add a description to the database
sqlite-utils insert research.db _metadata - --json << 'EOF'
[{"key": "title", "value": "Cognitive Study Dataset"},
 {"key": "description", "value": "Behavioral measurements from a controlled cognitive study, 2025"},
 {"key": "license", "value": "CC-BY-4.0"},
 {"key": "contact", "value": "researcher@university.edu"}]
EOF

# Create useful indexes for common queries
sqlite-utils create-index research.db measurements participant_id
sqlite-utils create-index research.db measurements session
```

### 3. Serve with datasette

```bash
pip install datasette
datasette serve research.db
```

Open `http://localhost:8001` in a browser.  You immediately see:

- A list of tables (participants, measurements, stimuli).
- Click any table to browse its rows with sorting and filtering.
- A SQL query page to write arbitrary queries.
- JSON and CSV export links on every page.

### 4. Add a metadata file for richer presentation

Datasette supports a `metadata.yml` (or `.json`) file that adds
descriptions, titles, and licensing information to the web interface:

```yaml
title: "Cognitive Study Dataset"
description: "Behavioral measurements from a controlled cognitive study"
license: "CC-BY-4.0"
databases:
  research:
    description: "Main study database"
    tables:
      participants:
        description: "Demographics and consent information for study participants"
        columns:
          id: "Unique participant identifier"
          age: "Age in years at time of consent"
          group: "Experimental group assignment (control or treatment)"
          consent_date: "Date informed consent was obtained"
      measurements:
        description: "Behavioral scores recorded per session"
        columns:
          participant_id: "Foreign key to participants.id"
          session: "Session number (1-indexed)"
          score: "Composite behavioral score (0-100 scale)"
          timestamp: "UTC timestamp of measurement"
      stimuli:
        description: "Stimulus materials used across sessions"
```

Serve with metadata:

```bash
datasette serve research.db --metadata metadata.yml
```

Now each table page shows its description and column-level documentation
directly in the browser.

### 5. Example queries users can run immediately

The SQL page allows anyone to explore the data without writing Python or R.
Some examples:

**Average score by group:**

```sql
SELECT
    p.group,
    AVG(m.score) AS mean_score,
    COUNT(*) AS n_measurements
FROM measurements m
JOIN participants p ON m.participant_id = p.id
GROUP BY p.group;
```

**Participant scores across sessions (for a single participant):**

```sql
SELECT session, score, timestamp
FROM measurements
WHERE participant_id = 'P001'
ORDER BY session;
```

**Stimuli summary by category:**

```sql
SELECT
    category,
    COUNT(*) AS n_stimuli,
    AVG(duration_ms) AS mean_duration_ms
FROM stimuli
GROUP BY category;
```

Each of these queries is a URL.  Datasette encodes the query in the URL
parameters, so results can be shared by simply copying the browser address
bar.  This turns ad-hoc data exploration into shareable, reproducible
interactions.

## How this makes data "actionable"

Traditional datasets require a multi-step setup process before any
interaction is possible.  Datasette collapses this:

| Workflow step           | Traditional CSV                       | Datasette + SQLite               |
|-------------------------|---------------------------------------|----------------------------------|
| Get the data            | Download files                        | Download one `.db` file          |
| Understand the schema   | Read README, inspect headers          | Browse table pages with docs     |
| First query             | Write Python/R script, import pandas  | Click a table, apply filters     |
| Complex query           | More scripting                        | Write SQL in the browser         |
| Share a result          | Email a script or screenshot          | Share a URL                      |
| Programmatic access     | Parse files with custom code          | Call the JSON API                |

The dataset goes from "inert file that requires programming to explore"
to "interactive application that answers questions immediately."

## Self-containment: the SQLite file as a self-documenting artifact

The SQLite file embodies the **Self-containment** principle in a way that
CSVs do not:

- **Schema is embedded.** Column types, constraints, and indexes are part
  of the file, not a separate data dictionary.
- **Relationships are explicit.** Foreign keys connect tables, making the
  data model navigable.
- **Metadata can be included.** Descriptions, licenses, and provenance
  notes can be stored in dedicated metadata tables.
- **Queries are portable.** SQL is a universal language; the queries
  themselves serve as documentation of what the data contains.

A single `.db` file plus a `metadata.yml` file is a complete, self-contained,
explorable dataset.

## Extending with plugins

Datasette has a rich plugin ecosystem for specialized use cases:

- **datasette-cluster-map**: Automatically display rows with latitude/longitude
  columns on an interactive map.
- **datasette-vega**: Add Vega-Lite chart visualizations to any query result.
- **datasette-export-notebook**: Export query results as Jupyter notebooks.
- **datasette-graphql**: Expose the database as a GraphQL API in addition
  to REST.
- **datasette-publish-fly**: Deploy a datasette instance to Fly.io with a
  single command.

Install and enable plugins to customize the view and controller layers
without changing the underlying data model:

```bash
datasette install datasette-vega
datasette serve research.db --metadata metadata.yml
```

Now every query result page includes an option to render the result as a
bar chart, line chart, or scatter plot, directly in the browser.

## Deployment options for sharing

Datasette can be deployed in multiple ways, making it practical for both
local exploration and public data sharing:

```bash
# Local exploration (default)
datasette serve research.db

# Static JSON export (no server needed, hostable on GitHub Pages)
datasette publish github-pages research.db --metadata metadata.yml

# Containerized deployment
datasette package research.db --metadata metadata.yml -t my-dataset:latest
docker run -p 8001:8001 my-dataset:latest

# Cloud deployment
datasette publish fly research.db --app my-study-data --metadata metadata.yml
```

The static export option is particularly interesting for research: it
generates a set of static JSON files that can be hosted on any web server,
including GitHub Pages.  The dataset becomes a permanent, citable,
explorable web resource with no running server required.

## Summary

Datasette demonstrates that making data actionable does not require
building a custom web application.  By storing data in SQLite (a
self-contained, self-describing format) and serving it with datasette (an
off-the-shelf exploration tool), you get:

- **Immediate explorability**: no code required to start querying.
- **Shareable interactions**: every query is a URL.
- **Programmatic access**: JSON API for scripted workflows.
- **Self-containment**: one file carries data, schema, and metadata.
- **Extensibility**: plugins add visualizations and specialized views.

The MVC decomposition -- SQLite as model, datasette UI as view, SQL
queries and plugins as controller -- is a pattern that can be applied to
any tabular research dataset to make it instantly actionable.

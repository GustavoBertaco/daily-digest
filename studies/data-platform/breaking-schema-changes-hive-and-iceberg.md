# Breaking Schema Changes in a Hybrid Hive and Iceberg Estate

> How a breaking schema change behaves differently on Hive tables and on Iceberg tables, why the
> break does not disappear under Iceberg but relocates to the consumer, how the market versions
> tables once a change has broken something, and which technologies are actually required to
> manage those versions when half your estate is one format and half is the other.

- **Topic:** Data Platform
- **Date:** 2026-09-04
- **Status:** draft

> *The words written here are all AI-generated, but all the content was critically reviewed
> and validated by me — the use of AI is to accelerate the knowledge searching and narrative
> building.*

## Contents

1. [Context](#context)
2. [Two formats, two kinds of breakage](#1-two-formats-two-kinds-of-breakage)
3. [The operation-by-operation comparison](#2-the-operation-by-operation-comparison)
4. [What is still breaking under Iceberg](#3-what-is-still-breaking-under-iceberg)
5. [Versioning a table after the change: four layers](#4-versioning-a-table-after-the-change-four-layers)
6. [What versioning costs](#5-what-versioning-costs)
7. [Choosing, for a hybrid estate](#6-choosing-for-a-hybrid-estate)
8. [Counterpoints: where this study could be wrong](#7-counterpoints-where-this-study-could-be-wrong)
9. [Takeaways](#takeaways)
10. [References](#references)

## Context

This study is written for a specific situation: **a platform where part of the estate is Hive
tables and part is Iceberg tables**, and both will coexist for a while. That constraint is not a
detail — it is what makes the problem interesting, because the two formats fail in ways different
enough that **a single breaking-change policy cannot cover both**, and most published guidance
quietly assumes you are on one or the other.

Three questions, in order:

1. What patterns exist for handling a breaking schema change on a Hive table versus an Iceberg
   table, and how do the failure modes differ?
2. Once a breaking change has happened, how does the market version tables?
3. What technologies are actually required to manage those versions?

The short version of the answer, stated up front so the rest can argue for it: **Hive breaks
physically, Iceberg cannot — and that is why Iceberg breaks silently instead.** Field IDs remove
the class of corruption that makes Hive dangerous, and in doing so they move the failure from a
layer that shouts to a layer that whispers. Versioning exists to catch what the format no longer
catches for you.

*A note on sources.* The Iceberg specification and evolution docs were read directly from the
Apache repository, along with the relevant Hive JIRA issues, and those carry the load-bearing
claims. Quantitative material on snapshot retention cost comes from vendor and practitioner blogs
and is **directional, not audited** — useful for order of magnitude, not for citation as fact.

## 1. Two formats, two kinds of breakage

### 1.1 On Hive, the break is physical

A Hive table is a directory layout plus a schema in the metastore. The data files — Parquet, ORC,
Avro — carry their own schema, and *nothing structurally binds the two together*. Reading a Hive
table therefore requires reconciling the metastore's column list with each file's column list, and
the mechanism for that reconciliation is where the damage lives.

**The reconciliation can be by position.** In the positional model, the third column in the file is
the third column in the schema, regardless of what either is called. Add a column in the middle of
a table and every file written before that change is now misaligned: what the metastore believes is
column 1 is physically column 2 in the old files. The concrete symptom reported in practice is a
type error — an `int` at index 1 in one partition meeting a `boolean` at index 1 in another —
surfacing only when a query touches the older partitions
([prestodb#12212](https://github.com/prestodb/presto/issues/12212)).

**Whether it is positional depends on the format, the engine, and a config flag** — and this is the
real problem, more than any single default. `parquet.column.index.access` and
`orc.force.positional.evolution` toggle the behavior in Hive 3; Presto and Trino have their own
`hive.parquet.use-column-names`-style settings; and the ecosystem has changed its mind about
defaults before, with ORC-54 moving ORC to name-based resolution and
[HIVE-20129](https://issues.apache.org/jira/browse/HIVE-20129) reverting Hive to positional for ORC
tables. The practical consequence for an operator is blunt: **on Hive, "is a rename safe?" has no
format-level answer — it has a per-engine, per-format, per-config answer**, and the same table can
be read correctly by one engine and incorrectly by another.

**Partition metadata is a second, independent break.** Each partition carries its own serde
metadata. `ALTER TABLE ... REPLACE COLUMNS` without `CASCADE` updates the table definition and
leaves the partitions behind; when the table serde and partition serde no longer line up, reads of
those partitions fail outright
([HIVE-16559](https://issues.apache.org/jira/browse/HIVE-16559)). This is a good failure in one
narrow sense — it is loud — but it is a failure discovered by consumers at query time, not by the
producer at change time.

**And partitioning itself cannot evolve.** Hive partition values are encoded in directory paths.
Changing the partitioning scheme means rewriting the table. There is no metadata-only path.

### 1.2 On Iceberg, the break is impossible — physically

Iceberg assigns every field a **stable integer ID**, and the schema is a mapping from those IDs to
names and types. Data files are associated with schema fields by ID, never by name or position.
Rename a column and the ID does not move; the files are untouched and still resolve correctly.
Drop a column and its ID is retired permanently — **IDs are never reused**, which is what prevents
a later `add` from silently inheriting a dropped column's data.

The specification states its correctness guarantees explicitly, and they are worth quoting because
their precise scope matters more than their reassuring tone
([Iceberg evolution docs](https://github.com/apache/iceberg/blob/main/docs/docs/evolution.md)):

> 1. Added columns never read existing values from another column.
> 2. Dropping a column or field does not change the values in any other column.
> 3. Updating a column or field does not change values in any other column.
> 4. Changing the order of columns or fields in a struct does not change the values associated
>    with a column or field name.

Read that list carefully. **Every guarantee is about data correctness. None is about query
compatibility.** Iceberg promises that your remaining columns still contain what they contained. It
does not promise that anything downstream still runs. Conflating those two readings is, in my
view, the single largest source of schema-change incidents on Iceberg estates — teams read
"schema evolution is safe" as "schema changes are safe to ship."

Partition evolution is genuinely different in kind from Hive. Because the partition spec is
metadata and partition values are derived through transforms rather than encoded in paths, **the
spec can change without rewriting a single file**. Old data keeps the old spec, new data adopts the
new one, and split planning handles a query that spans both. Sort order evolves the same way.

### 1.3 The reframing

So the comparison is not "Hive is unsafe, Iceberg is safe." It is:

| | Hive | Iceberg |
|---|---|---|
| Where the break lands | Storage/read layer | Consumer/query layer |
| How it announces itself | Type errors, failed partition reads, wrong values | Failed queries — **or silent nulls** |
| Who discovers it | Whoever queries an old partition | Whoever depended on the column name |
| Is it configurable away? | Partly, per engine and format | Not applicable — the format is not the problem |
| Can partitioning change? | No, requires full rewrite | Yes, metadata-only |

Iceberg removes an entire class of physical failure. What it does not do — and does not claim to
do — is tell you whether the change is safe to make.

## 2. The operation-by-operation comparison

For an estate running both, this is the table worth internalizing. "Safe" here means *the format
resolves the change without data damage*; it says nothing about consumers, which §3 handles.

| Operation | Hive | Iceberg |
|---|---|---|
| **Add column at end** | Generally safe | Safe, metadata-only |
| **Add column in middle** | **Dangerous** under positional resolution — misaligns all prior files | Safe; Iceberg allows adding at any position |
| **Rename column** | **Dangerous** — name-based readers lose the column, positional readers keep it by luck | Safe — ID is stable, data untouched |
| **Drop column** | Risky; positional readers shift | Safe; ID retired and never reused |
| **Reorder columns** | **Dangerous** under positional resolution | Safe, metadata-only |
| **Widen type** | Engine-dependent | Safe, within the allowed promotion set (§3) |
| **Narrow type** | Unsafe | **Not permitted** |
| **Change partitioning** | Requires full table rewrite | Metadata-only; specs coexist |
| **Change a partition's serde** | Requires `CASCADE`, else partition reads fail | Not applicable |

The asymmetry in the "change partitioning" row is the one with the largest operational consequence
in a hybrid estate, because it is the difference between a maintenance window and a `ALTER TABLE`
statement.

**Allowed type promotions in Iceberg are a short, closed list**, and worth memorizing rather than
guessing at ([Iceberg spec](https://github.com/apache/iceberg/blob/main/format/spec.md)):

- v1 and v2: `int` → `long`, `float` → `double`, and `decimal(P,S)` → `decimal(P',S)` where
  `P' > P` — **precision widening only, scale fixed**.
- v3 adds: `date` → `timestamp` or `timestamp_ns`, and `unknown` → any type.

Narrowing is never allowed, in any version. And there is a trap the docs state but few people
internalize: **type promotion is rejected if the field feeds a partition transform whose output
would change after promotion.** A column that is merely data can be widened; the same column used
as a partition source may not be.

For files that predate Iceberg and carry no field IDs — precisely the files you inherit when you
migrate a Hive table in place — Iceberg falls back to a `schema.name-mapping.default` property, a
JSON structure mapping names to field IDs. This is the seam where a migrated table is at its most
fragile, because for those files the resolution really is by name again.

## 3. What is still breaking under Iceberg

If the format cannot corrupt your data, what actually goes wrong? Four things.

**Consumers referencing the old name.** A rename is metadata-only for the data and total for the
SQL. Every dashboard, dbt model, semantic-layer mapping, notebook and downstream job that names the
old column is now wrong. Iceberg's safety guarantee is silent on all of it.

**Silent degradation to null — the dangerous case.** When a column disappears, the failure is not
uniform. Depending on the reader, a consumer fails outright on the next query, errors on the next
refresh, breaks in the semantic layer where the field is still mapped, **or quietly returns null
because the reader tolerates a missing column**. The last one produces no error and no alert: a
metric reads empty until somebody notices the number is wrong, which may be weeks. A Hive
positional break is more dangerous per incident but far easier to detect; an Iceberg drop is
harmless to the data and can be invisible for a long time.

**Changes the format refuses.** Narrowing a type (`long` → `int`, `double` → `float`), tightening
nullability from optional to required, and any promotion that would alter a partition transform's
output. These are rejected rather than accepted-and-broken, which is correct behavior, but they
still constitute "the change I wanted to make and cannot" — and the fallback for them is a rewrite
or a new table, which is where §4 begins.

**Migrated tables carrying legacy files.** Until files are rewritten, tables migrated in place from
Hive depend on name mapping rather than embedded field IDs. A rename on such a table is safe for
files that have IDs and resolved by name for those that do not — the two halves of one table
behaving under two different rules.

The useful summary: **on Iceberg the change is always *valid*; validity is not the same as being
safe to ship.** What the format has done is convert a data-integrity problem into a
change-management problem. That is a large improvement and a real transfer of responsibility, not
an elimination of work.

## 4. Versioning a table after the change: four layers

Once you accept that some changes will break consumers, the question becomes what you can offer
them: a way to keep reading the old shape while they migrate. The market answers this at **four
distinct layers**, and they are not competitors — they operate on different objects and solve
different problems.

### Layer 1 — Snapshots (Iceberg, native)

Every write produces an immutable snapshot: a consistent set of data and metadata files. Queries
can read the table as of a snapshot ID or a timestamp, and `rollback` resets the current pointer
to a previous snapshot without rewriting anything.

**What it is good for:** recovering from a bad write, auditing what a table looked like, debugging
"the number changed yesterday," reproducing a training set.

**What it is not:** a way to publish a stable old interface. A snapshot is a point in time, not a
named version, and it expires (§5). You cannot tell a consumer "read v1 for the next two quarters"
with snapshots alone.

### Layer 2 — Branches and tags (Iceberg, native)

Instead of a single timeline, a table can carry named branches and tags. A tag is a labeled fixed
snapshot; a branch is an independent line of commits. This is the primitive underneath
**write-audit-publish**: write to a staging branch, run validations against it, then fast-forward
`main` only if the audit passes.

**What it is good for:** making the *change itself* safe to perform — the new shape exists and is
queryable before anyone in production sees it. A tag also gives you a named, retained point ("the
schema as of the Q3 close") that survives ordinary snapshot expiry policy.

**What it is not:** multi-table. A branch belongs to one table, so a change spanning several tables
cannot be staged atomically at this layer.

### Layer 3 — Catalog commits (Nessie)

Nessie versions **the catalog** — the registry of which tables exist and which metadata pointer is
current — rather than the data. That shift buys the thing layer 2 cannot do: **atomic commits
across multiple tables**, plus Git semantics (branch, tag, merge, cherry-pick) over the whole
catalog, with zero-copy branching because branches share metadata pointers.

**What it is good for:** a breaking change that must land across several tables at once; isolated
ETL development against a full copy of the catalog; experiments that need a coherent multi-table
world.

**What it is not:** format-agnostic. Nessie is built for Iceberg (and Delta). **It does nothing for
the Hive half of a hybrid estate** — the single most important constraint in this section.

### Layer 4 — Files and objects (lakeFS)

lakeFS applies Git-like branching, commits and merges at the **object storage** level, beneath any
table format. Because it versions bytes rather than table metadata, it is **format-agnostic** and
works with Hive tables, Iceberg tables, raw Parquet, and unstructured files alike, versioning data
independently of the metastore.

**What it is good for:** exactly the hybrid problem. It is the only one of the four layers that
covers a Hive table and an Iceberg table with the same mechanism, letting you branch before a
schema or layout change and validate in isolation regardless of which half of the estate the table
lives in.

**What it is not:** free, or invisible. It sits in the data path and is a real piece of
infrastructure to operate, with its own semantics that engines must be pointed at.

### The layer nobody counts: views as indirection

There is a fifth answer that is not versioning at all, and it is frequently the cheapest one.

The **Iceberg View specification** defines an open, cross-engine metadata format for SQL views,
with its own version history — and crucially, *a view version's representation is immutable; a
changed definition creates a new version*. Because a view is a stored SQL definition, it can
present the old column name over the renamed physical column:

```sql
-- physical table renamed customer_id -> account_id
CREATE OR REPLACE VIEW analytics.orders AS
SELECT account_id AS customer_id, order_ts, amount
FROM warehouse.orders;
```

This is the **expand-and-contract** pattern from application databases, applied to tables: expand
(add the new shape), run both in parallel behind a stable interface, migrate consumers, contract
(drop the old). Views make the consumer interface a separate versioned artifact from the physical
table — which is precisely the separation the whole problem calls for. The same pattern shows up
in warehouses as side-by-side tables (`orders_v1`, `orders_v2`) with a view or synonym doing the
routing, and it is the closest thing the Hive half of an estate has to native versioning.

### The hybrid constraint, stated plainly

For an estate that is part Hive and part Iceberg, the four layers cover very different ground:

| Layer | Iceberg tables | Hive tables |
|---|---|---|
| Snapshots | Native | **None** |
| Branches / tags | Native | **None** |
| Catalog commits (Nessie) | Yes | **No** |
| Files / objects (lakeFS) | Yes | **Yes** |
| Views as indirection | Yes (Iceberg View spec) | Yes (engine views) |

**Hive has no native notion of a versioned table.** In practice teams simulate it by copying data
into timestamped partitions or keeping backup copies on HDFS — manual, expensive, and unable to
support rollback without reprocessing. Hive ACID transactional tables add transactional writes
through base and delta files with compaction, but they were designed for moderate concurrency and
do not provide the snapshot history, time travel or rollback that Iceberg gives natively.

So there are exactly **two mechanisms that span both halves of a hybrid estate**: object-level
versioning, and view indirection. Everything else is Iceberg-only. That is the finding that should
drive the technology decision in §6.

## 5. What versioning costs

Versioning is often discussed as though retaining history were free. It is not, and the cost has a
counter-intuitive shape.

Every write — insert, update, delete, and every compaction run — produces a new snapshot entry in
the table's metadata. Iceberg retains all past snapshots by default. The consequence is metadata
growth proportional to commit rate rather than to data volume, which is why streaming and
frequently-compacted tables suffer worst.

**And the dominant cost is not storage, it is query planning time.** Every query must plan against
current metadata; bloated manifest and metadata files slow down every read, including reads that
never touch history. Storage waste is real too — expired-but-unreclaimed files remain physically
billable — but the operational pain shows up first as queries getting slower for no visible reason.

Practitioner figures circulating in 2026 put a table with twelve months of unexpired snapshots at
roughly **3–5× the metadata size** of the same table on a seven-day retention window, and recommend
retention of **7–30 days combined with a minimum snapshot count of 5–10** for typical production
workloads. *(Directional; these come from vendor and practitioner blogs, not independent
measurement.)*

Two consequences follow, and both matter for §6:

1. **Time travel is not a long-term versioning strategy.** If your retention window is thirty days,
   you cannot offer a consumer a year to migrate off an old shape by pointing them at a snapshot.
   Tags survive expiry policy where plain snapshots do not, which is exactly why they exist — but
   a tag pins its files, so a retained tag is a retained storage cost you chose deliberately.
2. **Maintenance is not optional.** `expire_snapshots` and manifest rewriting are part of running
   the format, not a tuning exercise. A versioning strategy without a retention policy is a cost
   curve with no ceiling.

## 6. Choosing, for a hybrid estate

Bringing §4 and §5 together into decisions.

### Which layer, for which problem

| If the problem is… | Reach for | Why not the others |
|---|---|---|
| A bad write to undo | Snapshot rollback (Iceberg) | Cheapest; already there; no infrastructure |
| Validating a change before anyone sees it | Branch + WAP (Iceberg) | Snapshots are after-the-fact; catalog/file layers are heavier |
| A named point that must survive retention | Tag (Iceberg) | A snapshot expires; a tag is a deliberate pin |
| A change spanning several tables atomically | Nessie | Branches are per-table; nothing below the catalog is transactional across tables |
| The same guarantee on Hive **and** Iceberg | lakeFS | Every native mechanism is Iceberg-only |
| Letting consumers keep the old shape | Views (expand-and-contract) | Not versioning at all — and usually the right answer anyway |

### The minimum that is actually required

Strip away what is optional and the required set is small:

- **Iceberg snapshots plus a retention policy.** You get them whether you plan for them or not;
  the policy is the part you must supply. Not adopting this is not an option, it is a default you
  are accepting silently.
- **A view layer as the consumer interface.** This is the highest-leverage item in the list and the
  cheapest, because it is the only one that decouples "what the table is called" from "what
  consumers depend on" — and it works on both halves of the estate.
- **Snapshot expiration and manifest maintenance, scheduled.** Per §5, versioning without
  maintenance is an unbounded cost.

Everything else is conditional. **Branches and WAP** earn their place when changes are frequent
enough that validating in production is unacceptable. **Nessie** earns its place only when you
genuinely have multi-table atomic changes — it is a real operational commitment, and a single-table
branch is usually enough. **lakeFS** earns its place when the Hive half is large enough and
long-lived enough that its lack of native versioning is a live risk; if the Hive half is shrinking
on a credible timeline, migrating it is the better spend.

### The catalog question

A hybrid estate usually implies two catalogs — Hive Metastore for one half, an Iceberg REST
catalog for the other. The pattern reported as working is **federate first, migrate second,
decommission third**: run the REST catalog (Polaris, Nessie, Unity) alongside the existing HMS,
point new tables at the REST catalog, and federate so that governance, lineage and access control
are unified immediately rather than at the end of the migration. Engines can be configured with
multiple catalogs simultaneously, so coexistence is a supported configuration rather than a
transitional hack.

### Migration as the strategic answer

For a hybrid estate, most of this study's complexity is a tax on the Hive half. Iceberg provides
three in-place migration procedures, and the useful distinction between them is *how reversible
they are*:

- **`snapshot`** — creates a new Iceberg table pointing at the existing Hive data files, leaving
  the original table untouched. This is the rehearsal: run it, test reads, throw it away.
- **`migrate`** — replaces the Hive table with an Iceberg table in place, preserving schema,
  partitioning and location, and retaining a backup of the original definition by default.
- **`add_files`** — adds existing Hive data files into an already-existing Iceberg table as a new
  snapshot.

All three are metadata-only: the data files are not rewritten, which is why this is dramatically
cheaper than a full rewrite. The caveat from §2 applies and should be planned for — migrated files
carry no field IDs and depend on name mapping until they are rewritten by compaction, so a
migrated table is not fully at Iceberg's safety guarantees on day one.

## 7. Counterpoints: where this study could be wrong

**The Hive picture is a configuration matrix, and I have flattened it.** Positional versus
name-based resolution varies by format, by engine, by Hive version, and by flag, and the ecosystem
has reversed its defaults before. Any statement here of the form "Hive does X" should be verified
against your specific engine and version before you act on it. The defensible claim is the weaker
one: that the behavior is *configuration-dependent rather than guaranteed*, which is itself the
operational problem.

**"Silent nulls are worse than loud failures" is a judgment, not a measurement.** I have argued
that Iceberg's failure mode is more insidious because it can go undetected. Someone could
reasonably counter that loud failures cause real outages while silent nulls are caught by
downstream data quality checks — and that an estate with good observability inverts my ranking. I
have no incident data either way; the claim rests on the reasoning that undetected wrong numbers
propagate into decisions, which loud failures do not.

**The four-layer model is tidier than the market.** Delta Lake sits awkwardly in it: its column
mapping achieves metadata-only rename and drop much as Iceberg field IDs do, and it has time
travel, so a Delta-based estate would redraw several of these boundaries. Catalogs are also
converging on versioning features, which may collapse layers 2 and 3 over time and make a separate
Nessie deployment unnecessary.

**Iceberg v3 may change the versioning calculus and is not accounted for here.** v3 adds row
lineage with per-row identifiers and update sequence numbers, enabling native CDC without external
tooling, along with deletion vectors and a variant type. Row-level lineage could substantially
change what "versioning" needs to mean. Adoption is genuinely uneven as of 2026 — generally
available on Snowflake and in preview on Databricks, shipped across AWS services, but not yet in
open-source Trino — so building on it today is a bet on your specific engine.

**The recommendation to lean on views assumes governed views.** Views as an indirection layer only
work if the view layer is itself managed — versioned, owned, and not proliferating. An estate where
anyone can create a view has replaced a schema-coupling problem with a view-sprawl problem, and I
have not weighed how often that trade goes badly.

## Takeaways

- **Hive breaks physically; Iceberg cannot, which is exactly why it breaks silently.** Field IDs
  eliminate positional corruption and thereby move the failure from the storage layer to the
  consumer layer. The dangerous Iceberg incident is not a crash — it is a column that quietly
  returns null while a metric keeps reporting.

- **Read Iceberg's guarantees literally.** All four are about data correctness — that remaining
  columns still hold their values. None is about whether your queries still run. "Schema evolution
  is safe" and "this schema change is safe to ship" are different statements, and treating them as
  one is the root of most incidents.

- **On Hive, "is this safe?" has no format-level answer.** It resolves per engine, per file format,
  per config flag, and the defaults have changed historically. That uncertainty — not any single
  default — is the thing that makes Hive schema changes expensive to reason about.

- **Only two mechanisms span a hybrid estate: object-level versioning and view indirection.**
  Snapshots, branches, tags and Nessie are all Iceberg-only, and Hive has no native versioned-table
  concept at all. Any versioning policy that must apply uniformly across both halves is therefore
  built on lakeFS, on views, or on finishing the migration.

- **The required set is smaller than the available set.** Snapshots with a retention policy, a
  governed view layer as the consumer interface, and scheduled maintenance. Branches, Nessie and
  lakeFS are conditional on specific problems — multi-table atomicity, or a Hive half large enough
  that its lack of versioning is a standing risk.

- **Versioning's real cost is query planning, not storage.** Metadata grows with commit rate rather
  than data volume, and bloated metadata slows every read including those that never touch history.
  With retention windows realistically at 7–30 days, time travel cannot serve as the long-term
  compatibility promise to a consumer — that job belongs to tags, views, or a parallel table.

- **Open for the next pass:** whether Iceberg v3 row lineage changes what table versioning needs to
  be once engine support is even; measured incident data comparing detection time for Hive
  positional breaks versus Iceberg silent-null breaks; and how catalog-native versioning in Polaris
  and Unity affects the case for running Nessie separately.

## References

*Links checked September 2026. The Apache Iceberg specification, evolution documentation and the
cited Hive JIRA issues were fetched directly and carry every load-bearing claim about format
behavior. Retention and cost figures come from vendor and practitioner blogs and are directional
rather than audited. Vendor material is cited for mechanism, not endorsement.*

### Format behavior (primary)

- **Iceberg evolution documentation — Apache** ([github.com](https://github.com/apache/iceberg/blob/main/docs/docs/evolution.md))
  — the five supported operations, the four correctness guarantees quoted verbatim in §1.2, and
  partition/sort-order evolution semantics. *Supports:* §1.2, §2. *Caveat:* the guarantee list is
  about data correctness only — the central reading of this study.
- **Iceberg table specification — Apache** ([github.com](https://github.com/apache/iceberg/blob/main/format/spec.md))
  — the exact type promotion set per spec version, the partition-transform restriction on
  promotion, and `schema.name-mapping.default` for files without field IDs. *Supports:* §2, §3.
- **HIVE-16559: Parquet schema evolution for partitioned tables may break if table and partition
  serdes differ** ([issues.apache.org](https://issues.apache.org/jira/browse/HIVE-16559))
  — the `REPLACE COLUMNS` without `CASCADE` failure. *Supports:* §1.1.
- **HIVE-20129: Revert to position based schema evolution for orc tables** ([issues.apache.org](https://issues.apache.org/jira/browse/HIVE-20129))
  — evidence that resolution semantics have changed direction historically. *Supports:* §1.1's
  claim that the behavior is configuration-dependent rather than guaranteed.
- **prestodb#12212: Parquet Hive schema evolution checks based on column names** ([github.com](https://github.com/prestodb/presto/issues/12212))
  — the concrete positional-misalignment symptom across partitions. *Supports:* §1.1.

### Consumer-level breakage

- **Schema Evolution in Apache Iceberg: Valid Isn't Safe to Ship — Kastor Data** ([kastordata.io](https://kastordata.io/resources/schema-evolution-apache-iceberg-safe-to-ship))
  — the valid-versus-safe distinction and the enumeration of downstream failure modes including
  silent null degradation. *Supports:* §3, and the framing of §1.3. *Caveat:* vendor blog; the
  reasoning is checkable against the spec, the incident frequency claim is not.
- **Apache Iceberg Schema Evolution in Production: Best Practices and Pitfalls — LakeOps** ([lakeops.dev](https://lakeops.dev/blog/iceberg-schema-evolution-production))
  — which operations remain breaking for consumers, and validating renames against known consumers.
  *Supports:* §3. *Caveat:* vendor.

### Versioning layers

- **Apache Iceberg View Specification** ([iceberg.apache.org](https://iceberg.apache.org/view-spec/),
  [github.com](https://github.com/apache/iceberg/blob/main/format/view-spec.md))
  — cross-engine view metadata with immutable per-version representations. *Supports:* the view
  indirection layer in §4 and its role in the §6 minimum set.
- **Data Lakehouse Versioning Comparison: Nessie, Apache Iceberg, lakeFS — Dremio** ([dremio.com](https://www.dremio.com/blog/data-lakehouse-versioning-comparison-nessie-apache-iceberg-lakefs/))
  — the file / table / catalog versioning distinction that §4's layer model is built on.
  *Supports:* §4. *Caveat:* vendor; Dremio sponsors Nessie.
- **lakeFS documentation and Iceberg integration** ([docs.lakefs.io](https://docs.lakefs.io/iceberg/),
  [lakefs.io](https://lakefs.io/blog/open-table-formats/))
  — format-agnostic object-level versioning, independent of the metastore. *Supports:* §4's layer 4
  and the hybrid-coverage table. *Caveat:* vendor.
- **Iceberg Time Travel and Versioning — lakeFS** ([lakefs.io](https://lakefs.io/blog/iceberg-time-travel/),
  [lakefs.io](https://lakefs.io/blog/iceberg-versioning/))
  — snapshots, rollback, branches and tags, and WAP as the pattern built on them. *Supports:* §4
  layers 1–2. *Caveat:* vendor with a competing product.

### Cost and maintenance

- **Iceberg Snapshot Expiration and GC Best Practices — RisingWave** ([risingwave.com](https://risingwave.com/blog/iceberg-snapshot-expiration-gc/))
  and **Avoiding Metadata Bloat with Snapshot Expiration — Data Lakehouse Hub** ([datalakehousehub.com](https://datalakehousehub.com/blog/iceberg-metadata-bloat-cleanup/))
  — metadata growth with commit rate; planning-time as the dominant cost. *Supports:* §5.
  *Caveat:* vendor/practitioner blogs; **all figures directional**.
- **Apache Iceberg Retention Policy — LakeOps** ([lakeops.dev](https://lakeops.dev/blog/iceberg-retention-policy))
  — the 7–30 day window plus minimum snapshot count. *Supports:* §5, and the §6 conclusion that
  time travel cannot serve as a long-term compatibility promise. *Caveat:* directional.

### Migration and catalogs

- **Hive Migration — Apache Iceberg** ([iceberg.apache.org](https://iceberg.apache.org/docs/1.4.1/hive-migration/))
  and **Migrating a Hive Table to an Iceberg Table — Dremio** ([dremio.com](https://www.dremio.com/blog/migrating-a-hive-table-to-an-iceberg-table-hands-on-tutorial/))
  — `snapshot`, `migrate` and `add_files`, and the recommendation to rehearse with `snapshot`
  first. *Supports:* §6.
- **Hive metastore federation — Databricks** ([docs.databricks.com](https://docs.databricks.com/aws/en/query-federation/hms-federation-concepts))
  — governing HMS-registered tables from a modern catalog without migrating first. *Supports:*
  §6's federate-then-migrate sequencing. *Caveat:* vendor-specific implementation of a general
  pattern.

### Iceberg v3 (context for the counterpoints)

- **What's new in Apache Iceberg v3 — Google Open Source Blog** ([opensource.googleblog.com](https://opensource.googleblog.com/2025/08/whats-new-in-iceberg-v3.html))
  and **Apache Iceberg V2 vs V3 — Dremio** ([dremio.com](https://www.dremio.com/blog/apache-iceberg-v2-vs-v3-what-changed-and-what-it-means-for-your-tables/))
  — deletion vectors, row lineage, VARIANT, default values, geometry types, nanosecond timestamps.
  *Supports:* §7. *Caveat:* engine adoption is uneven; verify against your engine before relying on
  any v3 feature.

### Companion studies

- [[adopting-open-table-formats-at-scale]] — the adoption-and-rollout view of the same formats:
  what consolidated in the market and how an enterprise adopts a format broadly. This study is the
  narrower operational counterpart, about what happens to a single table when its schema changes.
- [[producer-layer-and-contract-gated-democratization]] — Movement 2 there covers the shift of
  governance to the catalog layer, which is the backdrop for §6's catalog federation discussion.
- [[data-platforms-in-2029]] — the forward-looking piece; its immutable/versioned-substrate thread
  is the long-horizon version of §4's layer model.

# Adopting Open Table Formats at Scale

> What actually consolidated in the open table format market, what is newly appearing, and
> how an established enterprise with petabytes of data adopts a format broadly — without
> betting the estate on a single vendor's narrative.

- **Topic:** Data Platform
- **Date:** 2026-08-15
- **Status:** draft

> *The words written here are all AI-generated, but all the content was critically reviewed
> and validated by me — the use of AI is to accelerate the knowledge searching and narrative
> building.*

## Contents

1. [Context](#context)
2. [What consolidated — and what didn't](#1-what-consolidated--and-what-didnt)
3. [Where the action actually moved](#2-where-the-action-actually-moved)
4. [A decision framework that doesn't bet the estate](#3-a-decision-framework-that-doesnt-bet-the-estate)
5. [Migrating petabytes](#4-migrating-petabytes)
6. [Running it: operating model, governance, cost](#5-running-it-operating-model-governance-cost)
7. [A 0–24 month roadmap](#6-a-024-month-roadmap)
8. [Counterpoints: where this study could be wrong](#7-counterpoints-where-this-study-could-be-wrong)
9. [Takeaways](#takeaways)
10. [References](#references)

## Context

Two earlier studies in this folder circled this question without answering it.
**[[data-platforms-in-2029]]** called open table formats "the closest thing to a safe bet"
in the whole forecast, and then explicitly deferred the "what to do about it now" to a
separate planning study. **[[producer-layer-and-contract-gated-democratization]]** mapped
the storage/catalog layer as one movement among several, rating evidence rather than
recommending action. This study is the missing third piece: **which format, which catalog,
and how a large estate actually gets there.**

The scenario it is written against is deliberately unglamorous and, in my experience, the
common one: a **consolidated enterprise with petabytes spread across a heterogeneous
estate** — a legacy Hive-and-Parquet lake nobody fully owns, a Databricks/Delta footprint
that grew from one successful team outward, a cloud warehouse holding the numbers the
business actually trusts, and a streaming tier bolted to the side. Nothing is greenfield.
Everything has a stakeholder. The question is never "which format is best" in the abstract;
it is "what do we standardize on, what do we migrate, in what order, and what do we
deliberately leave alone."

**A note on the evidence, because this topic earns it.** Table formats are a market where
nearly every well-written source has a commercial position. Dremio, Databricks, Snowflake,
AWS, Starburst, Onehouse and the various lakehouse consultancies all publish genuinely
useful technical material *and* all profit from a particular conclusion. The most-cited
adoption statistics are vendor-sponsored. I have leaned on points where independent parties
with *opposing* interests agree, and flagged the rest. **A further caveat specific to this
draft:** the network policy on the machine where this was researched blocked direct fetches
of several primary sources — the Iceberg spec pages, `delta.io`, and the AWS blogs among
them — so claims here were corroborated across multiple independent secondary sources
rather than read off the primary document. Where a number matters to a decision, verify it
against the primary source before you act on it. Specific figures are attributed to whoever
published them, not asserted as consensus.

**Scope.** This is about the *table format and catalog layer* — the thing that turns a pile
of Parquet into transactional tables. It is not about modeling methodology, semantic layers,
or engine selection, except where those decisions constrain this one.

## 1. What consolidated — and what didn't

**1.1 The convergence is real, and it is mostly about reading.** *(Well-evidenced;
multiple independent signals.)*

The strongest claim you can make with confidence is narrow but important: **Apache Iceberg
has become the default interchange format for new open lakehouses.** The evidence is
structural rather than promotional — every major cloud ships a managed Iceberg service,
Snowflake and Databricks both read and write it natively, and the long tail of engines from
DuckDB to Trino to PostgreSQL extensions have converged on reading it
([Alex Merced, *Lakehouse Table Formats in 2026*](https://amdatalakehouse.substack.com/p/lakehouse-table-formats-in-2026-iceberg)).
That is a different and much stronger signal than a vendor survey: competitors who would
prefer to lock you in have concluded they cannot, and are competing above the format instead.

The adoption numbers point the same way, with the usual asterisk. An independent survey of
252 senior data and IT leaders published in January 2026 reported that **58% run
business-critical analytics on Iceberg**, that **95% are using or planning to use it for AI
and ML workloads**, and that nearly four in five planned further migrations during 2026
([survey coverage](https://hostingjournalist.com/news/survey-apache-iceberg-becomes-enterprise-core)).
Treat the precise percentages as directional — surveys of self-selecting data leaders
oversample the engaged — but the *direction* is corroborated by the structural evidence above.

**1.2 "The format wars are over" is half true, and the false half matters.** *(Contested;
this is where most write-ups overreach.)*

The tidy narrative says one format won. The more defensible reading is that **the formats
never solved identical problems, so there was never a single war to win**
([James M, *Iceberg vs Delta vs Hudi in 2026*](https://jamesm.blog/data-engineering/iceberg-vs-delta-vs-hudi-2026/)).
What actually happened is that Iceberg won the *interoperability* role — the neutral format
you expose so that other people's engines can read your data — while the others retained
defensible positions in the niches they were designed for:

| Format | What it actually won | Why it persists |
|---|---|---|
| **Apache Iceberg** | The interchange and multi-engine standard | Vendor-neutral governance; every engine reads it; the REST catalog spec made it a protocol |
| **Delta Lake** | The largest single-vendor ecosystem in data | Deep Databricks integration; enormous installed base; UniForm removes the pressure to convert |
| **Apache Hudi** | Database-grade indexing and upsert-heavy CDC | 1.0 pushed further into indexing; strongest where mutation rate, not scan volume, is the problem |
| **Apache Paimon** | Streaming-native tables | Owns the Flink tier; reaches batch through an Iceberg compatibility mode |
| **DuckLake / Lance** | Deliberate re-designs (see §2.4) | Attack assumptions the others share, rather than competing feature-for-feature |

The practical consequence for a large estate is the opposite of what the consolidation
narrative implies. **If one format had truly won outright, you would migrate everything and
be done. Because the win is partial and role-specific, the correct answer for a
heterogeneous estate is usually a standard plus deliberate exceptions** — not a monoculture.
I develop that into an actual decision rule in §3.

**1.3 Watch what stopped differentiating.** The most useful thing to notice about 2026 is
what vendors *stopped* arguing about. The table format itself no longer differentiates
anyone — which is exactly why the competition moved up a layer, to the catalog. That shift
is the single most important thing in this study, and it is the subject of §2.1.

## 2. Where the action actually moved

**2.1 The catalog is the real battleground now.** *(Well-evidenced; the consensus across
sources with otherwise opposing interests.)*

The Iceberg REST Catalog specification — introduced back in Iceberg 0.14 — did something
subtle and consequential: **it turned the catalog from a library you linked into a protocol
you speak** ([Iceberg REST catalog spec](https://iceberg.apache.org/rest-catalog-spec/)).
Once the catalog is a protocol, it can hold the things that actually matter commercially:
identity, authorization, credential vending, lineage, and the audit trail. The format became
a commodity; the catalog inherited the lock-in.

The contenders, and what genuinely separates them:

| Catalog | Governance model | The honest case for it |
|---|---|---|
| **Apache Polaris** | ASF Top-Level Project since February 2026 | Vendor-neutral by construction; full RBAC, credential vending *and* remote signing; self-hostable or consumed via Snowflake Open Catalog / Dremio |
| **Unity Catalog** | Databricks-led, open-sourced core | If you are a Databricks shop it is effectively mandatory; strongest governance feature surface; deepest platform integration |
| **Apache Gravitino** | ASF TLP since mid-2025 | Federated metadata across heterogeneous systems rather than one lakehouse; AI/model catalog ambitions |
| **Lakekeeper** | Independent, Rust | Deliberately small: single binary, no JVM, no Python. The "boring infrastructure" option |
| **Cloud-native (Glue, S3 Tables IRC)** | Cloud vendor | Lowest operational effort inside one cloud; weakest story across clouds |

Two details matter more than the vendor comparison. First, **the interoperability floor is
rising**: Polaris, Lakekeeper and others have been aligning on the Iceberg 1.11 signer
endpoint properties, so engines configure remote signing the same way everywhere
([*The State of Apache Iceberg Catalogs*, June 2026](https://amdatalakehouse.substack.com/p/the-state-of-apache-iceberg-catalogs)).
Second, **conformance is not uniform** — implementing "the REST spec" covers a range of
completeness, and the gaps are exactly where multi-engine plans break. Unity Catalog is the
instructive case: its Iceberg REST endpoint supports read *and* write for UC-managed Iceberg
tables — write support reached general availability on Azure in April 2026
([Snowflake release notes](https://docs.snowflake.com/en/release-notes/2026/other/2026-04-06-iceberg-write-support-azure-unity-catalog)) —
while Delta tables exposed through Iceberg reads remain **read-only** to external Iceberg
clients ([Databricks docs, *Unity Catalog managed tables*](https://docs.databricks.com/aws/en/tables/managed)).
That distinction is easy to miss in a slide and expensive to discover in an integration test.

**2.2 Iceberg v3 closed the functional gap; engine support is the actual gate.**

The v3 spec adds seven capabilities, of which three change architecture rather than
performance: **deletion vectors** (binary bitmaps replacing positional delete files, with
vendors reporting up to 10x faster DML), **row lineage** (`_row_id` and
`_last_updated_sequence_number` per row, enabling CDC natively rather than through external
tooling), and the **VARIANT type** (a real semi-structured column with shredding and filter
pushdown, retiring the JSON-as-STRING workaround). The rest — default column values,
geometry/geography types, nanosecond timestamps, multi-argument partition transforms — are
welcome and unremarkable ([Dremio, *Iceberg V2 vs V3*](https://www.dremio.com/blog/apache-iceberg-v2-vs-v3-what-changed-and-what-it-means-for-your-tables/);
[Databricks, *Iceberg v3: Moving the Ecosystem Towards Unification*](https://www.databricks.com/blog/apache-icebergtm-v3-moving-ecosystem-towards-unification)).

**Row lineage deserves particular attention in an enterprise context**, because it converts
a class of bespoke plumbing — change capture, incremental model builds, audit trails
reconstructed after the fact — into a table property. That is the kind of change that
quietly removes a team's worth of maintenance work.

The constraint is not the specification. By 2026 v3 was generally available on Snowflake,
on Databricks Runtime 18.0+, and across the AWS analytics stack including EMR, Glue,
SageMaker and S3 Tables ([Atlan, *Apache Iceberg v3*](https://atlan.com/know/snowflake/apache-iceberg-v3/);
[AWS announcement](https://aws.amazon.com/about-aws/whats-new/2025/11/aws-apache-iceberg-v3-deletion-vectors-row-lineage)).
But **the binding constraint is your slowest reader** ([Ryft, *Apache Iceberg V3: Is It Ready?*](https://www.ryft.io/blog/apache-iceberg-v3-is-it-ready)).
In a large estate that slowest reader is usually a pinned engine version inside a system
nobody wants to touch. Upgrading table versions before every consumer can read them is one
of the few genuinely irreversible mistakes available in this domain — see §4.4.

**2.3 The bridges are load-bearing, and that changes the economics of waiting.**

Two mechanisms let a table serve readers of a format it was not written in.
**Delta UniForm** asynchronously generates Iceberg metadata alongside a Delta table, so one
copy of the Parquet files serves both reader ecosystems without a rewrite
([Delta Lake, *Unifying the open table formats*](https://delta.io/blog/unifying-open-table/)).
**Apache XTable** (incubating) translates metadata between Iceberg, Delta and Hudi, with
contributors including Microsoft, Google, Databricks and Snowflake — an unusual coalition
that is itself a signal about where the industry expects this to land.

The strategic consequence is underappreciated: **the bridges make the cost of *not* deciding
fall over time.** For most of software, deferring a platform decision compounds the eventual
cost. Here, the interoperability layer keeps improving while you wait, so a "serve Iceberg
readers from our existing Delta estate" position gets cheaper, not more expensive. That is a
real argument against a big-bang migration, and I take it seriously in §3.

The limits are equally real, and I would not build a program on the bridges alone.
Generated metadata is **asynchronous** — there is a freshness lag that matters for
low-latency consumers. Bridges primarily serve *readers*; concurrent multi-format *writers*
against one table is not a supported model. And a bridge preserves your existing physical
layout, including whatever partitioning and file-size problems it already has. **A bridge
buys time; it does not buy a better table.**

**2.4 The new entrants attack shared assumptions rather than compete on features.**

Three arrivals are interesting precisely because they are not trying to be a better Iceberg:

- **Apache Paimon** (1.0) is streaming-native by design and owns the Flink tier, with
  growing Spark support and an Iceberg compatibility mode to reach batch consumers. If your
  hard problem is continuous ingestion with frequent updates, Paimon is solving *your*
  problem; Iceberg is solving a related one.
- **DuckLake**, from the DuckDB/MotherDuck side, makes the sharpest architectural argument
  in the market: **stop putting metadata in files.** It keeps all table metadata in a
  relational database, which buys real multi-table transactions, straightforward
  consistency, and dramatically faster query planning
  ([MotherDuck, *The Open Lakehouse Stack*](https://motherduck.com/blog/open-lakehouse-stack-duckdb-table-formats/)).
  You do not have to adopt DuckLake to take the critique seriously — the same argument
  visibly surfaces inside Iceberg's own debates about `metadata.json` and adaptive metadata
  structures.
- **Lance** targets ML workloads explicitly: random access performance and built-in vector
  search, which the analytics-shaped formats handle badly.

None of these is a candidate to be an enterprise's *standard* today. All three are
candidates to be a justified exception (§3.3), and DuckLake's critique is the one I would
watch for signs of being absorbed into the mainstream formats.

**2.5 The counter-current: open format, re-closed operations.**

The most commercially significant trend of the past two years runs *against* the openness
narrative, and it deserves naming plainly. Managed table services — **Amazon S3 Tables**,
**Unity Catalog managed tables**, Snowflake-managed Iceberg — take the open format and
re-bundle storage, catalog and automatic maintenance into a single managed product
([AWS, *S3 Tables*](https://aws.amazon.com/s3/features/tables/);
[Databricks](https://www.databricks.com/blog/how-unity-catalog-managed-tables-bring-interoperability-performance-and-unified-governance)).
AWS reports up to 3x query throughput and 10x higher transactions per second versus
self-managed tables, and S3 Tables exposes an Iceberg REST endpoint any compatible engine
can use ([AWS, *S3 Tables IRC APIs*](https://aws.amazon.com/about-aws/whats-new/2025/03/amazon-s3-tables-apache-iceberg-rest-catalog-apis)).

This is a genuinely good trade for many teams — table maintenance is unglamorous work
(§5.1) and outsourcing it is rational. But be clear about what is being traded. **The
format stays open; the operations become proprietary.** You lose direct control of file
layout, compaction scheduling, and storage tiering — which is precisely the control you need
when compaction lag or cost becomes the problem. Onehouse published a critical analysis
reporting compaction delays of 2.5–3 hours and costs 20–30x higher than alternatives on S3
Tables ([Onehouse](https://www.onehouse.ai/blog/s3-managed-tables-unmanaged-costs-the-20x-surprise-with-aws-s3-tables));
Onehouse sells a competing managed service, so read that as an adversarial finding to test
rather than a settled fact — but **test it, on your workload, before you commit an estate to
it.** The reason to test is structural: with self-managed Iceberg you keep the buckets, the
file layout and the IAM, which is what matters when you have existing data, storage-tiering
rules, or compliance constraints that require owning the bucket.

## 3. A decision framework that doesn't bet the estate

**3.1 The central move: separate three decisions that are usually made as one.**

Most format debates go badly because "should we adopt Iceberg?" bundles three decisions with
radically different reversibility. Separate them and the strategy becomes much clearer:

| Decision | What it governs | Cost to reverse | Recommended posture |
|---|---|---|---|
| **Table format** | Physical metadata layout of tables | **Low.** Bridges (§2.3) and in-place conversion (§4.1) mean no data rewrite is required in most cases | Standardize, but hold it loosely. This is the *least* consequential of the three |
| **Catalog + governance model** | Identity, RBAC, credential vending, lineage, audit, the namespace everyone codes against | **High.** Every pipeline, grant, integration and access policy binds to it | **Decide this deliberately and first.** This is where the lock-in actually lives |
| **Compute engine(s)** | Who reads and writes | **Medium.** Bounded by workload; the open format is what keeps it medium rather than high | Keep plural on purpose; the format's job is to preserve this optionality |

**The recommendation that follows is the core of this study: choose the catalog
deliberately, and let the table format follow from it.** The industry spent two years
arguing about the layer that turned out to be cheap to change, while the expensive layer
was being decided by default — usually by whichever platform a successful team adopted first.
Sources with quite different commercial positions now converge on this framing
([Dremio, *Catalog Wars*](https://www.dremio.com/newsroom/lakehouses-ai-and-the-catalog-wars-four-key-trends-to-watch/);
[*Choosing the Right Iceberg Control Plane*](https://datalakehousehub.com/blog/2026-05-choosing-iceberg-control-plane/)),
which is roughly as close to independent corroboration as this market offers.

**3.2 A defensible default for a heterogeneous enterprise estate.**

Stated plainly, so it can be argued with:

- **Standard format: Iceberg**, for anything that must be read by more than one engine or
  outlive its current platform. Not because it is technically superior in every dimension —
  it is not — but because it maximizes the number of doors that stay open, which is the
  right optimization target for an estate that will outlive current vendor relationships.
- **Standard table version: v2 today, with a governed path to v3.** Adopt v3 per-workload
  once you have verified every consumer of that table can read it (§4.4), starting with
  workloads where deletion vectors or row lineage remove real work.
- **Catalog: pick one control plane and make it the enterprise namespace.** Where the
  estate is genuinely multi-vendor and expected to stay that way, a vendor-neutral,
  self-hostable catalog such as Polaris is the lowest-regret choice. Where Databricks is
  already the centre of gravity, fighting Unity Catalog costs more than it returns —
  standardize on it and use its Iceberg REST endpoint as the interoperability seam, with
  the read/write asymmetry of §2.1 explicitly designed around.
- **Federate before you consolidate.** Catalog federation lets one control plane surface
  tables that still live elsewhere. It buys a single governed namespace long before physical
  migration completes — which is what actually delivers value to users.

**3.3 Multi-format is a legitimate end state, if the exceptions are governed.**

The monoculture instinct is strong in platform teams and mostly wrong here. A defensible
policy is **one standard plus named, time-bound, reviewed exceptions** — for instance,
Paimon where a streaming ingestion tier genuinely needs it, or a specialized format for a
vector/ML workload. What makes this work is not the exception itself but the discipline:
every exception has a named owner, a stated reason, an expiry date, and a documented path
back to the standard. What makes it fail is exceptions granted informally and never revisited,
which is how you arrive at the heterogeneous estate you are currently trying to fix.

**3.4 Migrate on a forcing function, not on a calendar.**

The single most useful piece of guidance I found, and the one most at odds with how these
programs are usually run: **because the bridges keep improving (§2.3), migrate a workload
when a concrete forcing function arrives** — a multi-engine requirement the bridges cannot
serve, a governance consolidation, a platform change, a cost or performance problem you can
measure — **and not because the workload appears on a migration inventory.** A migration
program justified by "we should be on Iceberg" will be deprioritized the first time
something urgent happens, and will leave the estate half-migrated, which is strictly worse
than either end state.

## 4. Migrating petabytes

**4.1 Four mechanics, and the economics that separate them.**

| Mechanic | What happens to data files | Best for | Main limitation |
|---|---|---|---|
| **In-place metadata** (`migrate`) | Not moved or rewritten; Iceberg metadata written over existing files | Large Hive/Parquet tables where layout is already acceptable | Inherits every existing layout problem; source formats must be self-describing |
| **Shadow copy** (`snapshot`) | Not moved; a temporary Iceberg table references the originals | **Rehearsal and validation** before committing | Not a destination; a testing instrument |
| **Full rewrite** (`CTAS` / `INSERT…SELECT`) | Fully rewritten | Tables needing new partitioning, sorting, or file sizing | Full storage and compute cost; the expensive option |
| **Bridge in place** (UniForm / XTable) | Untouched; alternate metadata generated | Serving Iceberg readers from a Delta estate without migrating | Async freshness lag; readers not writers (§2.3) |

The mechanics deserve precision, because they are frequently conflated. **`migrate`** creates
an Iceberg table with the source table's identifier and metadata, **renames the source table
as a backup so failure is recoverable**, commits all data files across partitions, and drops
the source. **`snapshot`** creates a lightweight independent copy that references the original
data files while leaving the source table untouched and writable — which makes it the correct
tool for a rehearsal. **`add_files`** imports files from specific partitions into an existing
table without creating a new one, which makes it the tool for incremental backfill
([Iceberg table migration docs](https://iceberg.apache.org/docs/latest/table-migration/);
[Dremio, *How to Migrate a Hive Table*](https://www.dremio.com/blog/how-to-migrate-a-hive-table-to-an-iceberg-table/)).

In-place migration works by reading only the Parquet/ORC/Avro footers rather than the data
itself, which is why it is cheap at petabyte scale. **It is also why it only works for
self-describing formats** — CSV and JSON carry no consistent embedded schema and must be
rewritten ([AWS Prescriptive Guidance, *In-place migration*](https://docs.aws.amazon.com/prescriptive-guidance/latest/apache-iceberg-on-aws/table-migration-inplace.html)).

**The trap in the cheap option:** in-place migration converts your metadata, not your
problems. A table with five million small files and a bad partition spec becomes an Iceberg
table with five million small files and a bad partition spec — and Iceberg will make that
*more* visible, because manifest overhead now scales with your file count too (§4.4).
**Decide per table whether you are migrating or remediating**, and budget the rewrite where
the layout is the actual problem. On a mixed estate, expect the split to be roughly:
in-place for the large, well-laid-out tables that dominate volume; rewrite for the smaller
number of badly-laid-out tables that dominate pain.

**4.2 Sequence by forcing function and blast radius, not by size.**

The default instinct — sort tables by volume, start at the top — is wrong twice over. It
front-loads the highest-risk work before the team has learned anything, and it optimizes a
metric (terabytes migrated) that no stakeholder values.

A sequencing that holds up better:

1. **Wave 0 — instrument and inventory.** Before anything moves: table count, file count per
   table, file size distribution, partition specs, write patterns and concurrency, current
   cost per table, and *every consumer of every table* including the ones nobody remembers.
   The consumer inventory is the part that gets skipped and the part that causes the
   incidents. **File count matters more than volume** and is the number most estates cannot
   produce on demand (§4.4).
2. **Wave 1 — a thin vertical slice.** One non-critical but *real* domain, taken end to end
   through the whole path: catalog registration, migration, validation, cutover, maintenance,
   monitoring, decommission. The goal is a rehearsed runbook, not migrated volume.
3. **Wave 2 — forcing-function workloads.** Everything with a concrete trigger from §3.4.
   These have sponsors, which means they have budget and attention.
4. **Wave 3 — the long tail, bridged not migrated.** Point the bridges at whatever remains
   and let it sit there indefinitely if nothing forces the issue. **A permanently bridged
   long tail is an acceptable end state**, and pretending otherwise is what strands programs
   at 60%.

Order within a wave by blast radius ascending, not size descending: fewest consumers first,
so mistakes are cheap while the runbook is still wrong.

**4.3 Validation and cutover: assume you will need to go back.**

Dual-running is not optional at this scale, and the discipline is well-established
([Ryft, *Migrating from Hive to Apache Iceberg*](https://www.ryft.io/blog/migrating-from-hive-to-apache-iceberg);
[*From Delta Lake to Apache Iceberg: A Migration Blueprint*](https://blog.dataengineerthings.org/from-delta-lake-to-apache-iceberg-a-complete-migration-blueprint-for-modern-data-platforms-400ce1e996f5)):

- **Reconcile before cutover** — row counts, aggregate checksums on numeric columns, and
  spot-checked partition-level comparisons. Schema-only validation catches almost nothing.
- **Shadow-read** the new table from real consumer queries and diff the results while the old
  path still serves production.
- **Expect stragglers.** Concurrent writers to the source table during migration routinely
  leave files behind — this is normal, not a defect, and `add_files` exists to sweep them up.
  Plan a reconciliation pass rather than treating the first migration run as complete.
- **Keep the rollback real.** `migrate`'s renamed backup table is only a rollback if you have
  written down how to use it and have not yet expired the snapshots that make it meaningful.
- **Re-registering a table in a new catalog does not require rewriting data files** — but it
  does require that no active transactions are running. Catalog moves are quick and quietly
  dangerous; schedule them like cutovers, not like config changes.

**4.4 What actually breaks at petabyte scale.**

This is the section I would read first if I were running the program, because these failures
are silent, cumulative, and mostly absent from migration plans.

**Small files are the dominant cost driver, and the metric is file count, not volume.**
This is the single most common structural failure in production Iceberg estates, and it
compounds invisibly until latency doubles and the storage bill spikes. The mechanics are
arithmetic: a table with 500,000 small files queried 50 times a day generates roughly 25
million GET requests per month; compacted to 2,000 files, the same data generates about
100,000 ([LakeOps, *Fixing Small Files in Apache Iceberg*](https://lakeops.dev/blog/iceberg-small-files-guide)).
Streaming makes it worse mechanically — a table fed by 10-minute Flink checkpoints across
100 partitions produces around 14,400 files a day, most of them a few megabytes. And the
costs cascade: small files inflate query compute through API overhead, inflate *compaction*
compute because there are more footers to read, and accelerate snapshot accumulation because
each frequent write creates its own snapshot.

**Metadata bloat follows file count.** Every data file gets a manifest entry carrying
partition values, column-level statistics, size and record count. More files means larger
manifests, more of them, and slower planning — which is how a format designed to make
planning fast ends up making it slow.

**Orphan files and pinned snapshots are pure waste.** Published cost modelling puts 100 TB
of logical data across 5,000,000 uncompacted files at roughly $2,300/month in storage, plus
around 20 TB of orphan files and 15 TB of snapshot-pinned dead data
([LakeOps, *Iceberg Cost Optimization in 2026*](https://lakeops.dev/blog/iceberg-cost-optimization-2026)).
Treat the absolute figures as illustrative of the *shape* of the problem — roughly a third
of the footprint being dead weight — rather than as a benchmark.

**Optimistic concurrency degrades exactly where enterprises operate.** Iceberg's OCC assumes
conflicts are rare, which holds when commits are infrequent and large. It degrades when
commits are frequent and small — which is precisely what CDC pipelines, streaming writers and
automated jobs produce. At scale this stops being a curiosity: long-running compaction jobs
fail after hours of compute, and CDC pipelines spend a meaningful share of their time
retrying ([Ryft, *Handling Commit Conflicts in Apache Iceberg*](https://www.ryft.io/blog/handling-commit-conflicts-in-apache-iceberg);
[AWS, *Manage concurrent write conflicts*](https://aws.amazon.com/blogs/big-data/manage-concurrent-write-conflicts-in-apache-iceberg-on-the-aws-glue-data-catalog)).
**The essential diagnostic distinction: catalog commit conflicts are fixable by tuning retry
properties; validation conflicts are not.** No configuration resolves a validation conflict —
you must change what the writers touch. Teams that tune before diagnosing burn weeks.

**Schema ownership must be singular.** Concurrent schema changes from multiple engines
conflict, and the working pattern is to designate **one engine as schema owner** for DDL,
route schema changes through CI/CD with review gates, and treat them as deployments rather
than ad-hoc operations ([LakeOps, *Schema Evolution in Production*](https://lakeops.dev/blog/iceberg-schema-evolution-production)).
In a federated organization this is an organizational decision wearing a technical costume,
and it is worth settling before the first wave rather than after the first outage.

**Table version upgrades are a one-way door.** Per §2.2: verify every consumer, including
the forgotten ones from Wave 0, before upgrading a table to v3. This is the one item on this
list with no cheap remediation.

## 5. Running it: operating model, governance, cost

**5.1 Table maintenance is a platform service, not each team's homework.**

Iceberg tables degrade silently — files fragment, snapshots accumulate, metadata grows, and
query latency creeps up with no alert firing. The required maintenance is well understood:
compaction, snapshot expiry, orphan file cleanup, manifest rewriting.

The failure mode is organizational rather than technical. **Delegating maintenance to each
data-producing team guarantees it will be done inconsistently and abandoned under delivery
pressure**, because it is invisible work that competes with visible work. The pattern that
holds up is to run maintenance centrally as a platform service with explicit SLOs — target
file size, maximum snapshot age, compaction lag, orphan cleanup cadence — applied by policy
per table class, with per-table overrides by exception. Producing teams should be able to
*see* the state of their tables and *ignore* the mechanics.

This is also the honest argument for the managed services of §2.5: they sell you exactly this
function. The decision is not "managed or self-managed" in the abstract, but **whether you
can run this function to a better standard than the service, at the scale you operate.**
For most organizations at a few hundred tables, the answer is no. At petabyte scale with
tiering rules and cost pressure, it is often yes — and the control you retain over file
layout and scheduling is the reason.

**5.2 File count is the leading indicator of cost.**

If you take one operational metric from this study: **track file count per table and file
size distribution, and alert on them.** They lead cost and latency, they are cheap to
measure, and almost nobody instruments them until after the first bill shock. Storage volume
— the number every FinOps dashboard already shows — is a lagging and largely uninformative
indicator by comparison. A dashboard showing terabytes will look calm while the estate is
degrading.

Useful companions: dead-weight ratio (orphan plus snapshot-pinned bytes over logical bytes),
compaction lag, and GET requests per query — the last being what actually converts
fragmentation into money.

**5.3 Governance binds to the catalog, which is why §3.1 ordered the decisions that way.**

The REST catalog spec covers namespace and table management, metadata loading, snapshot
commits, **and storage credential vending** — and that last item is the governance seam.
Credential vending issues temporary, table-scoped credentials on demand, which removes
long-lived secrets and moves access decisions into the catalog's policy engine
([Dremio, *Credential Vending with Iceberg REST Catalogs*](https://www.dremio.com/blog/iceberg-credential-vending/)).
Polaris implements RBAC over catalogs, namespaces, tables and views alongside both credential
vending and remote signing.

The architectural consequence worth internalizing: **the catalog becomes your authorization
boundary for data.** Storage-level IAM remains as a backstop, but the fine-grained,
auditable, engine-independent policy lives at the catalog. That is a substantially better
place for it than per-engine grants replicated across four systems and drifting — and it is
the strongest argument for treating the catalog choice as the serious one.

**5.4 The standards a central team must own.**

Small list, high leverage. Get these written down before Wave 1, not after Wave 3:

- **Naming and namespace conventions** — the thing everyone codes against and nobody can
  change later.
- **Partitioning and sorting guidance per table class**, with defaults that are correct
  often enough that teams accept them.
- **Who may execute DDL**, per §4.4. One schema owner per table, enforced.
- **Table version policy** and the process for granting v3 upgrades.
- **The exception register** from §3.3 — owner, reason, expiry, path back.
- **Maintenance SLOs per table class** from §5.1.

## 6. A 0–24 month roadmap

Phase durations assume a large enterprise with existing platform capability; the sequencing
matters more than the timings, and **exit criteria matter more than dates.**

| Phase | Months | Focus | Exit criteria | What *not* to do |
|---|---|---|---|---|
| **0 — Baseline** | 0–3 | Inventory (tables, file counts, size distributions, consumers, cost); target-state decision on catalog per §3.1 | File-count instrumentation live; consumer map complete; catalog decided and written down with its reasoning | Don't migrate anything. Don't let a pilot pick the catalog by default |
| **1 — Foundation** | 3–9 | Stand up the catalog as enterprise namespace; federate existing catalogs; build the maintenance service (§5.1); publish the standards (§5.4); run Wave 1 as a rehearsal | One governed namespace over federated sources; maintenance service running with SLOs; one domain fully migrated and stable; runbook proven | Don't start parallel migration waves. Don't defer the maintenance service until "after migration" |
| **2 — Waves** | 9–18 | Forcing-function workloads (§3.4); bridges for everything else; v3 adoption where it removes real work | Triggered workloads migrated and validated; bridged long tail governed and monitored; no half-migrated domains | Don't chase migration percentage as a KPI. Don't grant v3 upgrades without consumer verification |
| **3 — Optimize** | 18–24 | Decommission legacy paths; remediate layout on tables that need it; review exception register; tune cost | Legacy catalogs retired or explicitly permanent; dead-weight ratio under target; every exception re-justified or expired | Don't declare victory while dual-running paths remain — that's carrying both costs |

**Two structural notes.** The maintenance service in Phase 1 is deliberately built *before*
the migration waves. Building it afterwards means the tables migrated first spend months
degrading, and the team learns the wrong lesson about the format. And Phase 2's success
criterion is deliberately not "percentage migrated" — it is "no domain is half-migrated,"
because a half-migrated domain pays both sets of costs and delivers neither set of benefits.

## 7. Counterpoints: where this study could be wrong

Applying the same treatment [[data-platforms-in-2029]] applies to itself:

- **The bridges may make migration permanently unnecessary.** If UniForm and XTable keep
  improving, the honest answer for a large Delta estate might be "bridge everything, migrate
  nothing, ever." I have argued for a standard plus governed exceptions; a defensible
  alternative is *no* format standard at all, just a catalog standard and a bridging policy.
  I think §4.4's point stands — bridges don't fix physical layout — but that is an argument
  about table health, not about format choice, and it could be addressed separately.
- **DuckLake's critique may be the one that ages well.** If metadata-in-files is genuinely
  the wrong design, today's consensus is a local optimum and the mainstream formats will
  absorb the change — visible already in Iceberg's adaptive-metadata discussions. That would
  not invalidate adopting Iceberg now, but it means the "settled" layer is less settled than
  §1 suggests.
- **Managed services may re-create the lock-in the format was meant to remove**, and this
  study may under-weight how fast that is happening. "Open format, proprietary operations"
  (§2.5) is a coherent commercial strategy, and an estate deep in managed tables has a
  portability story that is theoretically sound and practically untested.
- **The scale premise may be softer than it looks.** The industry has a documented history
  of building distributed systems for data that fits on one machine. If single-node engines
  keep improving, some of the petabyte-scale apparatus recommended here is over-engineering
  for a workload that a large machine could serve — and the mistake would not be visible
  from inside the program.
- **The adoption evidence is weaker than its confident presentation.** The 58%/95% figures
  come from a sponsored survey of self-selecting leaders (§1.1). I lean on the structural
  signal — competitors interoperating against their own interest — precisely because it does
  not depend on those numbers. If you find yourself citing the percentages in a business
  case, cite the structural argument instead; it is the more durable one.
- **And a limitation of this draft specifically:** several primary sources could not be
  fetched directly during research (see Context), so some claims rest on secondary
  corroboration. The architectural arguments do not depend on any single figure, but the
  figures themselves deserve a primary-source check before they enter a decision document.

## Takeaways

- **The format question is largely settled and was never the important one.** Iceberg is the
  default for interchange, and the strongest evidence is structural — competitors
  interoperating against their own commercial interest — not the vendor-sponsored adoption
  surveys. But "the format wars are over" overstates it: Delta, Hudi and Paimon retained
  real niches, so the right end state for a mixed estate is a standard plus governed
  exceptions, not a monoculture.
- **Choose the catalog deliberately; let the format follow.** Format, catalog and engine are
  three separable decisions with very different costs to reverse. Format is cheap to reverse
  — bridges and in-place conversion mean no data rewrite. **The catalog is where identity,
  authorization, credential vending and audit bind, and that is the expensive one.** Most
  organizations argued about the cheap decision while the expensive one was made by default.
- **Migrate on a forcing function, not a calendar.** Because the interoperability bridges
  keep improving, the cost of waiting *falls* — inverting the usual platform logic. Migrate
  when something concrete demands it; bridge the rest, possibly forever. A permanently
  bridged long tail is a legitimate end state; a half-migrated domain is not.
- **In-place migration converts your metadata, not your problems.** Reading Parquet footers
  makes it cheap at petabyte scale, but a badly laid-out table becomes a badly laid-out
  Iceberg table — and Iceberg amplifies the symptom, because manifest overhead now scales
  with file count too. Decide per table whether you are migrating or remediating.
- **File count, not data volume, is the metric that predicts cost and latency.** It is the
  most common silent failure in production estates, it leads every cost curve, and almost
  nobody instruments it before the first bill shock. Track file count and size distribution
  per table from day one; the terabytes number on your FinOps dashboard will look calm while
  the estate degrades.
- **Table maintenance is a central platform service with SLOs, or it doesn't happen.**
  Compaction, snapshot expiry and orphan cleanup are invisible work that loses to visible
  work every time it is delegated to producing teams. Build the service *before* the
  migration waves — and recognize that this exact function is what the managed table
  services are selling, which makes "can we run this better than they can?" the real
  build-versus-buy question, not "open versus proprietary."

## References

*Links collected August 2026. Vendor materials are cited for design patterns and market
signals, not as endorsements — in this market nearly every well-written source has a
commercial position, noted below where it bears on the claim. **Verification caveat:**
network policy during research blocked direct fetches of several primary sources
(`iceberg.apache.org`, `delta.io`, `aws.amazon.com`, `onehouse.ai`); those entries were
corroborated across independent secondary sources rather than read from the primary
document, and are marked accordingly.*

### Format landscape and convergence

- **Lakehouse Table Formats in 2026: Iceberg, Delta Lake, Hudi, Paimon, and DuckLake — Alex Merced** ([amdatalakehouse.substack.com](https://amdatalakehouse.substack.com/p/lakehouse-table-formats-in-2026-iceberg))
  — The most complete single survey of the five formats and their trajectories; source for
  the "converged on Iceberg for interchange, but formats never solved identical problems"
  reading. *Supports:* §1.1, §1.2, §2.4. *Caveat:* author is a Dremio developer advocate;
  Dremio's commercial interest favours open formats and neutral catalogs.
- **Iceberg vs Delta vs Hudi in 2026: The Format Wars Are Over — jamesm.blog** ([jamesm.blog](https://jamesm.blog/data-engineering/iceberg-vs-delta-vs-hudi-2026/))
  — Argues the strong consolidation thesis; useful precisely as the position §1.2 pushes
  back on. *Supports:* §1.1, §1.2. *Caveat:* independent blog; the title overstates its own
  contents.
- **The Ultimate Guide to Open Table Formats — Dremio** ([developer.dremio.com](https://developer.dremio.com/the-ultimate-guide-to-open-table-formats-iceberg-delta-lake-hudi-paimon-and-ducklake/))
  — Reference-grade comparison of format internals. *Supports:* §1.2. *Caveat:* vendor.
- **The Open Lakehouse Stack: DuckDB and the Rise of Table Formats — MotherDuck** ([motherduck.com](https://motherduck.com/blog/open-lakehouse-stack-duckdb-table-formats/))
  — The metadata-in-a-database argument behind DuckLake. *Supports:* §2.4, §7.
  *Caveat:* MotherDuck commercializes DuckDB; this is their thesis, cited as a critique
  worth taking seriously rather than as a verdict.
- **Survey: Apache Iceberg Becomes Enterprise Core** ([hostingjournalist.com](https://hostingjournalist.com/news/survey-apache-iceberg-becomes-enterprise-core))
  — The January 2026 survey of 252 senior data/IT leaders: 58% business-critical, 95%
  using or planning Iceberg for AI/ML. *Supports:* §1.1. *Caveat:* **sponsored survey of
  self-selecting respondents** — treat as directional, and prefer the structural argument
  (§7).
- **The 2025 State of the Apache Iceberg Ecosystem** ([datalakehousehub.com](https://datalakehousehub.com/blog/2026-02-state-of-the-apache-iceberg-ecosystem/))
  — Ecosystem-wide survey results. *Supports:* §1.1.

### The catalog layer

- **The State of Apache Iceberg Catalogs in June 2026** ([amdatalakehouse.substack.com](https://amdatalakehouse.substack.com/p/the-state-of-apache-iceberg-catalogs))
  — Comparison of Polaris, Unity, Gravitino, Lakekeeper and Nessie, plus the Iceberg 1.11
  signer-endpoint alignment. *Supports:* §2.1. *Caveat:* Dremio-affiliated author.
- **The State of Apache Polaris in July 2026** ([amdatalakehouse.substack.com](https://amdatalakehouse.substack.com/p/the-state-of-apache-polaris-in-july))
  — Polaris ASF Top-Level Project status (February 2026) and its positioning as a governance
  layer. *Supports:* §2.1, §3.2, §5.3. *Caveat:* Dremio ships Polaris in its product.
- **Lakehouses, AI and the Catalog Wars — Dremio** ([dremio.com](https://www.dremio.com/newsroom/lakehouses-ai-and-the-catalog-wars-four-key-trends-to-watch/))
  — Frames the shift of competition from format to catalog. *Supports:* §1.3, §2.1, §3.1.
  *Caveat:* vendor newsroom.
- **Choosing the Right Iceberg Control Plane: Polaris vs. Unity Catalog vs. Cloud REST** ([datalakehousehub.com](https://datalakehousehub.com/blog/2026-05-choosing-iceberg-control-plane/))
  — Decision-oriented catalog comparison; corroborates the "catalog is the consequential
  decision" framing from a different commercial position. *Supports:* §3.1, §3.2.
- **Apache Iceberg REST Catalog Specification** ([iceberg.apache.org](https://iceberg.apache.org/rest-catalog-spec/))
  — Primary specification: namespace/table management, metadata loading, snapshot commits,
  credential vending. *Supports:* §2.1, §5.3. *Caveat:* **could not be fetched directly**
  during research; described via secondary sources.
- **Unity Catalog managed tables for Delta Lake and Apache Iceberg — Databricks docs** ([docs.databricks.com](https://docs.databricks.com/aws/en/tables/managed))
  — The read/write asymmetry: IRC read+write+create for UC-managed Iceberg tables,
  read-only for Delta tables with Iceberg reads enabled. *Supports:* §2.1, §3.2.
  *Caveat:* vendor documentation, but authoritative for its own product surface.
- **Iceberg write support for Databricks Unity Catalog on Azure (GA) — Snowflake release notes** ([docs.snowflake.com](https://docs.snowflake.com/en/release-notes/2026/other/2026-04-06-iceberg-write-support-azure-unity-catalog))
  — Dates the Azure write-support GA to April 2026. *Supports:* §2.1.
- **Credential Vending with Iceberg REST Catalogs — Dremio** ([dremio.com](https://www.dremio.com/blog/iceberg-credential-vending/))
  — Temporary, table-scoped credentials as the governance mechanism. *Supports:* §5.3.
  *Caveat:* vendor.
- **Catalog federation for Apache Iceberg tables in the AWS Glue Data Catalog — AWS** ([aws.amazon.com](https://aws.amazon.com/blogs/big-data/introducing-catalog-federation-for-apache-iceberg-tables-in-the-aws-glue-data-catalog/))
  — Federation as the "one namespace before physical migration" mechanism. *Supports:*
  §3.2. *Caveat:* vendor; **not fetched directly.**

### Iceberg v3 and interoperability

- **Apache Iceberg V2 vs V3: What Changed — Dremio** ([dremio.com](https://www.dremio.com/blog/apache-iceberg-v2-vs-v3-what-changed-and-what-it-means-for-your-tables/))
  — Feature-by-feature account of deletion vectors, row lineage, VARIANT and the rest.
  *Supports:* §2.2. *Caveat:* vendor.
- **Apache Iceberg™ v3: Moving the Ecosystem Towards Unification — Databricks** ([databricks.com](https://www.databricks.com/blog/apache-icebergtm-v3-moving-ecosystem-towards-unification))
  — Notable as much for *who* published it as for its contents: the Delta vendor arguing
  for Iceberg unification is part of the structural evidence in §1.1. *Supports:* §1.1, §2.2.
  *Caveat:* vendor.
- **Apache Iceberg v3: New Features and Snowflake 2026 Guide — Atlan** ([atlan.com](https://atlan.com/know/snowflake/apache-iceberg-v3/))
  — v3 GA timing across Snowflake, Databricks Runtime 18.0+ and the AWS stack.
  *Supports:* §2.2.
- **Apache Iceberg V3: Is It Ready? — Ryft** ([ryft.io](https://www.ryft.io/blog/apache-iceberg-v3-is-it-ready))
  — Makes the key point that engine readiness, not spec maturity, is the adoption gate.
  *Supports:* §2.2, §4.4. *Caveat:* vendor.
- **AWS support for Iceberg V3 deletion vectors and row lineage** ([aws.amazon.com](https://aws.amazon.com/about-aws/whats-new/2025/11/aws-apache-iceberg-v3-deletion-vectors-row-lineage))
  — Dates v3 feature availability across EMR, Glue, SageMaker and S3 Tables.
  *Supports:* §2.2. *Caveat:* **not fetched directly.**
- **Unifying the open table formats with Delta UniForm and Apache XTable — Delta Lake** ([delta.io](https://delta.io/blog/unifying-open-table/))
  — Primary description of both bridging mechanisms. *Supports:* §2.3. *Caveat:*
  Delta-project source describing its own bridge; **could not be fetched directly** —
  the asynchronous-generation and reader-oriented limitations in §2.3 come from secondary
  corroboration and should be re-checked against current documentation.

### Migration mechanics

- **Table Migration — Apache Iceberg documentation** ([iceberg.apache.org](https://iceberg.apache.org/docs/latest/table-migration/))
  — Canonical reference for `migrate`, `snapshot` and `add_files`. *Supports:* §4.1.
  *Caveat:* **not fetched directly.**
- **In-place migration — AWS Prescriptive Guidance** ([docs.aws.amazon.com](https://docs.aws.amazon.com/prescriptive-guidance/latest/apache-iceberg-on-aws/table-migration-inplace.html))
  — Why in-place works by reading footers, and why it is limited to self-describing formats.
  *Supports:* §4.1. *Caveat:* vendor guidance, AWS-specific.
- **Enterprise-scale in-place migration to Apache Iceberg — AWS Big Data Blog** ([aws.amazon.com](https://aws.amazon.com/blogs/big-data/enterprise-scale-in-place-migration-to-apache-iceberg-implementation-guide/))
  — Repeatable, fault-tolerant migration at enterprise scale. *Supports:* §4.1, §4.2.
  *Caveat:* vendor; **not fetched directly.**
- **How to Migrate a Hive Table to an Iceberg Table — Dremio** ([dremio.com](https://www.dremio.com/blog/how-to-migrate-a-hive-table-to-an-iceberg-table/))
  — Clearest account of the procedural differences, including `migrate`'s backup-rename.
  *Supports:* §4.1, §4.3. *Caveat:* vendor.
- **Migrating from Hive to Apache Iceberg — Ryft** ([ryft.io](https://www.ryft.io/blog/migrating-from-hive-to-apache-iceberg))
  — Validation and cutover discipline, including straggler files from concurrent writers.
  *Supports:* §4.3. *Caveat:* vendor.
- **From Delta Lake to Apache Iceberg: A Complete Migration Blueprint** ([blog.dataengineerthings.org](https://blog.dataengineerthings.org/from-delta-lake-to-apache-iceberg-a-complete-migration-blueprint-for-modern-data-platforms-400ce1e996f5))
  — The "combine mechanics rather than pick one, and keep it reversible" framing that §4.1
  and §4.3 build on. *Supports:* §4.1, §4.3.
- **How Cloudinary transformed their petabyte-scale streaming data lake with Iceberg — AWS** ([aws.amazon.com](https://aws.amazon.com/blogs/big-data/how-cloudinary-transformed-their-petabyte-scale-streaming-data-lake-with-apache-iceberg-and-aws-analytics/))
  — One of the few published petabyte-scale accounts. *Supports:* §4.2. *Caveat:* vendor
  case study — selection bias toward successes; **not fetched directly.**

### Operations, concurrency and cost

- **Fixing Small Files in Apache Iceberg — LakeOps** ([lakeops.dev](https://lakeops.dev/blog/iceberg-small-files-guide))
  — Source of the file-count-over-volume argument and the GET-request arithmetic.
  *Supports:* §4.4, §5.2. *Caveat:* LakeOps sells Iceberg optimization — the problem
  described is real and independently corroborated, but the framing is theirs.
- **Apache Iceberg Cost Optimization in 2026 — LakeOps** ([lakeops.dev](https://lakeops.dev/blog/iceberg-cost-optimization-2026))
  — The dead-weight cost model for orphan files and snapshot-pinned data. *Supports:*
  §4.4, §5.2. *Caveat:* vendor; figures cited as illustrative of shape, not benchmarks.
- **Apache Iceberg Schema Evolution in Production — LakeOps** ([lakeops.dev](https://lakeops.dev/blog/iceberg-schema-evolution-production))
  — The single-schema-owner pattern and DDL-through-CI/CD. *Supports:* §4.4, §5.4.
  *Caveat:* vendor.
- **Handling Commit Conflicts in Apache Iceberg — Ryft** ([ryft.io](https://www.ryft.io/blog/handling-commit-conflicts-in-apache-iceberg))
  — The catalog-conflict versus validation-conflict distinction, which is the most
  operationally useful item in §4.4. *Supports:* §4.4. *Caveat:* vendor.
- **Manage concurrent write conflicts in Apache Iceberg on the AWS Glue Data Catalog — AWS** ([aws.amazon.com](https://aws.amazon.com/blogs/big-data/manage-concurrent-write-conflicts-in-apache-iceberg-on-the-aws-glue-data-catalog))
  — OCC behaviour under many writers. *Supports:* §4.4. *Caveat:* vendor; **not fetched
  directly.**
- **Surviving Commit Conflicts When Dozens of Writers Hit the Same Iceberg Table** ([datalakehousehub.com](https://datalakehousehub.com/blog/iceberg-concurrent-commits-agents/))
  — Why OCC degrades with frequent small commits — the automated-writer pattern.
  *Supports:* §4.4.
- **Don't let Apache Iceberg sink your analytics: practical limitations — Quesma** ([quesma.com](https://quesma.com/blog/apache-iceberg-practical-limitations-2025/))
  — A deliberately critical counterweight to the adoption material. *Supports:* §4.4, §7.

### Managed services and the re-bundling counter-current

- **Amazon S3 Tables — AWS** ([aws.amazon.com](https://aws.amazon.com/s3/features/tables/))
  — Managed storage, catalog and maintenance in one service; the 3x throughput / 10x TPS
  claims. The accompanying [Iceberg REST Catalog APIs announcement](https://aws.amazon.com/about-aws/whats-new/2025/03/amazon-s3-tables-apache-iceberg-rest-catalog-apis)
  is what makes the service reachable from non-AWS engines, and is the reason §2.5 treats
  the openness as real at the format layer even where operations are closed.
  *Supports:* §2.5. *Caveat:* vendor performance claims, unaudited; **not fetched
  directly.**
- **S3 Managed Tables, Unmanaged Costs: The 20x Surprise — Onehouse** ([onehouse.ai](https://www.onehouse.ai/blog/s3-managed-tables-unmanaged-costs-the-20x-surprise-with-aws-s3-tables))
  — Reports 2.5–3 hour compaction delays and 20–30x cost outcomes. *Supports:* §2.5.
  *Caveat:* **Onehouse sells a directly competing managed service** — treat as an
  adversarial hypothesis to test on your own workload, not as a finding; **not fetched
  directly.**
- **How Unity Catalog managed tables bring interoperability, performance and unified governance — Databricks** ([databricks.com](https://www.databricks.com/blog/how-unity-catalog-managed-tables-bring-interoperability-performance-and-unified-governance))
  — The managed-table position from the other major vendor. *Supports:* §2.5.
  *Caveat:* vendor.
- **S3 Tables vs Self-Managed Iceberg on AWS** ([medium.com](https://medium.com/aws-tip/s3-tables-vs-iceberg-on-aws-which-wins-d73b6c316e94))
  — The control-retention argument for self-managed: buckets, file layout, IAM, tiering.
  *Supports:* §2.5, §5.1.

### Adoption programs and operating model

- **A Comprehensive Cloud Data Lakehouse Adoption Strategy for Scalable Enterprise Analytics — IJERET** ([ijeret.org](https://ijeret.org/index.php/ijeret/article/view/383))
  — Academic treatment of phased adoption (foundation / expansion / optimization) across
  business alignment, platform engineering, and governance. *Supports:* §5, §6.
  *Caveat:* low-profile journal; used for structural framing, not empirical claims.
- **Iceberg Access Control Patterns** ([iceberglakehouse.com](https://iceberglakehouse.com/iceberg/iceberg-access-control/))
  — Catalog-layer RBAC: namespace, table and column-level privileges with credential
  vending. *Supports:* §5.3.

### Companion studies

- **[[data-platforms-in-2029]]** — The forecast this study operationalizes. It identifies
  open table formats as the most robust bet in the whole 2029 picture and explicitly defers
  the "what to do about it now" question; §3 through §6 here are that deferred answer.
  Its counterpoint discipline is the model for §7.
- **[[producer-layer-and-contract-gated-democratization]]** — Maps the storage/catalog layer
  as one *movement* among several and rates its evidence. This study takes that movement as
  given and asks what an enterprise should do about it; read that note first if you want the
  market-scan framing rather than the playbook.
- **[[agentic-access-to-the-data-platform]]** — Directly relevant to §4.4: automated and
  agentic writers produce exactly the frequent-small-commit pattern that degrades optimistic
  concurrency, and the catalog-as-authorization-boundary argument in §5.3 is the same seam
  that study relies on for governing agent access.

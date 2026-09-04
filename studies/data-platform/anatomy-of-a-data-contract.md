# The Anatomy of a Data Contract

> What a data contract actually contains, why schema validation and data quality validation are
> different things that get conflated, how teams handle a breaking change once a contract exists,
> and what the standard is adding now that the consumer on the other end is an agent rather than
> an analyst.

- **Topic:** Data Platform
- **Date:** 2026-09-04
- **Status:** draft

> *The words written here are all AI-generated, but all the content was critically reviewed
> and validated by me — the use of AI is to accelerate the knowledge searching and narrative
> building.*

## Contents

1. [Context](#context)
2. [What a data contract is — and what it is not](#1-what-a-data-contract-is--and-what-it-is-not)
3. [Anatomy: eleven sections, five required fields](#2-anatomy-eleven-sections-five-required-fields)
4. [Schema validation is not data quality validation](#3-schema-validation-is-not-data-quality-validation)
5. [Where the contract actually bites](#4-where-the-contract-actually-bites)
6. [Breaking changes: prevent, version, or migrate](#5-breaking-changes-prevent-version-or-migrate)
7. [Context as part of the contract](#6-context-as-part-of-the-contract)
8. [Counterpoints: where this study could be wrong](#7-counterpoints-where-this-study-could-be-wrong)
9. [Takeaways](#takeaways)
10. [References](#references)

## Context

This study answers a narrow set of questions about data contracts: what one *is*, what it
contains, how the contract behaves at the two points in the lifecycle where it is applied
(ingestion and transformation), what distinguishes schema validation from data quality
validation, and — the question that turns out to have the most interesting answer — what teams
actually do when a change would break the contract.

It deliberately does **not** re-argue where contracts belong organizationally. This repo already
has that scan in [[producer-layer-and-contract-gated-democratization]], whose *Movement 5* covers
shift-left, contract-as-code, the data mesh precedent, and the Thoughtworks counter-current that
tempers all of it. That note asks *who should hold the gate*. This one asks *what the gate is made
of*.

**A note on evidence, stated up front.** Named company case studies for data contracts are thinner
and older than the discourse implies — the most-cited implementation write-ups are from 2021–2023,
and several of them were unreachable this session (see the method caveat below). What *is* current
and verifiable is the behavior of the tooling. So this study leans on a specific argument: **what
a mature tool refuses to let you do is better evidence of settled practice than a conference talk
about intentions.** dbt does not block deletion of a contracted model before its deprecation date
as a design flourish; it does that because teams needed the guarantee. Confluent did not add
broker-side validation because client-side enforcement was working. Named cases appear below as
dated illustration, not as the load-bearing evidence.

**Method caveat.** Direct fetches succeeded this session for `github.com` and
`raw.githubusercontent.com` — which is fortunate, because the Bitol RFCs and the ODCS
specification pages are the primary sources that matter most here, and they were read directly.
Blocked by the egress proxy: Medium, Substack, `martinfowler.com`, `bitol.io`, `jgp.ai`,
`confluent.io`, `docs.getdbt.com`, and `montecarlodata.com`. Claims sourced from those domains
came through the search index rather than the page itself and are marked *fetch blocked* in the
references. Every percentage from a vendor or analyst blog is **directional, not audited**.

## 1. What a data contract is — and what it is not

The usual definition — "an agreement between a data producer and its consumers about schema,
semantics, quality and operational expectations" — is accurate and nearly useless, because it
describes four other artifacts equally well. The distinctions that matter are these:

**A contract is not a schema.** A schema says what shape the data has. A contract says what shape
the producer *promises* it will keep having, plus who is accountable when it doesn't, plus how
long they will keep the promise before retiring it. Schema is one section of a contract; the
commitment and the expiry are the parts that make it contractual.

**A contract is not a test suite.** Tests assert things about data that already exists. A contract
is published *before* the data is consumed and is the thing tests are generated from. The
distinction is not academic — it is visible in tooling behavior, which §3 examines in detail.

**A contract is not a catalog entry.** A catalog entry is descriptive metadata about what exists,
usually harvested. A contract is authored, versioned in source control, and reviewed. The Bitol
TSC chair pushes this further, arguing the contract should be treated as a **"meta standard"**:
the place where the information is *authored*, from which every other representation — catalog
entry, semantic model, knowledge bundle — is a derived projection rather than an independent
source ([Perrin, *The Meta Standard Nobody Asked For*](https://dataintelligenceplatform.substack.com/p/the-meta-standard-nobody-asked-for)
— *fetch blocked*). *(Contested; this is a standards-body author arguing for the centrality of
his own standard, and no evidence was found of an organization actually operating this way.)*

**The API analogy, and where it breaks.** Contracts are routinely explained as "APIs for data,"
and the analogy earns its keep on versioning and deprecation (§5). It breaks on two points worth
naming. First, an API call that violates its contract fails immediately and visibly to the
caller; a data pipeline that violates its contract usually succeeds and produces wrong numbers
that surface days later, to someone else. Second, an API has a bounded set of operations, while a
dataset has an unbounded set of possible queries — which is precisely why §6's semantic additions
exist at all.

### The field consolidated onto one standard, recently

Worth stating plainly because much writing on this topic still presents a two-horse race: **it is
over**. Two YAML specifications competed — the **Open Data Contract Standard (ODCS)**, seeded by
the template [PayPal open-sourced in May 2023](https://github.com/bitol-io/open-data-contract-standard)
and now governed by the **Bitol** project under the Linux Foundation's LF AI & Data, and the
**Data Contract Specification** from INNOQ. With the release of ODCS v3.1.0, the Data Contract
Specification [formally deprecated itself](https://github.com/datacontract/datacontract-specification),
naming ODCS "the conceptual successor," committing to support only through the end of 2026, and
shipping a migration path (`datacontract export --format odcs`). Both are Apache/MIT-licensed and
vendor-neutral; ODCS carries the media type `application/odcs+yaml;version=3.1.0`.

This matters for anyone starting now: there is one standard to target, and the tooling that grew
up around the deprecated spec — notably the `datacontract-cli` — reads and writes both.

## 2. Anatomy: eleven sections, five required fields

An ODCS contract has eleven sections: **fundamentals**, **schema**, **data quality**,
**references** (authoritative definitions), **team**, **roles**, **service-level agreement**,
**infrastructure & servers**, **support & communication channels**, **pricing**, and **custom
properties**.

Reading that list, the natural assumption is that a contract is a heavyweight document. The
specification says otherwise, and this is the single most clarifying fact about ODCS:

**Of the entire standard, five fields are required** — `apiVersion`, `kind`, `id`, `version`, and
`status`. Not `name`. Not `description`. Not the schema section. Not quality, not SLA, not
ownership ([ODCS fundamentals](https://raw.githubusercontent.com/bitol-io/open-data-contract-standard/main/docs/fundamentals.md)).

```yaml
apiVersion: v3.1.0                              # required
kind: DataContract                              # required
id: 53581432-6c55-4ba2-a65f-72344a91553a        # required
version: 1.1.0                                  # required
status: active                                  # required
name: seller_payments_v1                        # optional
domain: seller                                  # optional
description:                                    # optional
  purpose: Views built on seller tables.
  usage: Twice daily, before meals.
  limitations: Cannot be used with full moon days.
```

The consequence is worth sitting with. **The standard is a shared vocabulary, not a minimum bar.**
A technically valid ODCS contract can promise nothing at all. Everything that makes a contract
*binding* — that a schema is declared, that quality thresholds exist, that someone owns it — is a
policy an organization layers on top, usually as lint rules in CI or as a certification gate
before publication. ODCS v3.1.0 did tighten validation, but in a specific direction: it forbids
*unknown* properties ("no additional or unevaluated properties are allowed" across several
sections). Rejecting a field you didn't expect is not the same as requiring a field you omitted.
This distinction returns with force in §6.

**Version history** *(useful for dating any claim about what ODCS "supports")*: v2.0.0 introduced
SemVer, SLAs, pricing and stakeholders; **v3.0.0 (2024-10-21)** was the major restructuring
(`uuid`→`id`, `columns`→`properties`, support for hierarchies and non-table formats, data quality
redesigned to accommodate multiple engines); v3.0.1 (2024-12-22) and v3.0.2 (2025-03-31) were
incremental; **v3.1.0 (2025-12-08)** added relationships and foreign keys, restructured `team`
from array to object, tightened validation, and added timezone-aware `timestamp`/`time` types;
**v3.2.0** carries the AI-facing additions of §6.

The **service-level** section is where operational promises live, and ODCS models it as a list of
named properties drawn from a Data QoS vocabulary — `latency`, `retention`, `frequency`,
`availability`, `generalAvailability`, `endOfSupport`, `endOfLife`, `timeOfAvailability`,
`throughput`, `errorRate`, and the incident-response trio `timeToDetect` / `timeToNotify` /
`timeToRepair`. Each entry carries a `driver` marking it as `regulatory`, `analytics`, or
`operational` — a small design decision with real consequences, since it lets you sort which
promises are negotiable and which are not.

Finally, the contract is not the largest unit. The **Open Data Product Standard (ODPS)** wraps
contracts into products: `inputPorts` and `outputPorts` each reference a `contractId`, with a
`sbom` and an `inputContracts` list recording what the product consumed. **The contract is the
interface; the product is the packaging.**

## 3. Schema validation is not data quality validation

These two get collapsed constantly, including by people who should know better, and the collapse
is why some teams conclude contracts "don't work." They are different mechanisms answering
different questions at different times with different failure behavior.

| | Schema validation | Data quality validation |
|---|---|---|
| Question | Does the data have the promised **shape**? | Are the **values** produced acceptable? |
| Nature | Binary, structural | Statistical, threshold-based |
| When | At write time or build time | After materialization, or on a schedule |
| Typical failure | Reject the record; fail the build | Alert, quarantine, route to a dead-letter queue |
| ODCS home | `schema` section | `quality` section |
| Can it be enforced? | Usually yes | Usually only observed |

The last row is the important one. Shape can be checked before data lands, cheaply and
deterministically. Value distributions generally cannot — you find out a column went 40% null
after the rows exist. **This asymmetry, not tooling immaturity, is why most quality rules alert
rather than block.**

ODCS expresses quality rules at four levels of formality
([ODCS data quality](https://raw.githubusercontent.com/bitol-io/open-data-contract-standard/main/docs/data-quality.md)):

- **`text`** — a human-readable expectation, not executable. Useful as a staging post.
- **`library`** — maintained metrics that need no SQL: `nullValues`, `missingValues`,
  `invalidValues`, `duplicateValues`, `rowCount`.
- **`sql`** — a query returning a number or boolean, with `{object}` and `{property}` placeholders
  so the rule is portable across tables.
- **`custom`** — an escape hatch that compiles to a specific engine (Soda, Great Expectations,
  dbt-tests).

Thresholds are expressed with comparison operators — `mustBe`, `mustNotBe`, `mustBeGreaterThan`,
`mustBeLessThan`, `mustBeBetween` and inclusive variants — with `unit` as `rows` or `percent`.
Rules carry a `dimension` (accuracy, completeness, conformity, consistency, coverage, timeliness,
uniqueness), plus `severity`, `businessImpact`, and an optional cron `schedule`.

```yaml
properties:
  - name: order_id
    quality:
      - metric: nullValues
        mustBe: 0
        unit: rows
      - metric: nullValues
        mustBeLessThan: 1
        unit: percent
```

### Two tools, two ways of drawing the line

**Confluent draws it by rule type.** Its data contracts separate **compatibility rules**, which
govern schema evolution, from **domain rules** written in Google's Common Expression Language
(CEL), which assert semantic validity of values — and these run in `WRITE` mode with a configured
action on failure, such as routing the offending message to a dead-letter queue
([Confluent, *Schema Registry Data Contracts*](https://docs.confluent.io/platform/current/schema-registry/fundamentals/data-contracts.html)).
This is the cleanest separation available in a mainstream product. *Caveat worth stating: schema
rules require Confluent Enterprise or Cloud with the Stream Governance "Advanced" package, v7.4+
— the clean separation is a paid feature.*

**dbt draws it by timing.** A model contract with `enforced: true` runs a **preflight check** —
does the model's query actually return the declared column names and data types? — and then
injects those types and constraints into the DDL it sends to the platform. If the shape is wrong,
**the build fails and the table is not created**. dbt *tests*, by contrast, run after the model
has been built. The often-repeated framing that "contracts are just tests with extra steps" gets
this backwards: tests validate what was produced, contracts refuse to produce it.
*(Caveat: which constraints are genuinely enforced varies by platform — several warehouses accept
constraint syntax and do not enforce it, so "declared" and "enforced" can silently diverge.)*

### And then the standard blurs the line on purpose

Having drawn that distinction, honesty requires noting that ODCS is deliberately eroding it.
**RFC-0012, "Implicit Data Quality Rules," approved by the TSC on 2025-09-16**, makes schema-level
declarations *imply* quality checks — a metrics-based design where declaring a property carries
validation semantics without a separately authored rule
([RFC-0012](https://raw.githubusercontent.com/bitol-io/tsc/main/rfcs/approved/odcs-v3.1.0/0012-implicit-dq-rules.md)).
The direction of travel is toward one declaration producing both a structural guarantee and a
value check. The conceptual distinction in the table above remains true about *enforcement
behavior* even as the *authoring surface* merges.

## 4. Where the contract actually bites

A contract has effect only where something can refuse. There are three such points in a typical
stack, and they differ enormously in strength.

**At ingestion, the contract can reject the write.** This is the strongest form and the only one
that prevents bad data from existing. Kafka's Schema Registry enforces in the producer SDK
(client-side) and — crucially — with **broker-side Schema ID Validation** as a backstop. The
existence of that second mechanism is itself the evidence: client-side enforcement alone was
bypassable, so the platform grew a check the application cannot route around. Any contract
enforced only in a library the producer chooses to use is advisory.

**At transformation, the contract can fail the build.** dbt's preflight-plus-DDL mechanism (§3) is
the reference implementation. The data does not get published in the wrong shape because the
publishing step aborts.

**In CI, the contract can block the merge.** The `datacontract-cli` (MIT) provides `lint` to
validate the contract document, `test` to run schema and quality checks against real data — via
soda-core, DuckDB and Spark, across 18+ sources — `breaking` to detect backward-incompatible
changes between versions, and `changelog` to diff them. It imports from SQL DDL, Avro, Protobuf,
JSON Schema, BigQuery and Glue, and exports to ODCS, dbt, Avro, Protobuf, JSON Schema, SQL DDL,
RDF, Terraform, SodaCL, DBML and HTML, and ships as a GitHub Action
([datacontract-cli](https://github.com/datacontract/datacontract-cli)). `breaking` running in CI
is the concrete mechanism behind most claims that contracts "prevent breaking changes."

**GoCardless is the case worth citing here**, because it inverts the usual relationship: rather
than validating a pipeline against a contract, it *generates* the pipeline from one. Schemas are
defined in Jsonnet/JSON, and once the definition is merged in GitHub, dedicated BigQuery and
Pub/Sub resources are automatically provisioned and populated through their internal self-service
platform. They reported roughly **300 contracts in production across 28 teams**, about half
created in the preceding six months, and framed the friction of requiring explicit publication as
the *point* — it is what creates an interface someone commits to maintaining
([GoCardless engineering](https://medium.com/gocardless-tech/data-contracts-at-gocardless-6-months-on-bbf24a37206e)
— *fetch blocked; figures via search index, dated 2022*).

### What this does to lineage

Lineage is a consequence of enforcement rather than a feature of it, and the state of it is less
settled than the marketing suggests.

ODCS can already declare lineage *inside* the schema: `transformSourceObjects` lists the upstream
objects a property was derived from, `transformLogic` carries the literal SQL, and
`transformDescription` states it in business terms. Alongside `criticalDataElement`,
`classification` and `primaryKey`, that is enough to drive a basic impact analysis.

```yaml
- name: txn_ref_dt
  transformSourceObjects: [table_name_1, table_name_2]
  transformLogic: "sel t1.txn_dt as txn_ref_dt from table_name_1 t1 ... where t1.txn_dt=date-3"
  transformDescription: "Defines the logic in business terms."
  criticalDataElement: true
```

But the standard is not happy with this. **RFC-0011 ("Lineage") remains open**, awaiting a TSC
decision, and it exists to criticize exactly the above: table-to-table only, no namespace or
domain context, and column-level detail it considers too fine-grained. It proposes replacing that
with a `lineage` block carrying `inputDataContracts` (UUIDs of upstream contracts) and
`outputDatasets` (namespace and name following **OpenLineage** conventions)
([RFC-0011](https://github.com/bitol-io/tsc/blob/main/rfcs/0011-lineage.md)).

The useful concept the RFC contributes is the split between **design lineage** — declared
dependency between contracts, known before anything runs — and **operational lineage** — emitted
per job execution by OpenLineage and collected in something like Marquez. They are complementary:
design lineage tells you what *should* depend on what and is available at review time; operational
lineage tells you what actually read what, after the fact.

**The honest read is counter-intuitive**: the claim that data contracts improve lineage is
directionally right — impact analysis genuinely requires knowing who consumes a field — but the
contract↔lineage link is the *least* mature part of the standard, still an open RFC while the
AI-facing additions of §6 were approved and shipped. *(Well-evidenced: the RFC's open status and
its stated critique of the current fields are both directly verifiable.)*

## 5. Breaking changes: prevent, version, or migrate

This is where a contract stops being documentation and starts costing someone something, and the
question "do you cut a new version, or just ship the new shape downstream?" has three answers in
active use. Which one a team picks reveals more about its data culture than any policy document.

First, what counts as breaking. In dbt's model contracts: removing a column, changing a column's
`data_type`, removing or modifying a constraint, or changing an unversioned contracted model at
all. In schema-registry terms: removing a required field, renaming without an alias, and — the
one that surprises people — **adding a field without a default**, because existing data lacks the
field and there is no value to substitute. Safe changes are adding an optional field with a
default and widening a numeric type.

### Strategy 1 — Prevent: the registry refuses the change

The producer literally cannot register an incompatible schema. Compatibility mode is the policy
knob, and it is best understood as **a decision about who deploys first**:

| Mode | Guarantee | Deployment order |
|---|---|---|
| `BACKWARD` | New consumer reads old data | **Consumers first** |
| `FORWARD` | Old consumer reads new data | **Producers first** |
| `FULL` | Both directions | Either order |
| `*_TRANSITIVE` | Same, but checked against **all** prior versions, not just the latest | As above |

The transitive variants are the ones teams discover late: without them, a chain of individually
compatible changes can leave version 3 unreadable by a consumer still on version 1.

**Cost:** the change simply does not happen until the producer reshapes it into something
compatible. Strong safety, real velocity friction.

### Strategy 2 — Version and deprecate: consumers migrate on their own clock

The producer publishes a new version, the old one keeps running, and consumers move before a
declared date. dbt implements this concretely: the producer sets a `deprecation_date` on the old
version, and a consumer that would otherwise break switches from `ref('model')` to a **pin on the
last compatible version**, buying time to migrate without blocking the producer from shipping.

The detail that makes this more than convention: **dbt refuses to delete a model with an enforced
contract before its `deprecation_date` has passed.** The deprecation window is enforced by the
tool against the *producer*, not merely promised to the consumer. That is the kind of behavior
this study treats as evidence of settled practice — nobody builds that unless the informal version
failed.

**Cost:** you run two versions of the pipeline for the length of the window, and someone has to
chase the stragglers.

### Strategy 3 — Migrate: transform between versions in flight

Rather than preventing or duplicating, translate. Confluent's data contracts support declarative
**migration rules expressed in JSONata**, transforming data from one schema version into another,
so changes that would normally break downstream consumers can be accommodated in transit.

**Cost:** the translation logic is real code with real bugs, it accumulates as versions pile up,
and — stated plainly — this sits behind the same Enterprise/Cloud "Advanced" licensing as the
domain rules in §3. **Strategy 3 is partly a procurement decision.**

### Choosing between them

Underneath all three sits the same convention: **SemVer, where MAJOR means consumer action is
required**, usually paired with an expand-and-contract window (add the new field, dual-write,
migrate consumers, announce deprecation, remove in the next major).

Three questions decide which strategy fits:

1. **Do you know the full set of consumers?** Closed and known → versioning works, because you can
   name who must move. Open or unknown → prevention is the only safe option, since you cannot run
   a migration campaign for an audience you can't enumerate.
2. **Do you have the authority to make them move?** If not, prevention or migration are your
   options; versioning silently assumes someone actually migrates before the date, and a
   deprecation window nobody honors is just a delayed outage.
3. **Is it a stream or a table?** Streams already have a registry sitting in the write path, so
   compatibility enforcement is the natural mechanism. Warehouse tables have no equivalent
   interception point, which is precisely why dbt's versioned models with pinned refs exist as the
   closest analogue.

Most organizations of any size end up running all three in different places, and that is not
incoherence — it is the correct response to having both streams and tables, and both known and
unknown consumers.

## 6. Context as part of the contract

The most recent movement in the standard is not structural. It is **semantic**, and it is driven
by the consumer changing from an analyst to an agent.

The framing worth borrowing comes from Thoughtworks: making data ready for agentic AI requires a
**foundation** layer (data that is trusted), a **context** layer (meaning made explicit rather
than living in someone's head), and an **access** layer (controlling how agents operate on it).
Their argument for urgency is the sharpest sentence in the literature: *a person pauses at a
number that feels wrong; an agent acts on it confidently*
([Sadalage & Chandrasekaran, *Making Your Data Ready for Agentic AI*](https://martinfowler.com/articles/making-data-ready-for-agentic-ai.html)
— *fetch blocked*).

### The `context` block

**RFC-0038, approved by the TSC on 2026-05-18/19**, lands simultaneously in **ODCS v3.2.0 and
ODPS v1.1.0**. It adds an optional `context` object with three fields
([RFC-0038](https://raw.githubusercontent.com/bitol-io/tsc/main/rfcs/approved/odcs-v3.2.0/0038-context.md)):

```yaml
context:
  instructions: "Use for revenue analysis and order trends. Do not use for individual
    customer PII queries."
  verifiedStatements:
    - question: "What was total revenue last quarter?"
      answer: "Query ${total_turnover_euros} grouped by year."
    - question: "Show top countries by order count?"
  constraints:
    - constraint: "Do not expose individual order details; aggregate to country level minimum."
      tags: [gdpr, pii]
```

- **`instructions`** is guidance for machines, deliberately distinct from `description`, which
  remains for humans. The same contract now carries two audiences explicitly.
- **`verifiedStatements`** are curated question/answer pairs with two modes: an entry *with* an
  `answer` is returned **verbatim** when a query is semantically close, while an entry *without*
  one primes text-to-SQL and helps disambiguate.
- **`constraints`** are negative guidance — what a consumer must *not* do — carrying tags such as
  `[gdpr, pii]`.

Context **cascades**: Data Product → Data Contract → Schema Object, with lower levels taking
precedence for instructions and statements, but **constraints are never suppressed** by a lower
level. That asymmetry is a genuinely good design decision: it means a permissive schema-level
block cannot quietly override a restrictive product-level prohibition. Property-level context was
deliberately deferred.

The justification cited in the RFC is empirical: semantic descriptions alone improve SQL
generation accuracy by **12%**, and combined metadata approaches by **20–27%**. *(Directional —
these figures are quoted in the RFC's motivation section, and this study did not verify the
underlying studies.)*

### The rest of the AI-facing surface

- **RFC-0042, `vector` logical type — approved 2026-06-30**, ODCS v3.2.0. Fields: `dimensions`
  (required), `elementType`, `distanceMetric` (cosine, dotProduct, euclidean, hamming,
  manhattan), `embeddingModel`, `embeddingModelVersion`, `normalized`. The most interesting use
  case listed is not portability but **detecting stale embeddings generated by a retired model** —
  a failure mode that is invisible without model provenance recorded alongside the vectors.
- **RFC-0027, unstructured data quality — in review.** Extends quality to text, documents and
  multimedia with nine dimensions, two of which — **relevance** and **interpretability** — have no
  tabular equivalent.
- **RFC-0044, Open Semantic Definition Standard — pending.** A `kind: SemanticDefinition`
  document letting a concept be defined once in its owning domain and referenced by any number of
  contracts through `authoritativeDefinitions` of type `semanticDefinition`. It supersedes the
  earlier Business Definitions RFC and is federated by design rather than a central master schema.

### Is any of this mandatory? No — and that is the finding

The direct answer: **RFC-0038 defines `context` as optional and explicitly non-breaking**; every
existing contract remains valid without it. And that is not an exception, it is the pattern. Recall
§2: five required fields in the entire standard. **ODCS does not make semantics mandatory anywhere,
because ODCS does not make almost anything mandatory anywhere.** The v3.1.0 validation tightening
does not change this — forbidding unknown fields is not the same as requiring known ones.

Where mandatoriness exists in practice, it is **organizational policy layered on top**:
certification gates that define minimum completeness before an asset can be published, metadata
completeness thresholds, and lint rules in CI. The standard supplies the vocabulary; the
organization supplies the obligation.

**And a limitation this study will not paper over: no solid public evidence was found of any
company using the `context` block in production.** It was approved in May 2026. The guidance
circulating is prospective advice — start with `instructions` and `constraints` on your
most-queried contracts, where text-to-SQL accuracy is bleeding today — not a report of results.
Approved is not adopted.

### The governance problem this creates

Setting aside adoption, the design raises a question the RFC does not answer. A
`verifiedStatement` with an `answer` is **returned verbatim** to a consumer whose question is
semantically close. That answer is a business assertion that **nothing re-validates against the
data**. Schema declarations are checked at write time; quality rules are checked on a schedule;
a curated answer is checked by nobody.

So: who reviews it? Who versions it when the underlying metric definition changes? What happens
when it silently goes stale — the contract keeps serving a confident, verbatim, wrong answer, and
unlike a stale dashboard there is no visible timestamp to prompt suspicion. Contracts solved
exactly this class of problem for schema by making the promise explicit, versioned, and
enforceable. The `context` block reintroduces the problem one layer up, in prose, and the standard
currently offers no `deprecation_date` for a sentence.

This is not an argument against the block — the semantic gap it addresses is real, and schema and
quality rules genuinely never captured it. It is an argument that **context needs the same
lifecycle machinery the rest of the contract has**, and does not yet have it.

## 7. Counterpoints: where this study could be wrong

**"Tooling behavior proves practice" is an inference, not a measurement.** The core evidence
strategy of this study (§Context) could mislead. A vendor may ship a feature because one large
customer demanded it, or because a competitor shipped it, not because the practice is widespread.
dbt's deprecation-date enforcement proves dbt's maintainers believed it necessary; it does not
prove most teams use versioned models. Read every tooling claim here as evidence of *what is
possible and considered good practice by tool authors*, not as adoption data.

**The named cases are old.** GoCardless is 2022, PayPal's template 2023. A 2026 study leaning on
them is describing a field as it was three to four years ago. Several of those sources were read
through a search index rather than directly (*fetch blocked*), which compounds the risk of a
misquoted figure.

**Describing is not enforcing, and most implementations only describe.** The sharpest critique of
this space holds that the majority of contract tooling validates and reports without ever refusing
anything, with field reports of organizations where contracts were regularly violated with no
consequence because they were treated as documentation. If that is the median implementation, then
the mechanisms catalogued in §4 describe a well-designed minority rather than the norm. *(This
study could not verify those field percentages against a primary source — treat as directional.)*

**The contract can become the bottleneck it was meant to remove.** Requiring explicit publication
slows producers down, and without governance "shift left" degrades into pushing chaos upstream.
The most credible independent voice on data mesh maturity describes a *re-centralization* of the
platform substrate and a softening of producer-side gatekeeping into facilitation — a direct
tension with contract-as-gate. [[producer-layer-and-contract-gated-democratization]] weighs that
counter-current in detail; this study assumes the contract is wanted and asks how it works, which
begs that question rather than answering it.

**The `context` block may be a category error.** §6 treats it as governance needing lifecycle
machinery. An equally defensible reading is that it is **context engineering wearing governance
clothes** — prompt material that happens to be stored in a YAML file next to a schema, and which
will migrate to whatever the agent tooling standardizes on, leaving the contract holding a stale
copy. There is also an unexamined security surface: `instructions` is text written to be *read by
an agent as instruction*, which makes contract metadata an injection vector if authorship of
contracts is less tightly controlled than authorship of code.

**Lineage may be less immature than §4 concludes.** The argument rests heavily on RFC-0011 being
open. An RFC can stay open because the problem is genuinely unsettled, or because nobody
prioritized closing something that already works well enough via `transformSourceObjects` plus
OpenLineage in the runtime. This study reads it as the former; that reading is contestable.

## Takeaways

- **The standard is a vocabulary, not a minimum bar.** Five required fields in all of ODCS —
  `apiVersion`, `kind`, `id`, `version`, `status`. Everything that makes a contract binding is a
  policy your organization adds in CI or in a certification gate. If you adopt ODCS expecting the
  spec to enforce rigor, you will get a valid document that promises nothing.

- **Schema validation and quality validation fail differently, and that is structural.** Shape can
  be checked before data exists, so it can *block*; value distributions can only be checked after,
  so they mostly *alert*. Confluent separates them by rule type, dbt by timing. Teams that expect
  quality rules to prevent bad data are misreading a limitation of the universe as a limitation of
  their tooling.

- **Breaking changes have three answers, and the choice is about consumers, not technology.** Do
  you know who they are, can you make them move, and is it a stream or a table? Prevention suits
  unknown consumers, versioning suits known ones you have authority over, and migration is partly
  a licensing decision. Most large organizations correctly run all three.

- **The strongest contract enforcement lives at ingestion, and it is rarer than the discourse
  implies.** Only at the write path can a contract *reject* rather than *report* — and the
  existence of broker-side validation as a backstop to client-side SDK checks is the tell that the
  weaker form was routinely bypassed.

- **The AI-ready turn is semantic, approved, and unadopted.** The `context` block (instructions,
  verifiedStatements, constraints, cascading with constraints never suppressed) and the `vector`
  type with embedding provenance are real, dated, TSC-approved additions to ODCS v3.2.0. No public
  evidence was found of production use. Treat guidance about them as prospective.

- **Contracts solved stale promises for schema and just reintroduced them for prose.** A curated
  `verifiedStatement` is returned verbatim and validated by nothing. Until context gets the
  versioning, ownership and expiry that schema already has, it is documentation with better
  distribution — which is precisely the failure mode contracts were invented to fix.

- **Open for the next pass:** whether RFC-0011 closes and how contract-declared lineage reconciles
  with OpenLineage in practice; any first-hand report of the `context` block in production; and
  independent (non-vendor) measurement of whether contract enforcement reduces incidents, which
  remains unquantified outside marketing material.

## References

*Links checked September 2026. Bitol RFCs and ODCS specification pages were fetched directly and
are the primary sources for every claim about the standard. Sources marked* fetch blocked *were
reached through a search index rather than the page itself — verify quotes before citing them
onward. Vendor materials are cited for mechanism and design intent, not as endorsement, and every
percentage from a vendor or analyst is directional rather than audited.*

### The standard itself (primary; fetched directly)

- **Open Data Contract Standard — Bitol / LF AI & Data** ([github.com](https://github.com/bitol-io/open-data-contract-standard))
  — the specification, governance, licensing and media type. *Supports:* §1's consolidation
  account and §2's section list.
- **ODCS fundamentals** ([raw.githubusercontent.com](https://raw.githubusercontent.com/bitol-io/open-data-contract-standard/main/docs/fundamentals.md))
  — required vs optional fields. *Supports:* the five-required-fields finding in §2, which is the
  spine of §6's answer on mandatoriness.
- **ODCS schema section** ([raw.githubusercontent.com](https://raw.githubusercontent.com/bitol-io/open-data-contract-standard/main/docs/schema.md))
  — `transformSourceObjects`, `transformLogic`, `transformDescription`, `criticalDataElement`,
  `classification`. *Supports:* the contract-declared lineage discussion in §4.
- **ODCS data quality section** ([raw.githubusercontent.com](https://raw.githubusercontent.com/bitol-io/open-data-contract-standard/main/docs/data-quality.md))
  — the four rule types, threshold operators, dimensions, severity and scheduling. *Supports:* §3.
- **ODCS service-level agreement section** ([raw.githubusercontent.com](https://raw.githubusercontent.com/bitol-io/open-data-contract-standard/main/docs/service-level-agreement.md))
  — `slaProperties`, the Data QoS property vocabulary, the `driver` field. *Supports:* §2's SLA
  paragraph.
- **ODCS CHANGELOG** ([github.com](https://github.com/bitol-io/open-data-contract-standard/blob/main/CHANGELOG.md))
  — dated version history. *Supports:* every "as of version X" claim in §2.
- **Open Data Product Standard** ([github.com](https://github.com/bitol-io/open-data-product-standard))
  — `inputPorts`/`outputPorts`, `contractId`, `sbom`. *Supports:* the contract-vs-product
  distinction closing §2.

### Bitol RFCs (primary; the evidence for §4 and §6)

- **RFC-0038, Context Block for AI and Semantic Interoperability** ([raw.githubusercontent.com](https://raw.githubusercontent.com/bitol-io/tsc/main/rfcs/approved/odcs-v3.2.0/0038-context.md))
  — approved 2026-05-18/19; `instructions`, `verifiedStatements`, `constraints`, the cascade, the
  12% / 20–27% figures, OSI `ai_context` compatibility. *Supports:* all of §6. *Caveat:* the
  accuracy figures are quoted in the RFC's motivation and were not independently verified here.
- **RFC-0042, Vector Type** ([raw.githubusercontent.com](https://raw.githubusercontent.com/bitol-io/tsc/main/rfcs/approved/odcs-v3.2.0/0042-vector-type.md))
  — approved 2026-06-30; `dimensions`, `distanceMetric`, `embeddingModel`, stale-embedding
  detection. *Supports:* §6's AI-facing surface.
- **RFC-0011, Lineage** ([github.com](https://github.com/bitol-io/tsc/blob/main/rfcs/0011-lineage.md))
  — **still open**; `inputDataContracts` / `outputDatasets`, the design-vs-operational lineage
  split, the critique of the existing transform fields. *Supports:* §4's counter-intuitive read
  that the contract↔lineage link is the least mature part of the standard.
- **RFC-0012, Implicit Data Quality Rules** ([raw.githubusercontent.com](https://raw.githubusercontent.com/bitol-io/tsc/main/rfcs/approved/odcs-v3.1.0/0012-implicit-dq-rules.md))
  — approved 2025-09-16. *Supports:* §3's closing point that the standard is intentionally
  blurring the schema/quality authoring boundary.
- **RFC-0027 (unstructured data quality, in review) and RFC-0044 (Open Semantic Definition
  Standard, pending)** ([tsc/rfcs](https://github.com/bitol-io/tsc/tree/main/rfcs))
  — *Supports:* §6. *Caveat:* neither is approved; do not describe them as part of the standard.

### Tooling (the load-bearing evidence for "how it is applied")

- **Data Contract CLI** ([github.com](https://github.com/datacontract/datacontract-cli))
  — `lint` / `test` / `breaking` / `changelog`, soda-core + DuckDB + Spark execution, import and
  export matrix, GitHub Action. *Supports:* §4's CI enforcement point.
- **Data Contract Specification** ([github.com](https://github.com/datacontract/datacontract-specification))
  — **the deprecation notice naming ODCS the conceptual successor**, support through end of 2026,
  and the `servicelevels` vocabulary. *Supports:* §1's claim that the standards contest is over.
- **Schema Registry Data Contracts — Confluent** ([docs.confluent.io](https://docs.confluent.io/platform/current/schema-registry/fundamentals/data-contracts.html))
  — compatibility rules vs CEL domain rules vs JSONata migration rules; DLQ on failure.
  *Supports:* §3's rule-type separation and §5's strategy 3. *Caveat:* vendor documentation, and
  the capability requires a paid Stream Governance tier — noted in-line.
- **Schema Evolution & Compatibility Types — Confluent** ([docs.confluent.io](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html))
  — BACKWARD / FORWARD / FULL and the transitive variants. *Supports:* §5's deployment-order table.
- **Model contracts, model versions and `deprecation_date` — dbt Labs** ([docs.getdbt.com](https://docs.getdbt.com/docs/mesh/govern/model-contracts))
  — preflight check, DDL injection, the breaking-change list, pinned `ref`, and the refusal to
  delete a contracted model before its deprecation date. *Supports:* §3's timing-based separation
  and §5's strategy 2. *Caveat:* vendor documentation, *fetch blocked* — read via search index;
  the constraint-support matrix varies by platform and should be checked per warehouse.

### Practice and case material (dated; illustration rather than spine)

- **Data Contracts at GoCardless — 6 Months On / Implementing Data Contracts at GoCardless**
  ([medium.com](https://medium.com/gocardless-tech/data-contracts-at-gocardless-6-months-on-bbf24a37206e))
  — ~300 contracts, 28 teams, Jsonnet definitions generating BigQuery and Pub/Sub resources on
  merge. *Supports:* §4's contract-generates-infrastructure inversion. *Caveat:* 2022; *fetch
  blocked* — figures via search index.
- **Data Contracts: Developing Production-Grade Pipelines at Scale — Sanderson, Freeman & Schmidt
  (O'Reilly, Dec 2025)** ([oreilly.com](https://www.oreilly.com/library/view/data-contracts/9781098157623/))
  — the current book-length treatment of the architecture. *Supports:* general framing.
  *Caveat:* not read for this study; listed as the obvious next source.
- **Driving Data Quality with Data Contracts — Andrew Jones** ([oreilly.com](https://www.oreilly.com/library/view/driving-data-quality/9781837635009/))
  — the GoCardless practitioner's account. *Caveat:* not read directly.
- **7 Lessons From GoCardless' Implementation of Data Contracts — Monte Carlo** ([montecarlodata.com](https://www.montecarlodata.com/blog-data-contracts/))
  — introduce contracts during periods of change; contracts suit decentralized teams. *Caveat:*
  vendor; *fetch blocked*.

### Critical / counter-signal

- **Making Your Data Ready for Agentic AI — Sadalage & Chandrasekaran, Thoughtworks** ([martinfowler.com](https://martinfowler.com/articles/making-data-ready-for-agentic-ai.html))
  — the foundation / context / access layering and the "an agent acts on it confidently" argument.
  *Supports:* §6's framing. *Caveat:* *fetch blocked*; consultancy-authored.
- **Your Data Contracts Are in the Wrong Spot — Chad Sanderson** ([dataproducts.substack.com](https://dataproducts.substack.com/p/your-data-contracts-are-in-the-wrong))
  — contracts placed mid-pipeline become bottlenecks rather than prevention. *Supports:* §7.
  *Caveat:* *fetch blocked*; the author is a vendor founder in this space.
- **Data Contracts: Silver Bullet or False Panacea? — Monte Carlo** ([montecarlodata.com](https://www.montecarlodata.com/blog-data-contracts-open-questions/))
  — open questions on enforcement, ownership and scope. *Supports:* §7. *Caveat:* vendor whose
  product is observability, i.e. the detect-after alternative; *fetch blocked*.
- **The Shift-Left Playbook — Ataccama** ([ataccama.com](https://www.ataccama.com/blog/the-shift-left-playbook-data-contracts-data-quality-gates-and-feedback-loops))
  — producer-velocity cost and the "Spread Chaos Left" failure mode. *Supports:* §7. *Caveat:*
  vendor.
- **OpenLineage** ([github.com](https://github.com/OpenLineage/OpenLineage))
  — the operational-lineage standard RFC-0011 proposes aligning to. *Supports:* §4.

### Companion studies

- [[producer-layer-and-contract-gated-democratization]] — the market scan of *where* contracts sit
  organizationally (Movement 5: shift-left, contract-gated promotion, and the Thoughtworks
  counter-current). That note asks who should hold the gate; this one describes the gate's
  mechanism. Read together for the full picture.
- [[data-platforms-in-2029]] — the forward-looking piece; §2 and §3 there name the
  contract-formalized producer/consumer interface as a structural force.
- [[agentic-access-to-the-data-platform]] — the consumer side of §6: what changes when the thing
  querying your data is an agent.

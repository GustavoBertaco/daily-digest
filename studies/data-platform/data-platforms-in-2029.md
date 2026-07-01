# Data Platforms in 2029

> A forward-looking map of where data platforms are likely heading by 2029 — a glance at the plausible future state, to inform planning done elsewhere.

- **Topic:** Data Platform
- **Date:** 2026-06-21
- **Status:** draft

## Contents

1. [Context](#context)
2. [The forces shaping the next three years](#1-the-forces-shaping-the-next-three-years)
3. [The likely state of the platform in 2029](#2-the-likely-state-of-the-platform-in-2029)
4. [What changes for the people and the operating model](#3-what-changes-for-the-people-and-the-operating-model)
5. [Takeaways](#takeaways)
6. [References](#references)

## Context

This study takes a **glance at where data platforms are plausibly heading by 2029** — to
help teams making multi-year commitments (storage formats, compute engines, governance
models, build-vs-buy, cloud strategy) plan against a target that is moving under them.

A word on epistemic humility (knowing the limits of what we can claim to know), because this domain earns it. Forecasting data architecture
has a poor track record: the industry spent roughly a decade building distributed systems
for data that mostly fit on a single machine ([DuckDB, *The Lost Decade of Small Data*](https://duckdb.org/2025/05/19/the-lost-decade-of-small-data)),
and the first data-mesh wave produced about as many "lip-service" domains as genuine ones
([Thoughtworks, *State of data mesh 2026*](https://www.thoughtworks.com/insights/blog/data-strategy/the-state-of-data-mesh-in-2026-from-hype-to-hard-won-maturity)).
So this is a **foresight exercise** (in the Shell/GBN scenario-planning tradition) — a map of
plausible directions held with calibrated confidence, not a prediction. **Scope:** it
describes the future *state*; "what to do about it now" is left to a separate planning study.
And a caveat on the evidence itself: much public material on the 2029 platform comes from
vendors forecasting outcomes they profit from, so this study leans on primary and independent
signals where it can and flags conflicts where it can't.

**What looks near-certain** (multiple independent signals, not one vendor's roadmap):

- **The data foundation — not the model — is the binding constraint on AI.** Around eight in
  ten organizations cite data limitations as the roadblock to scaling agents, and fewer than
  10% have scaled them to tangible value ([McKinsey](https://www.mckinsey.com/capabilities/mckinsey-technology/our-insights/building-the-foundations-for-agentic-ai-at-scale));
  Gartner expects **60% of AI projects to be abandoned through 2026** for lack of AI-ready
  data, with 63% of organizations lacking or unsure of AI-ready data practices ([Gartner](https://www.gartner.com/en/newsroom/press-releases/2025-02-26-lack-of-ai-ready-data-puts-ai-projects-at-risk)).
- **Data keeps growing — and most individual workloads stay small.** IDC's Global DataSphere
  shows total data creation rising steeply, led by unstructured data ([IDC](https://my.idc.com/getdoc.jsp?containerId=US53363625)),
  even as the median analytical scan sits near ~100 MB and the 99.9th-percentile read under a
  few hundred GB — a DuckDB finding independently corroborated by Amazon's and Snowflake's own
  fleet telemetry (§1.3) ([DuckDB](https://duckdb.org/2025/05/19/the-lost-decade-of-small-data)).
  Both are true; the platform must serve a long tail of small queries over an ever-larger whole.
- **Open table formats are consolidating** into a converging Iceberg/Delta core ([Databricks](https://www.databricks.com/blog/next-era-open-lakehouse-apache-icebergtm-v3-public-preview-databricks)).
- **Kubernetes is the de-facto production substrate** — ~82% of organizations run it in
  production, a majority with stateful workloads ([CNCF 2025 survey](https://www.cncf.io/announcements/2026/01/20/kubernetes-established-as-the-de-facto-operating-system-for-ai-as-production-use-hits-82-in-2025-cncf-annual-cloud-native-survey/)).
- **Regulation is rising and hardening**, turning governance into an architecture input
  rather than a downstream overlay (BCBS 239, DORA, regional privacy such as LGPD).

**What is genuinely contested** (this is where the planning risk lives, and where I won't
pretend the sources agree):

- **How far agent autonomy actually goes** by 2029 — first-class consumer, or assistive
  copilot that still routes through humans. Adoption is real; *scaled value* is not yet.
- **Open formats vs. consolidated vendors.** "Open" here means *format-level* openness — a
  published, vendor-neutral on-disk spec any engine can read and write — not that the surrounding
  platform is open-source or vendor-plural. Even as the formats open in that narrow sense, the
  stack around them is consolidating into a few large vendors, and independent voices warn that
  "neutrality is eroding" and lock-in is shifting rather than disappearing
  ([The New Stack](https://thenewstack.io/data-stack-consolidation-risks/)). Format openness looks
  more like a *battleground* than a settled destination — which is precisely why Kubernetes/BYOC
  hedges exist.
- **Centralized vs. decentralized vs. federated ownership.** The pendulum keeps swinging; data
  mesh reached "hard-won maturity" largely by *re-centralizing the platform* while
  decentralizing ownership, and all three models coexist in practice ([Thoughtworks](https://www.thoughtworks.com/insights/blog/data-strategy/the-state-of-data-mesh-in-2026-from-hype-to-hard-won-maturity)).
- **Which modeling layer organizes the platform** — dimensional, Data Vault, semantic layer,
  knowledge graph — remains unsettled; they coexist today and likely still will in 2029.

**The through-line.** There is no single "2029 data platform," and any source promising one
is selling something. The most robust pattern across the *independent* signals is that the
platform's centre of gravity is drifting **toward the data layer** — open (vendor-neutral)
table formats, immutable and versioned assets, and governance and meaning enforced where the
data lives — because that is what AI-readiness and tightening regulation *separately* demand,
which is why it shows up regardless of who is forecasting. But the largest architectural bets —
autonomy, centralization, open-formats-vs-consolidated-vendors, scale-out-vs-single-node — stay
genuinely unresolved. The
planning-relevant insight is therefore not "adopt the winning architecture"; it is **build
for optionality** across these axes, because the evidence does not yet justify betting the
platform on any one of them.

## 1. The forces shaping the next three years

Five forces are pushing the platform toward its 2029 state. They are not equal: some are
**exogenous** (they happen *to* the platform team — AI demand, data growth, regulation) and
some are **choices** the team and its vendors are still actively contesting (open formats vs.
consolidated vendors, where ownership sits, which modeling layer wins). The planning value is in
telling them apart — you adapt to the first set and place bets on the second. Each force
below is tagged for confidence and for *who benefits from believing it*, because in this
domain the loudest sources are rarely disinterested.

**1.1 The demand force: AI pulls hard, but the data foundation is the throttle.**
*(Exogenous · near-certain direction, contested magnitude.)* The dominant pull on the
platform is no longer reporting or even self-service BI — it is feeding AI and, increasingly,
agents. But the constraint is not model quality; it is the data beneath it. Roughly eight in
ten organizations cite data limitations as the roadblock to scaling agents, and fewer than
10% have scaled them to tangible value ([McKinsey](https://www.mckinsey.com/capabilities/mckinsey-technology/our-insights/building-the-foundations-for-agentic-ai-at-scale));
Gartner expects 60% of AI projects to be abandoned through 2026 for lack of AI-ready data
([Gartner](https://www.gartner.com/en/newsroom/press-releases/2025-02-26-lack-of-ai-ready-data-puts-ai-projects-at-risk)).
What's near-certain is that AI demand reshapes platform priorities (governed access, lineage,
real-time context) and that the platform team owns much of the upside. What's contested is
*how far agent autonomy actually goes* by 2029 — first-class consumer or assistive copilot.

**1.2 The architecture force: open formats and composability — pulling against a
consolidation undertow.** *(Partly choice · genuinely two-directional.)* Open table formats
are converging on an Iceberg/Delta core ([Databricks](https://www.databricks.com/blog/next-era-open-lakehouse-apache-icebergtm-v3-public-preview-databricks)),
and the composable-systems movement is decoupling engines from storage through shared
intermediate representations ([Composable Data Management Manifesto, VLDB 2023](https://www.vldb.org/pvldb/vol16/p2679-pedreira.pdf)).
That points toward interchangeable, lock-in-resistant stacks. But the *opposite* force is
just as real: the stack is consolidating into a few large vendors, and independent voices
warn that "neutrality erodes" and lock-in shifts rather than disappears ([The New Stack](https://thenewstack.io/data-stack-consolidation-risks/)).
By 2029 "open" is most plausibly a **contested equilibrium** — open at the format layer,
consolidated at the platform layer — which is exactly why Kubernetes-native and
bring-your-own-cloud deployments persist as hedges ([CNCF](https://www.cncf.io/announcements/2026/01/20/kubernetes-established-as-the-de-facto-operating-system-for-ai-as-production-use-hits-82-in-2025-cncf-annual-cloud-native-survey/)).

**1.3 The economics force: the unit of compute shrinks and cost moves left.** *(Exogenous
hardware trend + choice.)* Two cost pressures compound. First, single-node engines now handle
the overwhelming majority of real workloads — the median analytical scan is ~100 MB and the
99.9th-percentile read is under a few hundred GB ([DuckDB](https://duckdb.org/2025/05/19/the-lost-decade-of-small-data)).
That figure comes from the vendor with the most to gain from it, so it's worth checking against
telemetry from vendors with the opposite incentive — and it holds up. Amazon's own analysis of
its production Redshift fleet (sampled across 200 instances, the public "Redset" trace) finds a
~2,030x gap between median and 99.9th-percentile query cost, with well under 0.1% of queries
consuming roughly a quarter of all compute ([*Why TPC Is Not Enough*, VLDB 2024](https://www.vldb.org/pvldb/vol17/p3694-saxena.pdf)).
The public "Snowset" trace of 70M real production Snowflake queries shows the same skew: a small
minority of large queries consume nearly half (45.6%) of total CPU time while the bulk of
queries stay small and cheap ([Snowset, NSDI 2020](https://www.usenix.org/conference/nsdi20/presentation/vuppalapati)).
Three vendors' own operational telemetry — DuckDB, Redshift, Snowflake — independently converges
on the same shape: most queries small and cheap, a thin tail huge and expensive. That erodes the
assumption that everything needs a scale-out cluster, *without* removing the need for one: IDC's
DataSphere shows the total keeps growing, led by unstructured data
([IDC](https://my.idc.com/getdoc.jsp?containerId=US53363625)). Second, cloud-data spend has
become a board-level line item, pushing FinOps from after-the-fact reporting toward
shaping spend *before* it happens ([State of FinOps](https://www.finops.org/framework/scope/finops-for-data-cloud-platforms/)).
Direction by 2029: a long tail of small, cheap, often single-node/streaming workloads
alongside a still-growing core — and cost-awareness designed into the platform, not bolted on.

**1.4 The control force: regulation and sovereignty become architecture inputs.**
*(Exogenous · near-certain and one-directional — it only tightens.)* The least speculative
force. Risk-data-aggregation rules (BCBS 239), operational-resilience and ICT-concentration
rules (DORA, in force since Jan 2025), and a thickening mesh of regional privacy regimes
(GDPR, LGPD and peers) increasingly dictate *where data lives, how long it's kept, how it's
lineage-tracked, and how resilient the platform must be*. By 2029 these are design
constraints set before architecture, not compliance overlays applied after — most acutely in
financial services, where they are effectively non-negotiable. This force is exogenous and
compounding: no platform team gets to opt out, and it tends to *favor* the immutability,
lineage and portability trends above for independent reasons. With one sharp exception: on the
*deletion* axis, privacy law (erasure, minimization, retention maxima) pulls directly *against*
immutability and time-travel — a tension §2.4 treats explicitly rather than pretending the
forces align on every axis.

**1.5 The operating-model force: the product *label* has already won; data-specific product
*rigor* has not.** *(Choice · contested.)* Gartner's benchmark — ~80% of large software
organizations running platform-engineering teams that operate the platform as a product — was a
target for *2026*, not 2029 ([Gartner](https://www.gartner.com/en/experts/top-tech-trends-unpacked-series/platform-engineering-empowers-developers)):
that shift has already happened. What hasn't is the *rigor* behind the label, especially for
data. A survey of 518 platform engineers found nearly 30% of platform teams still don't measure
success at all ([State of Platform Engineering, Vol. 4, Jan 2026](https://platformengineering.org/reports/state-of-platform-engineering-volume-4)) —
the framing arrived before the discipline did — and data lags furthest: data mesh, the movement
that first argued for treating data as a product, reached only "hard-won maturity" by 2026, with
many declared "data domains" turning out to be lip service rather than accountable ownership
([Thoughtworks](https://www.thoughtworks.com/insights/blog/data-strategy/the-state-of-data-mesh-in-2026-from-hype-to-hard-won-maturity)).
Data contracts are only beginning to formalize the producer/consumer interface that would make
that rigor real. On top of that, the *locus of ownership* — central, decentralized, or
federated — remains genuinely open: data mesh reached its current state largely by
**re-centralizing the platform while decentralizing ownership**, and all three models coexist in
practice. The 2029 question is therefore not *whether* platforms are run as products — that's
settled — but whether *data* products specifically close the gap to the rigor general platform
engineering already claims, and where ownership ends up sitting.

| Force | Direction by 2029 | Confidence | Who benefits from the claim (read skeptically) | Implication for the platform |
| --- | --- | --- | --- | --- |
| **AI / agentic demand** | Dominant pull; data foundation is the throttle | High on direction, low on autonomy magnitude | AI vendors & consultancies (upside); data-quality vendors (the "fix") | Invest in governed access, lineage, real-time context; don't over-build for full autonomy yet |
| **Open formats & composability** | Open at the format layer, consolidating at the platform layer | Medium — genuinely two-directional | Open-format vendors *and* consolidators both spin it their way | Treat portability (K8s/BYOC, open formats) as a hedge, not a settled win |
| **Compute & cost economics** | Small/streaming long tail beside a still-growing core; cost designed-in | High on direction, medium on mix | Single-node vendors push "small data"; hyperscalers push "scale-out" | Support both single-node and distributed; bake FinOps into provisioning |
| **Regulation & sovereignty** | Tightening, one-directional; becomes a design input | Highest in the set | Compliance/governance tooling vendors amplify it (but it's real) | Design for residency, retention, lineage, resilience up front — non-negotiable in FS |
| **Operating model & ownership** | Product *label* already near-universal (2026); data-specific product *rigor* and ownership locus both unsettled through 2029 | High on label, low on rigor and ownership | Platform-tooling & IDP vendors; data-mesh consultancies | Don't credit the label; fund the rigor (SLOs, catalogs, accountability) and keep ownership model reversible |

## 2. The likely state of the platform in 2029

This section sketches the plausible 2029 platform as a **layered reference picture** — but
read it as a *band* of states, not a blueprint. The forces in §1 that are near-certain shape
the layers consistently; the contested ones cut across them, so the layer descriptions give
the **mainstream-plausible** reading and the scenario lens at the end bounds the uncertainty.
Nothing here is a single-vendor architecture; it is the shape the independent signals point to.

**2.1 The substrate: open table formats, immutable and portable storage on a composable compute
fabric.** The base of the 2029 platform is open *at the format layer* — table/data formats with
a published, vendor-neutral spec that any engine can read and write, not necessarily an
open-source platform around them — and immutable by construction. Open table formats
have converged on an Iceberg/Delta core ([Databricks](https://www.databricks.com/blog/next-era-open-lakehouse-apache-icebergtm-v3-public-preview-databricks)),
data files are immutable with snapshots and time-travel native, and a versioning layer — at
the catalog ([Project Nessie](https://projectnessie.org/)) or the storage tier ([lakeFS](https://lakefs.io/))
— gives the data lake git-like branching and history. Compute is decoupled from storage and
*plural*: multiple engines query the same tables through shared intermediate representations
([Composable Data Management Manifesto, VLDB 2023](https://www.vldb.org/pvldb/vol16/p2679-pedreira.pdf)),
with single-node engines serving the long tail and distributed engines the still-growing core
([DuckDB](https://duckdb.org/2025/05/19/the-lost-decade-of-small-data)). Increasingly this runs
on a Kubernetes-native or bring-your-own-cloud substrate for portability and sovereignty
([CNCF](https://www.cncf.io/announcements/2026/01/20/kubernetes-established-as-the-de-facto-operating-system-for-ai-as-production-use-hits-82-in-2025-cncf-annual-cloud-native-survey/)).
*High confidence on format-level openness and immutability; contested is how much of the
surrounding platform actually escapes vendor consolidation (§1.2).
Immutability is not free, either: it buys audit and reproducibility at the cost of an erasure
obligation someone has to engineer back in — see §2.4.*

**2.2 The processing path: streaming-first, with batch as a peer not a default.** Ingestion,
enrichment, quality and governance shift *left* toward the source: streams become queryable
tables (Kafka topics materializing directly into Iceberg/Delta), and analytics increasingly run
in the stream rather than waiting for a warehouse load ([Kai Waehner, *2026 streaming trends*](https://www.kai-waehner.de/blog/2025/12/10/top-trends-for-data-streaming-with-apache-kafka-and-flink-in-2026/)).
Batch does not disappear; what changes is that real-time stops being a special case, and schema
and quality are enforced at the boundary by contracts rather than discovered downstream
([Chad Sanderson](https://dataproducts.substack.com/p/the-consumer-defined-data-contract)).

*The unglamorous first mile still dominates the bill.* Whatever processing paradigm wins, most
platform effort in 2029 still goes into *capture* — change-data-capture off operational stores,
the long tail of SaaS APIs, and schema drift at the source ([Debezium](https://debezium.io/) as
the open CDC baseline). Contracts move *where* quality is enforced (left, at the boundary); they
do not remove the underlying integration load. A 2029 plan that budgets for the streaming engine
but not for connector sprawl and source-schema volatility will be wrong in the same direction
platform plans have been wrong for a decade.

**2.3 The semantic layer: from tables to governed business meaning.** The platform's primary
interface is no longer the physical table but a governed semantic layer — trending toward
ontologies and knowledge graphs that encode entities, metrics and relationships ([Salesforce](https://www.salesforce.com/blog/agentic-future-demands-open-semantic-layer/);
[arXiv 2604.00555](https://arxiv.org/abs/2604.00555)) — with metrics defined as version-controlled
code ([dbt/MetricFlow](https://www.getdbt.com/blog/how-the-dbt-semantic-layer-works)). Beneath it,
modeling stays *plural*: Data Vault where auditable history is mandatory (notably FS), wide/
One-Big-Table where AI and ML consume flattened features, dimensional where it still earns its
keep. "No metadata, no AI" becomes literal — the modeling layer is the precondition for
trustworthy AI ([Gartner active metadata](https://atlan.com/gartner-active-metadata-management/)).
*Contested: whether knowledge graphs go mainstream or stay niche, and which method dominates.*

**2.4 The control layer: active metadata, governance, observability, cost — enforced where data
lives.** Governance moves from periodic and downstream to **real-time, data-layer and
event-driven**, orchestrated by active metadata that drives action across the estate ([Gartner/Atlan](https://atlan.com/gartner-active-metadata-management/)).
Data observability (freshness, volume, distribution, schema, lineage) becomes table-stakes
([Monte Carlo](https://www.montecarlodata.com/blog-data-testing-vs-data-quality-monitoring-vs-data-observability-whats-right-for-your-team/)),
and FinOps is designed into provisioning rather than reconciled after the invoice ([FinOps Foundation](https://www.finops.org/framework/scope/finops-for-data-cloud-platforms/)).
In regulated and financial-services settings this layer is where the platform is won or lost:
lineage, retention, residency and resilience are architectural requirements set by BCBS 239,
DORA and regional privacy law, mapped through frameworks like EDM Council's CDMC.

**Retention and erasure — the immutable platform's standing debt.** The immutability that makes
the substrate auditable (§2.1) collides head-on with privacy law's right-to-erasure, data
minimization, and retention *maxima*: you cannot simply `DELETE` a subject out of a chain of
immutable snapshots and time-travel history. The 2029 platform pays this debt deliberately, with
mechanisms designed in rather than bolted on — **crypto-shredding** (destroy a per-subject key so
its data is unrecoverable), row-level deletes and snapshot/partition rewrites that physically
expire history (Iceberg and Delta now expose these), tombstoning, and retention-tier expiry. The
hardest cases are governance, not engineering: **legal hold vs. retention maximum** — BCBS 239
wants long, reconstructable history while LGPD/GDPR want the same data gone — and **time-travel
vs. minimization**, where every retained snapshot is a copy a regulator can ask you to justify.
The honest position is that immutability and erasure *coexist by engineering, not by nature*; a
platform that adopts git-for-data without a deletion story has built an audit asset and a
compliance liability in one stroke ([CDMC](https://edmcouncil.org/frameworks/cdmc/) for the
control taxonomy; [LGPD](https://www.dlapiperdataprotection.com/index.html?t=law&c=BR)/GDPR for
the obligation; [Event Sourcing](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing)
for the append-only principle the tension is inherent to). *This qualifies the study's own safe
bet: immutability is low-regret only where a deletion path is engineered beside it.*

**Security is a first-class layer, not a sub-clause of governance.** Governance answers *who may
use what, for which purpose*; security answers *who can reach the bytes at all* — a different
control set and a different budget line. The load-bearing 2029 controls are attribute/policy-based
access enforced at the data layer (policy-as-code over the catalog), automated PII discovery,
classification and masking/tokenization, and encryption with customer-managed keys (the substrate
beneath crypto-shredding above). Agentic consumption (§2.5) adds an attack surface that governance
framing alone misses: an autonomous agent holding broad, governed query rights is a high-value
target and a confused-deputy risk — prompt-injected or over-scoped, it can exfiltrate at machine
speed *through* a perfectly governed contract. Least-privilege, per-action scoping and full
action-logging for agents are 2029 security requirements, not 2030 nice-to-haves
([OWASP Top 10 for LLM Applications](https://genai.owasp.org/)).

**2.5 The consumption surface: agents alongside humans.** Access broadens from dashboards and
hand-written SQL to **agent-mediated querying** through governed, intent-shaped tools that hit
the semantic layer rather than raw tables. Production reporting and human exploration persist;
the change is that a second class of consumer — autonomous or semi-autonomous agents — now
drives a meaningful share of load and demands a correct, governed contract. A third surface
widens too: **governed sharing across organizational boundaries** — data clean rooms and
data-product exchange — shifts sharing from bulk copies toward query-time, permissioned access
over the same open formats and semantic contracts, extending the in-house consumption model
outward. *How far that autonomy goes by 2029 is the single most contested variable in the study (§1.1).*

| Layer | Where it is in 2026 | Plausible 2029 state | What changes most |
| --- | --- | --- | --- |
| Ingestion / processing | Batch-default; streaming as add-on | Streaming-first; batch a peer; quality/governance shifted left | Real-time stops being a special case |
| Storage / table format | Iceberg/Delta gaining; some lock-in | Converged open core; immutable + versioned (git-for-data) | History, time-travel, audit become native |
| Compute / engine | Mostly distributed clusters | Decoupled, engine-plural; single-node tail + distributed core | Compute unit shrinks; portability (K8s/BYOC) |
| Modeling / semantic | Tables + BI metrics; semantic layer emerging | Semantic layer/knowledge graph as primary interface; metrics-as-code | Interface moves from tables to meaning |
| Governance / metadata | Periodic, downstream, catalog-based | Real-time, data-layer, active-metadata-orchestrated | Governance becomes enforcement, not audit |
| Security / retention | Perimeter + scheduled deletes | Data-layer access control, PII masking, crypto-shred erasure path | Deletion & least-privilege become design inputs |
| Consumption | Humans via dashboards/SQL | Humans + agents via governed tools over the semantic layer | Agents become first-class consumers |

**Scenario lens — bounding the four contested axes.** Rather than predict one outcome, the
study brackets the axes that §1 leaves open. A given organization in 2029 will likely sit at
different points on each:

| Contested axis | Conservative | Mainstream | Aggressive |
| --- | --- | --- | --- |
| Agent autonomy | Copilots; humans approve every action | Agents run governed queries under supervision | Agents act semi-autonomously across domains |
| Ownership locus | Central platform owns data | Central platform, federated domain ownership | Fully decentralized data products |
| Open formats vs. consolidated vendors | Single-vendor stack | Open formats under 1–2 platform vendors | Composable best-of-breed on open formats |
| Compute model | Scale-out default | Single-node tail + distributed core | Mostly single-node/streaming, burst to cloud |

## 3. What changes for the people and the operating model

The people changes follow the technology and lag it — and they are where most of the value,
and most of the failure, actually lands. The honest caveat up front: tooling is rarely the
constraint here; culture and adoption are. Industry adoption of internal platforms is high yet
a minority of organizations realize the productivity gains they expect, so everything below is
contingent on the operating model, not just the stack.

**A framing note before the changes: "platform teams become product teams" already happened —
it is not a 2029 prediction.** Gartner's own benchmark for that shift was 80% of large software
orgs by *2026* ([Gartner](https://www.gartner.com/en/experts/top-tech-trends-unpacked-series/platform-engineering-empowers-developers)),
which is now, not three years out. Stating it as a change *coming* by 2029 would be describing
the present as the future — an easy trap in forecasts that lean on adoption headlines instead of
checking their timestamps. What actually still moves between now and 2029 is narrower and less
comfortable: whether the *rigor* behind that
label — especially for data specifically, as distinct from general software platform
engineering — closes the gap it's currently well short of.

**The product label is universal; product rigor for data is not — that gap, not adoption, is
the real 2029 question.** A survey of 518 platform engineers found nearly 30% of platform teams
still don't measure success at all ([State of Platform Engineering, Vol. 4, Jan 2026](https://platformengineering.org/reports/state-of-platform-engineering-volume-4)),
even where "platform as product" is the stated model — the label arrived well ahead of the
discipline (SLOs tied to outcomes, roadmaps driven by user research, paved-road UX) that's
supposed to come with it. Data lags furthest: data mesh, the movement that first argued data
should be treated as a product, reached only "hard-won maturity" by 2026, and many declared
"data domains" turned out to be lip service rather than genuine, accountable ownership
([Thoughtworks](https://www.thoughtworks.com/insights/blog/data-strategy/the-state-of-data-mesh-in-2026-from-hype-to-hard-won-maturity)).
So the realistic 2029 claim is not "data platforms become product teams" — that box is
already checked on paper — it's whether *data* products specifically reach the rigor general
platform engineering already claims: discoverable catalogs, producer accountability, contracts
that are enforced rather than aspirational. Whether that closes by 2029 is itself uncertain: it
was already "a few years out" once, in the original 2019 data-mesh telling, and missed.

**Ownership splits from enablement — but where the line sits stays as contested in 2029 as it is
today.** The mainstream pattern is a central platform/CoE that *enables*, with domains that
*own* their data products — the federated middle ground. But data mesh reached its current state
largely by re-centralizing the platform while decentralizing ownership (§1.5), and centralized,
decentralized and federated models all coexist in 2026 and likely still will in 2029
([McKinsey](https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/charting-a-path-to-the-data-and-ai-driven-enterprise-of-2030)).
Unlike the product-label question above, this one genuinely isn't settling — it's the
operating-model axis to keep *reversible*, not the one to bet a target-state design on.

**The unit of collaboration shifts from ticket to contract — from pocket adoption today to the
default by 2029.** Data contracts already exist in scattered, team-by-team form now; the
2026→2029 move is from that patchwork to contracts as the *default* producer/consumer interface
— schema, freshness and quality guarantees enforced in the pipeline rather than discovered
downstream ([Chad Sanderson](https://dataproducts.substack.com/p/the-consumer-defined-data-contract)).
That shift is also what would let the "data domains" above stop being lip service: an
unenforced contract is just documentation, and it's the enforcement, not the paperwork, that's
still rare today. Contracts are also described as the prerequisite for trustworthy,
production-grade AI, tying this operating-model change directly to the §1.1 AI demand force —
which is a real reason to expect the adoption curve to steepen rather than stay flat.

**Roles and skills shift from plumbing to meaning and governance — plus one function that
genuinely doesn't exist yet in most organizations: supervising agents.** As ingestion and
transformation automate and shift left, scarce human effort moves up the stack: semantic and
analytics-engineering work (modeling-as-code), data product management, and governance/lineage
stewardship are already emerging roles today, not 2029 novelties. *Supervising agents* that read
and act on the platform is different — it has no real incumbent in most 2026 org charts, which is
what makes it the one item on this list that is an actual forward change rather than a maturing
of something already underway. The single most-desired emerging skill reported across
organizations is **AI cost management**, reflecting both the growth of AI spend and the
difficulty of allocating it ([State of FinOps](https://www.finops.org/framework/scope/finops-for-data-cloud-platforms/))
— itself a symptom of a role gap that's open now and plausibly closes by 2029, not one that's
already closed.

**A second audience joins every interaction: the reviewer and the regulator — moving from
bolted-on to designed-in, and spreading beyond financial services.** The *audience* isn't new:
BCBS 239 and DORA already force this in FS today. What's not yet arrived is the *design
posture* — building for the auditor from the outset (lineage, reasoning traces, source
attribution, action logs as first-class artifacts) rather than retrofitting compliance after
the fact, and that posture generalizing past FS into other regulated sectors as agentic access
broadens (§2.5). Frameworks like EDM Council's DCAM give teams a shared maturity language for
"where the platform must be" — a useful yardstick precisely because most platforms aren't there
yet.

## Takeaways

- **There is no single "2029 data platform."** Any source promising one is selling something.
  Plan for a *band* of outcomes and keep the four contested axes — agent autonomy, ownership
  locus, open-formats-vs-consolidated-vendors, single-node-vs-scale-out — reversible rather than
  bet on one.
- **The centre of gravity moves to the data layer.** Open table formats, immutable and
  versioned assets, and governance and meaning enforced *where the data lives* — this is the
  one pattern robust across independent signals, because AI-readiness and regulation demand it
  separately. It is the closest thing to a safe bet in the study. *The asterisk: immutability owes
  a deletion debt — git-for-data without an erasure path is an audit asset and a privacy liability
  at once (§2.4).*
- **The interface shifts from tables to business meaning.** A governed semantic layer — trending
  toward knowledge graphs — becomes the primary surface, with modeling left plural beneath it
  (Data Vault for audit, wide tables for AI, dimensional where it fits). "No metadata, no AI."
- **AI is the demand driver, but the data foundation is the throttle — and regulation only
  tightens.** Both reward the *same* investments (lineage, immutability, governance, real-time
  context), which is why those investments are low-regret even under deep uncertainty.
- **The product label already won; product rigor for data — and ownership — haven't.** Platform-
  as-product passed 80% adoption in 2026, so don't mistake the label for the change. What's
  actually still open through 2029 is whether *data* products reach the same rigor (measured
  SLOs, discoverable catalogs, enforced contracts, accountable producers) general platform
  engineering already claims, plus where ownership ends up sitting. Culture and adoption, not
  tooling, decide whether any of this delivers.
- **In financial services, the contested becomes settled.** Immutability, lineage, residency and
  resilience are non-negotiable architectural constraints (BCBS 239, DORA, LGPD) — the regulated
  case is less a different platform than the general one with its optional parts made mandatory.

## References

Grouped by the role each source plays in the study. Each entry has a link, a brief
explanation, the contribution it makes, and — where it applies — a caveat on fit.
*Links checked June 2026. Vendor materials are cited for design patterns and market
signals, not as endorsements. Analyst reports behind paywalls (McKinsey, Gartner) are
cited from their public abstracts/landing pages — read the primary before quoting figures.*
<!-- This is the working source shortlist from the June 2026 research pass; prune and
promote into the body as sections §1–§3 are written. -->

### Forces & market signal

- **Charting a path to the data- and AI-driven enterprise of 2030 — McKinsey** ([mckinsey.com](https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/charting-a-path-to-the-data-and-ai-driven-enterprise-of-2030))
  — the single most on-point source: a named end-state vision for the data/AI enterprise
  at the end of this decade, with the centralized vs. decentralized vs. federated
  architecture split. *Supports:* the §2 2029 reference picture and the §1 framing.
  *Caveat:* scraper-blocked; URL confirmed via McKinsey's own index, read in-browser.
- **Building the foundations for agentic AI at scale — McKinsey** ([mckinsey.com](https://www.mckinsey.com/capabilities/mckinsey-technology/our-insights/building-the-foundations-for-agentic-ai-at-scale))
  — eight in ten companies cite *data limitations* as the roadblock to scaling agents;
  the data foundation is the binding constraint. *Supports:* the §1 "forces" argument
  that AI demand is pulling the platform forward. *Caveat:* same source as the agentic
  study — reused deliberately as the load-bearing market signal.
- **Rethinking enterprise architecture for the agentic era — McKinsey** ([mckinsey.com](https://www.mckinsey.com/capabilities/mckinsey-technology/our-insights/rethinking-enterprise-architecture-for-the-agentic-era))
  — argues infrastructure must become modular and "mesh-like," with agents/tools/systems
  joined through a shared orchestration layer. *Supports:* the §1 driver "agentic
  consumption reshapes architecture" and the §3 operating-model shift.
- **Over 100 Data, Analytics and AI Predictions Through 2030 — Gartner (compendium PDF)** ([agatadata.com mirror](https://agatadata.com/wp-content/uploads/2024/11/Over-100-data-analytics-and-ai-predictions-through-2030-2024-Gartner.pdf))
  — a dated, quotable set of Gartner strategic-planning assumptions through 2030.
  *Supports:* the §1 forces table (confidence/horizon per trend). *Caveat:* hosted on a
  third-party mirror — verify each assumption against the originating Gartner note.
- **Experts Give 8 Big Data Predictions for 2026 — Database Trends & Applications** ([dbta.com](https://www.dbta.com/Editorial/News-Flashes/Experts-Give-8-Big-Data-Predictions-for-2026-172655.aspx))
  — a near-term practitioner-press read on where platforms head next. *Supports:* the §1
  near-term forces. *Caveat:* aggregated vendor commentary — directional, not primary.
- **Lack of AI-Ready Data Puts AI Projects at Risk — Gartner (press release)** ([gartner.com](https://www.gartner.com/en/newsroom/press-releases/2025-02-26-lack-of-ai-ready-data-puts-ai-projects-at-risk))
  — **primary** Gartner source for the Context reality-check: 60% of AI projects abandoned
  through 2026 without AI-ready data; 63% of orgs lack/are unsure of AI-ready data practices
  (Q3 2024 survey, n=248). *Supports:* the Context "data is the binding constraint, hype
  outruns value" framing — a deliberate counterweight to the optimistic vendor sources.
- **Worldwide IDC Global DataSphere Forecast, 2025–2029 — IDC** ([idc.com](https://my.idc.com/getdoc.jsp?containerId=US53363625))
  — the canonical data-growth forecast (total creation rising steeply, unstructured fastest).
  *Supports:* the Context tension — data keeps growing *and* most workloads stay small; both
  the IDC and DuckDB pictures hold at once. *Caveat:* paywalled landing page; the headline
  trend is public, the precise 2029 figures require the report.
- **What engineering leaders get wrong about data-stack consolidation — The New Stack** ([thenewstack.io](https://thenewstack.io/data-stack-consolidation-risks/))
  — an **independent** (non-vendor) counter-signal: as the stack consolidates into a few
  vendors, "neutrality erodes" and lock-in shifts rather than disappears. *Supports:* the
  Context "open formats vs. consolidated vendors is contested" point — included specifically to
  balance the open-source/composable optimism elsewhere in the set.
- **FinOps for Data Cloud Platforms — FinOps Foundation** ([finops.org](https://www.finops.org/framework/scope/finops-for-data-cloud-platforms/))
  — the practitioner-standard scope for governing data-cloud spend, shifting FinOps from
  after-the-fact reporting toward shaping spend before it happens. *Supports:* the §1.3 cost
  force. *Caveat:* the canonical *State of FinOps 2026* report (data.finops.org) blocks
  automated fetch — pull its figures manually before quoting.

### Architecture & the 2029 platform

- **The next era of the open lakehouse: Apache Iceberg™ v3 in Public Preview — Databricks** ([databricks.com](https://www.databricks.com/blog/next-era-open-lakehouse-apache-icebergtm-v3-public-preview-databricks))
  — (Apr 2026) row lineage, deletion vectors, the VARIANT type, and Delta↔Iceberg
  convergence via UniForm "write-once, read-anywhere." *Supports:* the §2 storage/table-
  format layer — the open-format convergence likely settled by 2029. *Caveat:* vendor
  framing of an open standard; corroborate with the Iceberg spec.
- **Apache Iceberg v4 Roadmap: Adaptive Metadata, Single-File Commits, the Delta Convergence — Alex Merced** ([iceberglakehouse.com](https://iceberglakehouse.com/posts/apache-iceberg-v4-roadmap-adaptive-metadata-delta-convergence/))
  — the forward roadmap beyond v3, including the stated v4/Delta-5 metadata unification.
  *Supports:* the §2 trajectory of where table formats land by 2029. *Caveat:* practitioner
  blog tracking a moving roadmap — treat dates as provisional.
- **The Lost Decade of Small Data? — DuckDB** ([duckdb.org](https://duckdb.org/2025/05/19/the-lost-decade-of-small-data))
  — median warehouse scan ~100 MB and 99.9-pct reads <300 GB; argues "99% of useful
  datasets" fit a single node ("data singularity"). *Supports:* the §2 counter-current to
  scale-out — single-node/decoupled compute as a real 2029 design point. *Caveat:* authored
  by the engine's vendor; independently corroborated below by Amazon's Redshift-fleet study
  and the Snowset Snowflake trace — vendors with no single-node engine to sell.
- **Separating Storage and Compute in DuckDB — MotherDuck** ([motherduck.com](https://motherduck.com/blog/separating-storage-compute-duckdb/))
  — the architectural pattern that lets single-node engines scale via the cloud when
  needed. *Supports:* the §2 "decoupled compute" point. *Caveat:* vendor (a16z-backed) —
  cited for the pattern, not the product.
- **Top Trends for Data Streaming with Kafka and Flink in 2026 — Kai Waehner** ([kai-waehner.de](https://www.kai-waehner.de/blog/2025/12/10/top-trends-for-data-streaming-with-apache-kafka-and-flink-in-2026/))
  — diskless Kafka + Iceberg, analytics shifting into the stream layer, and agentic AI fed
  by real-time context over MCP. *Supports:* the §2 "streaming-first lakehouse" direction.
  *Caveat:* author is a Confluent employee — strong on the streaming view, read alongside
  batch-centric sources.
- **The Agentic Future Demands an Open Semantic Layer — Salesforce** ([salesforce.com](https://www.salesforce.com/blog/agentic-future-demands-open-semantic-layer/))
  — the semantic layer as the governed contract between data and agents. *Supports:* the
  §2 semantic/metrics layer as the 2029 control plane (links to the companion agentic
  study). *Caveat:* vendor positioning around its own stack.
- **Toward Data Systems That Are Business Semantic Centric and AI Agents Assisted — Cecil Pang (arXiv 2506.05520)** ([arxiv.org](https://arxiv.org/abs/2506.05520))
  — the academic anchor: proposes a Business-Semantics-Centric, AI-Agents-Assisted data
  system (BSDS) — curated data linked to business entities, a knowledge base for agents,
  governed pipelines. *Supports:* the §2 thesis that the 2029 platform is organized around
  business meaning, not tables. *Caveat:* a single-author preprint (rev. Mar 2026) — a
  conceptual framework, not empirical.
- **Gartner Active Metadata Management Research Guide (2026) — Atlan summary** ([atlan.com](https://atlan.com/gartner-active-metadata-management/))
  — "no metadata, no AI"; catalogs giving way to metadata-"anywhere" orchestration that
  drives action across the estate. *Supports:* the §2 governance/metadata layer. *Caveat:*
  a vendor's reading of Gartner — go to the Gartner note for the assumptions.
- **Revisiting data architecture for next-gen data products — McKinsey** ([mckinsey.com](https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/tech-forward/revisiting-data-architecture-for-next-gen-data-products))
  — how the reference data architecture is being reworked around reusable data products.
  *Supports:* the §2 layered picture and the §3 product-oriented operating model.
  *Caveat:* scraper-blocked; URL confirmed via McKinsey's index.

- **Building a modern data platform on the lakehouse architecture and cloud-native ecosystem — Discover Applied Sciences (Springer, 2025)** ([link.springer.com](https://link.springer.com/article/10.1007/s42452-025-06545-w))
  — peer-reviewed treatment of running the lakehouse on a **Kubernetes / cloud-native**
  substrate. *Trend:* "platforms over Kubernetes to avoid lock-in." *Supports:* the §2
  infrastructure layer — open, portable, cloud-agnostic deployment. *Lifecycle:* spans
  ingestion→serving on a portable substrate.
- **OKDP — Open Kubernetes Data Platform** ([okdp.io](https://okdp.io/en/))
  — a fully open-source, Kubernetes-native data-platform distribution (v1.0 slated Sep 2026).
  *Trend:* anti-vendor-lock-in / open platform on K8s. *Supports:* the §2 evidence that
  cloud-agnostic, operator-based stacks are productizing by 2029. *Caveat:* early-stage
  project — cited as a directional signal, not a proven standard.
- **BYOC Data Plane Atomicity: a Simpler, Secure Cloud — Redpanda** ([redpanda.com](https://www.redpanda.com/blog/byoc-data-plane-atomicity-secure-cloud))
  — the clearest articulation of **control-plane / data-plane separation**: vendor-managed
  control plane, data plane inside the customer's VPC for sovereignty. *Trend:* control
  planes + BYOC. *Supports:* the §2 deployment-topology shift and the §1 sovereignty force.
  *Caveat:* vendor framing of its own model — cited for the pattern, not the product.
- **The Three Layers of Modern Software Architecture: Control, Data & Management Planes — Pankaj Parashar (Medium)** ([medium.com](https://medium.com/@pankaj-parashar/the-three-layers-of-modern-software-architecture-control-data-and-management-planes-58d3cb2f677a))
  — the **vendor-neutral** articulation of the control/data/management-plane split, paired with
  the Redpanda entry above so the pattern isn't sourced solely from a party that sells it.
  *Supports:* the §2 deployment topology. *Caveat:* a personal essay — used for the neutral
  conceptual framing, not data.
- **Kubernetes Established as the De Facto "Operating System" for AI — 2025 CNCF Annual Survey** ([cncf.io](https://www.cncf.io/announcements/2026/01/20/kubernetes-established-as-the-de-facto-operating-system-for-ai-as-production-use-hits-82-in-2025-cncf-annual-cloud-native-survey/))
  — **neutral, large-sample** evidence (Linux Foundation/CNCF): K8s production use at 82%,
  ~70% running stateful workloads on it, plus the Data-on-Kubernetes Community (DoKC).
  *Supports:* hardens the §2 Kubernetes-substrate claim that otherwise rested on one paper +
  one early project. *Caveat:* survey self-report; "stateful on K8s" ≠ "full platform on K8s."
- **Project Nessie — Transactional Catalog with Git-like Semantics** ([projectnessie.org](https://projectnessie.org/))
  — branches/tags/commits over Iceberg catalogs; references **immutable data files** rather
  than copying them, giving an auditable, time-travelable history. *Trend:* immutable assets
  + "git for data." *Supports:* the §2 catalog layer and the §3/governance audit story (and
  the FS audit-trail need). *Lifecycle:* versioning/governance over immutable storage.
- **lakeFS — Data Version Control for the Data Lake** ([lakefs.io](https://lakefs.io/))
  — turns object storage into a Git-like repo (zero-copy branching of production data).
  *Trend:* immutable assets + git-for-data, at the storage tier rather than the catalog.
  *Supports:* the same §2 point from a complementary angle. *Caveat:* one of two competing
  models (storage-level vs. Nessie's catalog-level) — present both, don't pick a winner.
- **Event Sourcing pattern — Microsoft Azure Architecture Center** ([learn.microsoft.com](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing))
  — the durable, vendor-neutral statement of the **immutability/append-only** principle:
  store every change as an immutable event, derive state. *Trend:* immutable assets (the
  *why*, upstream of the lakehouse). *Supports:* the §2 framing that immutability is a design
  principle the 2029 platform inherits, not just an Iceberg side-effect. *Lifecycle:* ingestion/modeling.
- **Debezium — open-source change data capture** ([debezium.io](https://debezium.io/))
  — the vendor-neutral CDC baseline for the *first mile*: streaming row-level changes off
  operational databases into the platform. *Supports:* the §2.2 point that capture/integration,
  not the processing engine, still dominates platform effort in 2029. *Lifecycle:* ingestion/capture.
- **OWASP Top 10 for LLM Applications — OWASP GenAI Security Project** ([genai.owasp.org](https://genai.owasp.org/))
  — the practitioner reference for LLM/agent risks (prompt injection, excessive agency,
  sensitive-information disclosure). *Supports:* the §2.4 security layer and the agent-as-attack-
  surface point in §2.5 — the threat model that governance framing alone misses. *Caveat:*
  fast-moving project; treat the list as directional. *Lifecycle:* security/consumption.

### Data modeling methodologies

*The methods that produce what the semantic layer serves — the thinnest area in the first
research passes, and decisive for both AI-readiness and FS auditability.*

- **Data Vault 2.0 in the Lakehouse Era — Sendoa Moronta (Towards Data Engineering)** ([medium.com](https://medium.com/towards-data-engineering/data-vault-2-0-in-the-lakehouse-era-advanced-architecture-and-patterns-f1cdab23bf89))
  — insert-only hubs/links/satellites give full historization and audit-grade lineage, applied
  to the lakehouse. *FS relevance:* the dominant modeling method where audit/lineage are
  mandatory (banking, insurance) — directly serves BCBS 239's traceability demands. *Caveat:*
  practitioner blog; the canonical reference is Dan Linstedt's *Building a Scalable Data
  Warehouse with Data Vault 2.0*. *Lifecycle:* modeling/historization.
- **Dimensional Modeling Is Dead? Why Kimball's principles survived — Reliable Data Engineering (Feb 2026)** ([medium.com](https://medium.com/@reliabledataengineering/dimensional-modeling-is-dead-d9f5eea4f18c))
  — the wide-table / One-Big-Table shift: columnar storage rewards denormalization and ML/AI
  prefer flat tables, yet fact-vs-dimension thinking still guides query design. *Supports:* the
  §2 modeling-layer trajectory (from star schema toward wide, AI-consumable tables). *Caveat:*
  opinion piece; pair with Kimball's *The Data Warehouse Toolkit* as the canonical baseline.
- **Ontology-Constrained Neural Reasoning in Enterprise Agentic Systems — arXiv 2604.00555 (2026)** ([arxiv.org](https://arxiv.org/abs/2604.00555))
  — a neurosymbolic architecture where an enterprise **ontology / knowledge graph** grounds and
  validates agent actions (reporting large accuracy gains from KG grounding vs. ungrounded LLMs).
  *Trend:* knowledge-graph / ontology modeling as the 2029 substrate for agentic AI (GraphRAG).
  *Supports:* the §2 thesis that modeling shifts toward business-meaning graphs, not just tables.
  *Caveat:* recent preprint — directional; verify the quoted figures against the primary.
- **How the dbt Semantic Layer works with MetricFlow — dbt Labs** ([getdbt.com](https://www.getdbt.com/blog/how-the-dbt-semantic-layer-works))
  — metrics-as-code: semantic models and metrics defined in version-controlled YAML, compiled to
  SQL on demand. *Trend:* analytics-engineering / modeling-as-code feeding the semantic layer.
  *Supports:* the §2 metrics/semantic layer (the *how it's built*) and the §3 ways-of-working
  shift; version-controlled metric definitions double as FS-grade metric auditability. *Caveat:*
  vendor primary for its own tool — cited for the now-cross-vendor pattern, not the product.
- **From Golden Record to Golden Context: Redefining Master Data for AI Agent Consumption — Tahir Khan (Apr 2026)** ([medium.com](https://medium.com/@Tahir-Khan/from-golden-record-to-golden-context-redefining-master-data-for-ai-agent-consumption-2349eec0840b))
  — **MDM / reference data**, reframed for 2029: the golden record evolves into "golden context"
  agents can consume. *FS relevance:* counterparty, instrument, legal-entity and customer
  mastering is acute in banking (cf. GoldenSource, SIX for FS instrument/security masters);
  entity resolution underpins both BCBS 239 aggregation and AI-readiness. *Supports:* the §2
  modeling layer and §3 governance. *Caveat:* practitioner essay for the forward framing; the
  discipline's authorities are the FS reference-data vendors named above. *Lifecycle:* mastering/entity resolution.

### Engineering canon & systems literature

*Peer-reviewed / primary sources anchoring the architecture claims, so the study does not
rest on vendor forecasts alone.*

- **Lakehouse: A New Generation of Open Platforms… — Zaharia, Ghodsi, Xin, Armbrust (CIDR 2021)** ([cidrdb.org PDF](https://www.cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf))
  — the foundational paper that named and argued the lakehouse: open direct-access formats,
  first-class ML, warehouse-class performance on the lake. *Lifecycle:* storage + modeling +
  serving. *Supports:* the §2 baseline architecture the 2029 state evolves from. *Caveat:*
  authored by Databricks founders — foundational but not disinterested; the durable definition.
- **DuckDB: an Embeddable Analytical Database — Raasveldt & Mühleisen (SIGMOD 2019)** ([duckdb.org PDF](https://duckdb.org/pdf/SIGMOD2019-demo-duckdb.pdf))
  — the peer-reviewed primary behind the in-process / single-node analytics movement
  (replaces the marketing blog as the load-bearing citation). *Lifecycle:* compute/query.
  *Supports:* the §2 "decoupled, single-node compute" design point with academic grounding.
- **Why TPC Is Not Enough: An Analysis of the Amazon Redshift Fleet — van Renen, Saxena, Kraska et al. (VLDB 2024)** ([vldb.org PDF](https://www.vldb.org/pvldb/vol17/p3694-saxena.pdf))
  — Amazon's own operational telemetry from 200 sampled production Redshift instances (the
  public "Redset" trace): a ~2,030x gap between median and 99.9th-percentile query cost, with
  under 0.1% of queries consuming roughly a quarter of all compute. *Lifecycle:* compute/query.
  *Supports:* independent, non-DuckDB confirmation of the §1.3 claim that real analytical
  workloads are extremely skewed toward small and cheap. *Caveat:* still vendor telemetry, but
  peer-reviewed and against Amazon's own scale-out interest — a useful counterweight to the
  DuckDB entry above.
- **Building an Elastic Query Engine on Disaggregated Storage (the "Snowset" trace) — Vuppalapati, Miron, Agarwal, Truong, Motivala, Cruanes (NSDI 2020)** ([usenix.org](https://www.usenix.org/conference/nsdi20/presentation/vuppalapati))
  — 70M real production Snowflake queries over 14 days (Cornell + Snowflake co-authors); a small
  minority of large queries consume nearly half (45.6%) of total CPU time while most queries stay
  small and cheap. *Lifecycle:* compute/query. *Supports:* a second, independent large-scale
  telemetry confirmation of the §1.3 skewed-workload claim, from a different vendor and compute
  model than DuckDB's. *Caveat:* 2018 trace data — directionally durable but worth checking for
  drift against more recent studies.
- **The Composable Data Management System Manifesto — Pedreira, Erling, Karanasos, Wes McKinney et al. (VLDB 2023)** ([vldb.org PDF](https://www.vldb.org/pvldb/vol16/p2679-pedreira.pdf))
  — the missing engineering through-line: decoupling UIs from engines via a shared IR
  (Substrait) and reusable components (Velox, Arrow, DuckDB). *Lifecycle:* spans the stack.
  *Supports:* the §2 thesis that the 2029 platform is *composable* — engines, formats, and
  catalogs interchangeable. The single most important systems-trend source in the set.
- **Data observability vs. data quality… — Monte Carlo** ([montecarlodata.com](https://www.montecarlodata.com/blog-data-testing-vs-data-quality-monitoring-vs-data-observability-whats-right-for-your-team/))
  — the firm that coined "data downtime"; the five-pillar observability frame (freshness,
  volume, distribution, schema, lineage). *Lifecycle:* the quality/observability stage the
  earlier list under-served. *Supports:* the §2/§3 reliability layer. *Caveat:* vendor-origin;
  the durable reference is the O'Reilly book *Data Quality Fundamentals* (Moses et al.).

### Financial-services regulation & standards

*The FS spine — the constraints that turn a generic platform into a banking-grade one. These
are primary/institutional sources, not commentary.*

- **BCBS 239 — Principles for effective risk data aggregation and risk reporting — Basel Committee / BIS** ([bis.org](https://www.bis.org/publ/bcbs239.htm))
  — the defining banking data-platform regulation (14 principles: governance, data
  architecture/infrastructure, aggregation capability, reporting). *FS relevance:* the
  backbone of the §4-companion-study (a future "FS planning" study); dictates lineage,
  accuracy, timeliness, and stress-time aggregation. *Caveat:* applies to G-SIBs/D-SIBs —
  scope to the institution; widely treated as best practice beyond its formal scope.
- **Digital Operational Resilience Act (DORA) — ESMA / EU** ([esma.europa.eu](https://www.esma.europa.eu/esmas-activities/digital-finance-and-innovation/digital-operational-resilience-act-dora))
  — binding EU ICT-risk framework (in force Jan 2025): five pillars incl. third-party/ICT
  concentration risk and resilience testing. *FS relevance:* reshapes data-platform
  resilience, cloud-provider dependency, and incident reporting — an architecture constraint,
  not just policy. *Caveat:* EU scope; map to the equivalent regime per market.
- **DCAM — Data Management Capability Assessment Model — EDM Council** ([edmcouncil.org](https://edmcouncil.org/frameworks/dcam/))
  — the FS-originated global standard for assessing data-management maturity. *FS relevance:*
  the maturity yardstick boards and regulators recognize; a structured way to phrase "where
  the platform must be by 2029."
- **CDMC — Cloud Data Management Capabilities — EDM Council** ([edmcouncil.org](https://edmcouncil.org/frameworks/cdmc/))
  — six components / 14 capabilities / 37 sub-capabilities for governed data in cloud &
  multi-cloud, co-chaired by Morgan Stanley and LSEG. *FS relevance:* directly addresses the
  cloud data-lifecycle controls (classification, protection, residency) the earlier list
  lacked. *Lifecycle:* governance + protection + residency + retention.
- **FINOS — Fintech Open Source Foundation (Linux Foundation)** ([finos.org](https://www.finos.org/))
  — where FS open standards are codified: the Common Domain Model (CDM), FDC3, and RegTech/AI
  initiatives. *FS relevance:* evidence that the 2029 FS platform converges on shared open
  standards rather than bespoke per-bank stacks; the FS analog to the open-format convergence
  in §2.
- **LGPD — Brazil's General Data Protection Law (overview) — DLA Piper, Data Protection Laws of the World** ([dlapiperdataprotection.com](https://www.dlapiperdataprotection.com/index.html?t=law&c=BR))
  — GDPR-aligned regime (in force 2020), enforced by the ANPD, fines up to 2% of revenue; the
  template the rest of LatAm is converging toward. *Relevance:* the regional/privacy layer the
  earlier list lacked — for a LatAm FS footprint, controls map to *each* market's regime, not a
  single framework. Pair with **InCountry's LATAM data-residency guide** ([incountry.com](https://incountry.com/blog/data-residency-requirements-in-latam-brazil-mexico-and-argentina/))
  for Brazil/Mexico/Argentina residency. *Lifecycle:* governance + residency. *Caveat:* law-firm
  /vendor summaries — cite the statute (and ANPD guidance) for anything binding.

### Operating model & people

- **The state of data mesh in 2026: From hype to hard-won maturity — Thoughtworks** ([thoughtworks.com](https://www.thoughtworks.com/insights/blog/data-strategy/the-state-of-data-mesh-in-2026-from-hype-to-hard-won-maturity))
  — (Jan 2026, Werner et al.) data products with AI-ready outputs, central teams evolving
  into enabling CoEs, federated governance as policy-as-code with stakeholder alignment as
  the real bottleneck. *Supports:* the §3 operating-model and ownership trajectory.
- **Data Mesh Principles and Logical Architecture — Zhamak Dehghani / Martin Fowler** ([martinfowler.com](https://martinfowler.com/articles/data-mesh-principles.html))
  — the foundational four-principle definition (domain ownership, data as product,
  self-serve platform, federated governance). *Supports:* the §3 vocabulary and the
  baseline the 2026→2029 maturation is measured against. *Caveat:* 2020 origin — cited as
  the canonical definition, not a current-state read.
- **Platform Engineering Empowers Developers… — Gartner (Top Tech Trends)** ([gartner.com](https://www.gartner.com/en/experts/top-tech-trends-unpacked-series/platform-engineering-empowers-developers))
  — the projection that 80% of large software orgs stand up platform-engineering teams by
  2026, operating the platform as a product. *Supports:* the §1.5/§3 point that the *product
  label* shift is already the present, not a 2029 forecast. *Caveat:* general software-platform
  framing — adapt to the data-platform context; also dates the claim to 2026, which is why §3
  treats it as arrived rather than pending.
- **State of Platform Engineering Report, Volume 4 — platformengineering.org (Jan 2026)** ([platformengineering.org](https://platformengineering.org/reports/state-of-platform-engineering-volume-4))
  — survey of 518 platform engineers: nearly 30% of platform teams report they don't measure
  success at all, even under a stated "platform as product" model. *Supports:* the §1.5/§3
  counterweight to the Gartner adoption headline — the label has outrun the discipline (SLOs
  tied to outcomes, roadmaps driven by user research) it's supposed to imply. *Caveat:*
  self-reported industry survey, not academic; general software platform engineering, not
  data-specific — cited as the closest available proxy for the maturity gap.
- **The Consumer-Defined Data Contract — Chad Sanderson** ([dataproducts.substack.com](https://dataproducts.substack.com/p/the-consumer-defined-data-contract))
  — data contracts as the producer/consumer interface that shifts quality enforcement left.
  *Supports:* the §3 ways-of-working shift (contracts/SLAs as the unit of collaboration, moving
  from pocket adoption today to a default by 2029). *Caveat:* an opinionated practitioner
  newsletter — strong framing, one viewpoint.

### Scenario & forecasting method

- **The state of AI in 2025: Agents, innovation, and transformation — McKinsey (QuantumBlack)** ([mckinsey.com](https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai))
  — the survey baseline for adoption rates and where value is/ isn't being captured.
  *Supports:* calibrating the §1 forces to actual adoption rather than hype. *Caveat:*
  survey self-report; scraper-blocked, read in-browser.
- **Hype Cycle / Planning Guide for Data Management, 2026 — Gartner** ([gartner.com](https://www.gartner.com/en/documents/7001098))
  — positions each capability on the maturity curve, a useful confidence filter for the
  §1 forces table. *Supports:* separating near-certain shifts from contested ones.
  *Caveat:* paywalled; landing page only — figures require the licensed document.
- **Three Decades of Scenario Planning in Shell — Wack / van der Heijden (via ResearchGate)** ([researchgate.net](https://www.researchgate.net/publication/272585648_Three_Decades_of_Scenario_Planning_in_Shell))
  — the methodological backbone: scenario planning builds *multiple plausible narratives* ("what
  could happen?") rather than a single forecast — the Shell/GBN tradition (Pierre Wack, later
  Peter Schwartz's *The Art of the Long View*). *Supports:* the study's own method — it justifies
  framing 2029 as a map of plausible states, not a prediction, and disciplines the §1→§2
  scenario construction. *Caveat:* cite Schwartz's book / van der Heijden's *Scenarios* as the
  canonical primaries; the link is a convenience copy.

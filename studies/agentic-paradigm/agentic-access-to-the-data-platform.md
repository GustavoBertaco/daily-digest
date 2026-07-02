# Agentic Access to the Data Platform

> Emerging usage patterns, governance, and UX for agent-driven access to a data platform.

- **Topic:** Agentic Paradigm
- **Date:** 2026-06-21
- **Status:** draft

> *The words written here are all AI-generated, but all the content was critically reviewed
> and validated by me — the use of AI is to accelerate the knowledge searching and narrative
> building.*

## Contents

1. [Context](#context)
2. [How the usage pattern is changing](#1-how-the-usage-pattern-is-changing)
3. [How platform teams are designing for agentic access](#2-how-platform-teams-are-designing-for-agentic-access)
4. [The user experience of agentic data access](#3-the-user-experience-of-agentic-data-access)
5. [A regulated worked example: banking & financial services](#4-a-regulated-worked-example-banking--financial-services)
6. [Recommendations and a phased roadmap](#5-recommendations-and-a-phased-roadmap)
7. [Takeaways](#takeaways)
8. [References](#references)

## Context

This study explores how **agent-driven access is reshaping the data platform** — as
data consumers increasingly reach the platform through autonomous and semi-autonomous
agents rather than through dashboards, notebooks, and hand-written SQL. The central
question: how is the usage pattern changing, what risk does ungoverned agentic access
open, and how should platform teams design the architecture, governance, and user
experience around it — so that faster time-to-insight does not come at the cost of
correctness, attribution, and control?

This is not fringe behavior. Agent deployment nearly quadrupled across enterprises
during 2025 ([KPMG Q3 2025 Pulse](https://kpmg.com/us/en/articles/2025/ai-quarterly-pulse-survey.html):
42% had deployed agents, up from 11% two quarters earlier), and adoption runs ahead of
that in regulated, data-rich sectors — roughly one in five financial-services
organizations had already deployed agentic AI by early 2026
([Banking Dive / NVIDIA](https://www.bankingdive.com/spons/going-from-good-to-great-with-ai-agents-in-banking/818277/)). The appeal is real: a well-designed agent resolves a business question into a
governed query in seconds and lowers the skill barrier for non-technical staff. But the
same autonomy bypasses the platform's founding assumptions — that a *known human*, with
a *known role*, runs a query they *personally wrote*. Agents break all three at once.

**The central finding.** The market consensus is that agentic access is governed at the
**data layer, not the model layer**, and mediated through a **semantic layer** rather
than raw tables. Teams that expose raw SQL to agents report failures; teams that expose
governed, intent-shaped capabilities are scaling. For any data platform — and most
acutely where data is sensitive or regulated — the semantic layer plus a non-human
identity model is the controlling architecture decision.

**Five takeaways for the platform roadmap:**

1. **Treat agents as first-class identities.** Service accounts and human SSO were
   not designed for ephemeral actors that chain calls across systems. Non-human
   identities already outnumber humans by 40:1 to 100:1 in some enterprises
   ([Singh](https://medium.com/@raktims2210/ai-agent-identity-zero-trust-the-2026-playbook-for-securing-autonomous-systems-in-banks-e545d077fdff);
   [BankInfoSecurity](https://www.bankinfosecurity.com/agentic-ai-redefines-identity-security-a-31253)),
   and need their own lifecycle, least-privilege, and audit primitives.
2. **Govern at the data layer.** Data governance is now framed as the prerequisite
   for AI governance — risk originates where sensitive data enters the pipeline, not
   at the output ([BigID](https://bigid.com/blog/agentic-ai-governance-trends/)).
3. **Route agents through a semantic layer.** Direct NL-to-SQL against raw tables is
   the leading predicted cause of failed agentic analytics projects
   ([Redpanda / Gartner](https://www.redpanda.com/blog/5-predictions-about-agentic-ai-and-analytics-in-2026)).
   A governed semantic contract keeps answers correct and policy-compliant.
4. **Design the experience for supervision, not just speed.** Progressive delegation,
   confidence signals, reasoning transparency, and override controls convert raw
   agent capability into something a user and an auditor can trust
   ([Fuse Lab Creative](https://fuselabcreative.com/ui-design-for-ai-agents/);
   [Agentic Design](https://agentic-design.ai/patterns/ui-ux-patterns)).
5. **Instrument for observability from day one.** Separate, tamper-evident logging of
   agent actions is becoming a regulatory expectation (EU AI Act, NIST AI RMF)
   ([BigID](https://bigid.com/blog/agentic-ai-governance-trends/)) and — in regulated
   sectors — a precondition for Know-Your-Agent supervision
   ([IMF](https://www.imf.org/en/publications/imf-notes/issues/2026/04/22/how-agentic-ai-will-reshape-payments-575560)).

## 1. How the usage pattern is changing

**1.1 From human-in-the-loop queries to agent-mediated access.** Traditional usage is
interactive and human-paced. Agentic usage inverts several properties: agents operate
continuously, ingest and act far faster than a human, decompose one business question
into many sub-queries, and may act on behalf of a group rather than a named
individual. Expected changes in platform telemetry:

- **Query volume and burstiness rise** — one question fans out into entity
  resolution, metric logic, date filtering, and multiple joins as separate executions.
- **Access becomes less predictable** — agents chain actions across systems and
  escalate scope within seconds, unlike human sessions.
- **The actor becomes ambiguous** — a query may run under a service identity on behalf
  of a user or team, breaking one-user-one-query auditing.
- **Exploration replaces reporting** — most self-service users shift ad-hoc and
  exploratory work to LLM-driven interfaces, while production reporting stays on
  traditional BI ([Redpanda / Gartner](https://www.redpanda.com/blog/5-predictions-about-agentic-ai-and-analytics-in-2026)).

**1.2 Why this is happening now — and why it stalls.** Several forces pulled adoption
up fast. *Standardization* arrived — the Model Context Protocol (introduced late 2024,
now stewarded under the Linux Foundation
([Colrows](https://colrows.com/blogs/mcp-semantic-layer-integration/))) gave agents a
common way to discover and invoke governed capabilities, with major data platforms
shipping MCP servers ([Techstrong.ai](https://techstrong.ai/features/microsoft-brings-sql-to-the-agentic-era-with-sql-mcp-server/)).
And the *economic promise* is real — faster time-to-insight and a lower technical
barrier are what pull teams in. The result: deployment nearly quadrupled in 2025
([KPMG](https://kpmg.com/us/en/articles/2025/ai-quarterly-pulse-survey.html)), though
most organizations only experimented — fewer than 10% scaled to tangible value.

*But the realized economics are not yet favorable, and the pullback is visible.* The
promise on paper has not shown up in returns, and the counter-current is now well
documented. Gartner predicts that **over 40% of agentic AI projects will be canceled by
the end of 2027**, citing escalating costs, unclear business value, and inadequate risk
controls ([Gartner](https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027)).
Roughly three-quarters of enterprises have already rolled back or shut down a deployed
AI agent — and, tellingly, that rate is *higher* (~81%) among organizations with mature
governance, i.e. those measuring honestly ([Sinch, via CX Dive](https://www.customerexperiencedive.com/news/why-three-quarters-of-enterprises-have-rolled-back-ai-agents/821140/)).
The broader backdrop is MIT's finding that ~95% of generative-AI pilots deliver no
measurable P&L impact ([MIT NANDA, via Fortune](https://fortune.com/2025/08/18/mit-report-95-percent-generative-ai-pilots-at-companies-failing-cfo/)),
and Forrester's expectation that ~25% of 2026 AI spend slips to 2027 as CFOs press for
ROI ([TechTarget](https://www.techtarget.com/searchdatamanagement/feature/How-agentic-AI-governance-tackles-data-security-challenges)).

*Why so many stall:* [McKinsey](https://www.mckinsey.com/capabilities/mckinsey-technology/our-insights/building-the-foundations-for-agentic-ai-at-scale)
attributes the gap primarily to shaky data foundations — eight in ten companies cite
data limitations as the roadblock. Read together, the signals point one way: agentic
access is not a fad — adoption is real and rising — but *value is gated, and the gate is
the data foundation and governance, not the model*. That is precisely why the platform
team owns much of the upside, and why the economics turn favorable only after the
controlling layers in Section 2 are in place.

**1.3 The risk surface this opens.**

| Risk | Why agents amplify it | Consequence |
| --- | --- | --- |
| Over-permissioning | Agents are often granted broad access without oversight; access now defines both their value and their risk. | Excess standing access to customer and transaction data. |
| Loss of attribution | Ephemeral agents acting for groups break one-user-one-action audit trails. | Inability to answer who accessed what, for which purpose. |
| Shadow AI | Unsanctioned agents operate outside IT oversight. | Ungoverned data egress; regulatory exposure. |
| Incorrect answers at scale | NL-to-SQL on raw tables yields plausible but wrong results. | Ungoverned decisions causing financial or reputational loss. |
| Continuous scope drift | Agents gain new permissions and data sources between audit cycles. | Periodic audits miss real-time privilege escalation. |

A blunt field framing: agents lack human judgment — if they encounter data they
should not have, they will use it rather than report it. Wherever data is sensitive,
that makes least-privilege and data-layer enforcement non-negotiable rather than
aspirational.

## 2. How platform teams are designing for agentic access

A fairly consistent four-layer reference architecture is emerging. Sequencing is
deliberate: define scope and policy first, then build the controlling layers, then
expand autonomy as trust is demonstrated.

**2.1 The semantic layer as the control plane.** The strongest cross-source consensus:
agents should query governed business meaning — metrics, entities, join paths,
policies — rather than raw tables
([Coalesce](https://coalesce.io/data-insights/semantic-layers-2025-catalog-owner-data-leader-playbook/)).
The agent resolves a question into semantic intent, and a query engine constructs SQL
from the governed model as the source of truth
([ThoughtSpot](https://www.thoughtspot.com/data-trends/agentic-semantic-layer)). This
keeps an agent from guessing which column represents churn, revenue, or a delinquent
account.

*Sharpest market signal:* analysts predict a majority of agentic analytics projects
relying on the protocol layer alone, without a consistent semantic layer, will fail
([Redpanda / Gartner](https://www.redpanda.com/blog/5-predictions-about-agentic-ai-and-analytics-in-2026)
put it at ~60%). The protocol moves the request; the semantic layer makes the answer
correct and
compliant. It is also where contested definitions — "active customer," "revenue,"
"eligible account" (or, in a regulated domain, "exposure," "default") — are pinned
down once and enforced everywhere.

*Practical pattern:* expose a small set of intent-shaped tools (e.g. `query_metric`,
`get_entities`, `validate_join`, `list_metrics`) rather than one tool per metric or a
single run-SQL tool ([Colrows](https://colrows.com/blogs/mcp-semantic-layer-integration/)).
Fewer, intent-shaped tools measurably improve tool-selection accuracy and shrink the
attack surface.

**2.2 Identity: treat the agent as a first-class actor.** The Coalition for Secure AI
published an Agentic Identity and Access Management framework (March 2026) whose first
principle is that agents are first-class identities — not humans, not traditional
service accounts ([CoSAI, via Resilient Cyber](https://www.resilientcyber.io/p/identity-is-the-agentic-ai-problem)).
Converging controls:

- Inventory every agent and machine identity before buying tooling.
- Enforce least-privilege and just-in-time access rather than standing broad grants
  ([BankInfoSecurity](https://www.bankinfosecurity.com/agentic-ai-redefines-identity-security-a-31253)).
- Add guardrails at the tool and API layer, not only inside the model.
- Keep dedicated, tamper-evident logs of agent actions, separate from human logs.
- Plan for Know-Your-Agent: verifiable agent identities linked to a legal entity.

**2.3 Governance: shift left to the data, enforce in real time.** Move governance from
a downstream, periodic activity to a real-time, data-layer one. Data governance is the
prerequisite for AI governance ([BigID](https://bigid.com/blog/agentic-ai-governance-trends/));
real-time monitoring replaces periodic audits because agents gain permissions between
cycles; governance increasingly behaves as an event-driven orchestration layer
integrating catalogs, warehouses, IAM, and BI rather than a standalone gate
([OvalEdge](https://www.ovaledge.com/blog/agentic-data-governance);
[Acceldata](https://www.acceldata.io/blog/what-enables-agentic-ai-to-move-from-detection-to-governance-enforcement)).
Deloitte's prescription for high-assurance environments: agent control rooms, real-time
auditing, action logging, human oversight, and kill switches with human override
([Deloitte](https://www.deloitte.com/us/en/insights/topics/emerging-technologies/ai-agents-scaling-faster.html)).
Forrester frames the moment as governance entering its agentic era
([Forrester](https://www.forrester.com/blogs/the-forrester-wave-data-governance-solutions-q3-2025-shows-that-governance-entered-the-agentic-era/))
— a "hard hat" phase where cost control, reliability, and governance matter more than
demos ([TechTarget](https://www.techtarget.com/searchdatamanagement/feature/How-agentic-AI-governance-tackles-data-security-challenges)).

**2.4 Observability: you cannot govern what you cannot see.** Full traceability of an
agent's actions, tool access, data access, and the identity it acts for is becoming a
regulatory expectation (EU AI Act, NIST AI RMF)
([BigID](https://bigid.com/blog/agentic-ai-governance-trends/)). A practical near-term
approach: dedicated agent logging combined with anomaly detection — agents watching
agents — because agent activity exceeds human review capacity
([Acceldata](https://www.acceldata.io/blog/what-enables-agentic-ai-to-move-from-detection-to-governance-enforcement)).

| Layer | Design decision | What good looks like |
| --- | --- | --- |
| Semantic | Agents query governed meaning, not raw tables. | Intent-shaped tools over a governed metric/entity model. |
| Identity | Agents are first-class non-human identities. | Inventory, least-privilege, JIT, KYA linkage. |
| Governance | Real-time, data-layer, event-driven enforcement. | Control room, action logging, kill switch, human override. |
| Observability | Full, separate, tamper-evident traceability. | Dedicated agent logs plus automated anomaly detection. |

## 3. The user experience of agentic data access

Governance answers whether agentic access is *safe*; UX answers whether it is
*trustworthy and adopted*. In agentic interfaces, trust is earned through visible
control, and control is itself a UX surface. NN/g's State of UX 2026 work identifies
trust as a defining design challenge — users burned by premature AI features resist
later ones, so a poorly governed early rollout carries a lasting adoption cost
([NN/g, via Fuse Lab Creative](https://fuselabcreative.com/ui-design-for-ai-agents/)).

**3.1 Progressive delegation.** The system earns autonomy through demonstrated
reliability rather than demanding it at launch. In one analytics interface, an agent
initially required manual approval for every change; after a run of consecutive
approvals, routine actions moved to auto-execution with notification — and adoption was
higher than versions offering full autonomy from day one
([Optimal Workshop](https://www.optimalworkshop.com/blog/agentic-ai-the-next-frontier)).
This also gives risk and compliance functions a defensible, evidence-based path to
expand agent authority.

**3.2 Supporting UX patterns** ([Agentic Design](https://agentic-design.ai/patterns/ui-ux-patterns);
most relevant to a data platform):

- **Reasoning transparency** — show the steps and semantic definitions used, so an
  analyst sees that "active customer" meant the governed definition.
- **Confidence indicators** — surface uncertainty so users know when to verify.
- **Source attribution** — every answer traces back to the data assets and metrics it
  used, doubling as audit evidence.
- **Override and intervention controls** — mixed-initiative controls and a clear
  stop/kill path for multi-step workflows.
- **Onboarding for correct mental models** — help users understand what the agent can
  and cannot do, to set appropriate reliance.

*Designing for two users at once:* on a governed platform every agentic interaction has
a second audience — the reviewer or auditor. The artifacts that build end-user trust
(reasoning traces, source attribution, confidence signals, action logs) are also the
governance and compliance evidence. Designing them once, for both, avoids bolting on
auditability later.

**3.3 Calibrating autonomy to stakes.** People accept autonomy readily for low-stakes
tasks and demand more control as stakes rise. Tier interactions by data sensitivity
and action irreversibility: exploratory queries over non-sensitive aggregates can be
highly autonomous, while customer-level data or anything triggering a downstream
action routes through approval, masking, or human-in-the-loop review. This mirrors the
event-driven governance model — a request is evaluated on role, purpose, and context,
then granted, denied, masked, or routed for approval
([Acceldata](https://www.acceldata.io/blog/what-enables-agentic-ai-to-move-from-detection-to-governance-enforcement)).

## 4. A regulated worked example: banking & financial services

The patterns in Sections 1–3 are general. This section grounds them in one demanding
setting — a regulated bank — to show how the same principles harden under real
supervisory pressure. Readers in unregulated domains can treat it as a stress test of
the architecture rather than a requirement.

The general patterns get a regulated institution most of the way, but several
considerations are sharper for a bank — sharper still in Latin America, where multiple
national data-protection regimes apply alongside sector supervision.

**4.1 From Know-Your-Customer to Know-Your-Agent.** An IMF note on agentic AI in
payments frames an emerging supervisory shift toward Know-Your-Agent, with mandated
verifiable identities for financial bots linked to legal entities. It proposes a
three-layer lens of *intent, authorization, and settlement*
([IMF](https://www.imf.org/en/publications/imf-notes/issues/2026/04/22/how-agentic-ai-will-reshape-payments-575560)).
Traditional fraud models, built on human behavioral patterns, lose power when
transactions originate from autonomous agents — a direct concern for a bank's data and
risk platforms ([PYMNTS](https://www.pymnts.com/cybersecurity/2026/agentic-ai-pushes-banks-to-fix-security-data-and-decision-rights/)).

**4.2 Governance by design, mapped to regulation.** The literature converges on
governance-by-design: embedding identity safeguards, provenance verification, and
policy-based access control directly into the system so regulation becomes a
system-level enabler rather than a manual overlay. Solutions are expected to be
designed against applicable regimes (GDPR, OCC, MAS, ISO, among others) — for this
footprint, mapping controls to each market's data-protection law and banking
supervisor rather than a single framework.

**4.3 The build-versus-scale gap.** Early agentic wins in banking do not equal scaled
success, and the gap that appears at scale is governance
([TechTarget](https://www.techtarget.com/searchdatamanagement/feature/How-agentic-AI-governance-tackles-data-security-challenges)).
The recommended sequence is design-first: classify scope and risk before selecting
tooling. Organizations that buy
governance platforms before defining what they need to govern end up with expensive
shelfware; those that write policy without monitoring infrastructure end up with
unenforceable rules.

## 5. Recommendations and a phased roadmap

Deliberately design-first, for any platform team already seeing agentic traffic rise.
The regulated-sector steps (Phase 4) apply where supervision demands them; everything
before is general.

**Phase 1 — See and scope (now)**
- Instrument telemetry to distinguish agent- from human-originated access; quantify
  volume, fan-out, and data domains.
- Inventory existing agents and machine identities touching the platform, including
  unsanctioned ones (shadow AI).
- Classify data domains and actions by sensitivity and irreversibility to create the
  tiering later phases enforce.

**Phase 2 — Build the controlling layers**
- Stand up or extend a governed semantic layer and require agents to query through it;
  begin with the top metrics and entities, not the whole model.
- Expose a small set of intent-shaped capabilities (via MCP or equivalent) instead of
  a raw-SQL tool.
- Implement first-class agent identity with least-privilege and JIT access; separate
  agent action logs from human logs.
- Add event-driven access evaluation that can grant, deny, mask, or route for approval
  based on role, purpose, and context.

**Phase 3 — Make it trustworthy and supervised**
- Ship the UX trust layer: reasoning transparency, confidence indicators, source
  attribution, and override/kill controls.
- Stand up an agent control room with real-time auditing, anomaly detection, and human
  override.
- Adopt progressive delegation so autonomy expands from an evidence base.

**Phase 4 — Scale and align to regulation** *(where applicable)*
- Map controls to each market's data-protection law and sector regulator (for a bank,
  the banking supervisor); prepare for Know-Your-Agent with verifiable, entity-linked
  agent identities.
- Move governance from periodic audit to continuous monitoring as agent scope drifts.
- Treat the data foundation itself as the scaling constraint — the most-cited reason
  agentic programs stall.

## Takeaways

- **One decision orders the rest:** agents reach data only through a *governed
  semantic layer*, under a *first-class non-human identity*, with *every action logged
  separately*. Nearly every other recommendation enables or depends on this.
- Govern at the **data layer, not the model layer**; the semantic layer is the control
  plane that keeps answers correct and policy-compliant.
- The binding constraint on scaling agentic value is the **data foundation itself** —
  which is why the platform team owns the upside.
- In agentic UX, **trust is earned through visible control**; the same artifacts that
  build user trust are the compliance evidence an auditor needs.
- In regulated or sensitive-data environments, **least-privilege, real-time
  enforcement, and separate tamper-evident logging** are non-negotiable — and, for
  banks specifically, the supervisory frame is shifting from Know-Your-Customer toward
  Know-Your-Agent.

## References

Grouped by the role each source plays in the study. Each entry has a (validated) link,
a brief explanation, the contribution it makes to the study, and — where it applies — a
caveat on fit. *All links checked June 2026; vendor materials are cited for design
patterns and market signals, not as endorsements.*

### Adoption & market signal

- **Building the foundations for agentic AI at scale — McKinsey** ([mckinsey.com](https://www.mckinsey.com/capabilities/mckinsey-technology/our-insights/building-the-foundations-for-agentic-ai-at-scale))
  — fewer than 10% of enterprises have scaled agents to tangible value, and eight in
  ten cite *data limitations* as the roadblock; lays out data-architecture principles
  (treat ingestion as a product, share meaning not just data, trust by default).
  *Supports:* the §1.2 "why fewer than 10% scale" finding and the framing that the data
  platform itself is the binding constraint — the source the central thesis rests on.

- **How agentic AI governance tackles data, security challenges — TechTarget** ([techtarget.com](https://www.techtarget.com/searchdatamanagement/feature/How-agentic-AI-governance-tackles-data-security-challenges))
  — carries Forrester's "hard hat" phase (governance/reliability over demos; ~25% of
  2026 AI spend slips to 2027) and Deloitte's survey (74% plan agentic deployment, only
  21% have a mature governance model).
  *Supports:* the §1/§2 framing that the moment is about foundations, and the
  build-vs-scale gap in §4.3.

- **Agentic AI in Financial Services: A Research Roundup for 2026 — Neurons Lab** ([neurons-lab.com](https://neurons-lab.com/articles/agentic-ai-in-financial-services-2026/))
  — aggregates Deloitte/McKinsey/KPMG/EY figures (e.g. 99% plan to put agents in
  production, ~11% have).
  *Supports:* the adoption-vs-scaling gap in §1.2. *Caveat:* a secondary roundup —
  figures inherit the primary sources' definitions; cited for the consolidated signal,
  not as origin.

- **Going from good to great with AI agents in banking — Banking Dive / NVIDIA** ([bankingdive.com](https://www.bankingdive.com/spons/going-from-good-to-great-with-ai-agents-in-banking/818277/))
  — NVIDIA's State of AI in Financial Services 2026 (800+ respondents): ~21% have
  deployed agents, BFSI leads cross-industry on mainstreaming them.
  *Supports:* the Context "roughly one in five FS organizations" adoption figure.
  *Caveat:* sponsored post summarizing a vendor survey — treat the number as directional.

- **AI Quarterly Pulse Survey, Q3 2025 — KPMG** ([kpmg.com](https://kpmg.com/us/en/articles/2025/ai-quarterly-pulse-survey.html))
  — 42% of organizations had deployed at least some agents, up from 11% two quarters
  earlier — the basis for "deployment nearly quadrupled in 2025."
  *Supports:* the Context and §1.2 "nearly quadrupled" adoption figure. *Caveat:* a
  rolling pulse survey; the quarter-over-quarter base shifts, so read it as momentum,
  not a precise multiple.

- **Over 40% of Agentic AI Projects Will Be Canceled by End of 2027 — Gartner** ([gartner.com](https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027))
  — primary press release attributing cancellations to escalating costs, unclear
  business value, and inadequate risk controls; also flags "agent washing."
  *Supports:* the §1.2 counter-current that realized economics are unfavorable.
  *Caveat:* a forward-looking analyst prediction, not measured outcomes.

- **Why three-quarters of enterprises have rolled back AI agents — Sinch / CX Dive** ([customerexperiencedive.com](https://www.customerexperiencedive.com/news/why-three-quarters-of-enterprises-have-rolled-back-ai-agents/821140/))
  — survey finding ~75% of enterprises have rolled back or shut down a deployed agent,
  rising to ~81% among those with mature governance.
  *Supports:* the §1.2 "pullback is visible" evidence. *Caveat:* a single vendor-
  commissioned (Sinch) survey of customer-facing agents — directional, not definitive.

- **MIT report: 95% of generative-AI pilots are failing — MIT NANDA (via Fortune)** ([fortune.com](https://fortune.com/2025/08/18/mit-report-95-percent-generative-ai-pilots-at-companies-failing-cfo/))
  — the NANDA "State of AI in Business 2025" study: ~95% of GenAI pilots show no
  measurable P&L impact (150 interviews, 350-employee survey, 300 public deployments).
  *Supports:* the §1.2 backdrop on weak realized returns. *Caveat:* covers *generative*
  AI broadly, not agentic specifically — cited as context, not as an agentic figure.

### The semantic layer as the control plane

- **5 predictions about agentic AI and analytics in 2026 — Redpanda (Gartner-sourced)** ([redpanda.com](https://www.redpanda.com/blog/5-predictions-about-agentic-ai-and-analytics-in-2026))
  — the headline prediction that ~60% of agentic analytics projects relying on the
  protocol layer (MCP) *alone*, without a consistent semantic layer, will fail; plus the
  exploratory-vs-production split and "25% of ungoverned decisions cause loss."
  *Supports:* the sharpest market signal in §2.1 and the risk table in §1.3. *Caveat:*
  Gartner figures reach the study via a vendor blog; attribution noted, primary report
  is paywalled.

- **What is an Agentic Semantic Layer? — ThoughtSpot** ([thoughtspot.com](https://www.thoughtspot.com/data-trends/agentic-semantic-layer))
  — the agent resolves a question into *semantic intent*, and a query engine constructs
  SQL from the governed model as source of truth, rather than the model emitting SQL
  from a prompt.
  *Supports:* the core §2.1 mechanism (governed meaning over raw tables) almost verbatim.

- **Semantic Layers in 2025: A Catalog Owner and Data Leader Playbook — Coalesce** ([coalesce.io](https://coalesce.io/data-insights/semantic-layers-2025-catalog-owner-data-leader-playbook/))
  — defines the semantic layer (entities, metrics, time logic, row-level policy) and an
  L0–L5 maturity model.
  *Supports:* the §2.1 vocabulary and the §5 "start with top metrics" sequencing.

- **MCP Semantic Layer: Build a Governed MCP Server — Colrows** ([colrows.com](https://colrows.com/blogs/mcp-semantic-layer-integration/))
  — concrete pattern: expose a *small set of intent tools* (`query_metric`,
  `get_entities`, `validate_join`, `list_metrics`) rather than per-metric or run-SQL
  tools; notes MCP is now stewarded under the Linux Foundation.
  *Supports:* the §2.1 "practical pattern" (the exact tool names) and the MCP
  standardization point in §1.2.

- **Microsoft Brings SQL to the Agentic Era With SQL MCP Server — Techstrong.ai** ([techstrong.ai](https://techstrong.ai/features/microsoft-brings-sql-to-the-agentic-era-with-sql-mcp-server/))
  — a shipping vendor example: NL→DAB (not NL→SQL), a fixed small tool set, and RBAC
  applied at the abstraction layer.
  *Supports:* evidence that major platforms are shipping MCP servers (§1.2) and that
  intent-shaped tools + data-layer RBAC is the converging design (§2.1–2.2).

### Identity for non-human actors

- **Identity Is the Agentic AI Problem Nobody Has Solved Yet — Resilient Cyber** ([resilientcyber.io](https://www.resilientcyber.io/p/identity-is-the-agentic-ai-problem))
  — coverage of CoSAI's Agentic IAM framework (March 2026) whose first imperative is
  that agents are *first-class identities*, not humans and not service accounts.
  *Supports:* the §2.2 first pillar — the foundational identity claim and its source.

- **Agentic AI Redefines Identity Security — BankInfoSecurity / GovInfoSecurity** ([bankinfosecurity.com](https://www.bankinfosecurity.com/agentic-ai-redefines-identity-security-a-31253))
  — shift from role-based to intent-based access; machine identities expanding faster
  than visibility; session-based access and guardrails.
  *Supports:* the §2.2 controls (least-privilege, JIT, guardrails at the tool/API layer).
  *Caveat:* a single-vendor RSAC interview (Oasis Security) — directional on practice,
  not a standard.

- **AI Agent Identity & Zero-Trust: The 2026 Playbook for Banks, Telecom, Governments — Raktim Singh (Medium)** ([medium.com](https://medium.com/@raktims2210/ai-agent-identity-zero-trust-the-2026-playbook-for-securing-autonomous-systems-in-banks-e545d077fdff))
  — non-human identities outnumber humans by up to 100:1; treat agents as first-class
  digital employees under zero-trust.
  *Supports:* the Context/§2.2 "40:1–100:1" identity-ratio figure. *Caveat:* a personal
  Medium essay — used for the framing and the widely-repeated ratio, not as primary data.

- **Agentic AI Pushes Banks to Fix Security, Data and Decision Rights — PYMNTS** ([pymnts.com](https://www.pymnts.com/cybersecurity/2026/agentic-ai-pushes-banks-to-fix-security-data-and-decision-rights/))
  — banks must strengthen non-human-identity management and unify cyber strategy before
  agentic value is safe to capture.
  *Supports:* the §4 banking framing that identity and decision-rights are the gating
  controls.

### Governance & observability

- **The Forrester Wave™: Data Governance Solutions, Q3 2025 — Governance Has Entered the Agentic Era — Forrester** ([forrester.com](https://www.forrester.com/blogs/the-forrester-wave-data-governance-solutions-q3-2025-shows-that-governance-entered-the-agentic-era/))
  — governance is now the control plane for trust at scale; leading platforms automate
  policy enforcement and remediation with humans in the loop.
  *Supports:* the §2.3 "governance entering its agentic era" framing and the move from
  static control to real-time enforcement.

- **Emerging Trends in Agentic AI Governance Platforms for 2026 — BigID** ([bigid.com](https://bigid.com/blog/agentic-ai-governance-trends/))
  — six trends converging on *data governance as the foundation for AI governance*;
  cites EU AI Act Art. 10 on data quality/provenance before deployment.
  *Supports:* the Context/§2.3 "govern at the data layer" takeaway and the regulatory
  hook in §2.4.

- **What Is Agentic Data Governance? A Practical Guide for Data Leaders — OvalEdge** ([ovaledge.com](https://www.ovaledge.com/blog/agentic-data-governance))
  — enforce policy at the point of access/share/change in real time, replacing
  retrospective audits.
  *Supports:* the §2.3 shift from periodic audit to real-time, data-layer enforcement.

- **Agentic AI Governance Enforcement: From Detection to Action — Acceldata** ([acceldata.io](https://www.acceldata.io/blog/what-enables-agentic-ai-to-move-from-detection-to-governance-enforcement))
  — worked examples of runtime enforcement (auto-mask a new PII column, pause a broken
  pipeline) with blast-radius reasoning before acting.
  *Supports:* the §2.3 event-driven "grant/deny/mask/route" model and the §3.3
  stakes-calibrated routing.

### User experience & human-AI interaction

- **Agent UX: UI Design for AI Agents in 2026 — Fuse Lab Creative** ([fuselabcreative.com](https://fuselabcreative.com/ui-design-for-ai-agents/))
  — the interface as the *accountability layer*; carries NN/g's State of UX 2026 finding
  that trust is the defining AI-design challenge and that premature AI features poison
  later adoption.
  *Supports:* the §3 opening (trust as a design challenge, lasting adoption cost) and
  the progressive-delegation argument.

- **UI/UX & Human-AI Interaction Patterns — Agentic Design** ([agentic-design.ai](https://agentic-design.ai/patterns/ui-ux-patterns))
  — a catalog of patterns: human-in/on-the-loop, progressive disclosure, reasoning
  transparency, confidence indicators, trust calibration.
  *Supports:* the §3.2 vocabulary of supporting UX patterns.

- **Designing User Experiences for Agentic AI: The Next Frontier — Optimal Workshop** ([optimalworkshop.com](https://www.optimalworkshop.com/blog/agentic-ai-the-next-frontier))
  — progressive disclosure of explanations, audit trails of actions/reasoning, and
  ongoing design-test-refine cycles for learning systems.
  *Supports:* the §3.1 progressive-delegation pattern and the §3.2 reasoning-transparency
  / source-attribution patterns.

### Banking & regulation

- **How Agentic AI Will Reshape Payments — IMF Notes 2026/004** ([imf.org](https://www.imf.org/en/publications/imf-notes/issues/2026/04/22/how-agentic-ai-will-reshape-payments-575560))
  — the Know-Your-Customer → Know-Your-Agent shift, verifiable bot identities linked to
  legal entities, and the *intent / authorization / settlement* three-layer lens that
  keeps probabilistic reasoning upstream of deterministic control.
  *Supports:* the §4.1 KYC→KYA argument and the principle of separating agent reasoning
  from authoritative enforcement (mirrors the §2 data-layer thesis).

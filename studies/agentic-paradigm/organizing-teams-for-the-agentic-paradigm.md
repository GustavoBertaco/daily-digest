# Organizing Teams for the Agentic Paradigm (Toward 2029)

> How team structures, roles, and operating models should evolve as AI agents become
> coworkers rather than tools — a leader's view of the org chart we are building toward 2029,
> tested against the consulting, academic, and engineering evidence.

- **Topic:** Agentic Paradigm
- **Date:** 2026-06-29
- **Status:** draft

## Contents

1. [Context](#context)
2. [The shift: from an org chart of people to an org chart of people and agents](#1-the-shift-from-an-org-chart-of-people-to-an-org-chart-of-people-and-agents)
3. [The new shape: pyramid → diamond (and whether it lasts)](#2-the-new-shape-pyramid--diamond-and-whether-it-lasts)
4. [Team structures for human–agent teams](#3-team-structures-for-humanagent-teams)
5. [New roles and how human work changes](#4-new-roles-and-how-human-work-changes)
6. [The operating model: probabilistic work, oversight, and the centralized/decentralized balance](#5-the-operating-model-probabilistic-work-oversight-and-the-centralizeddecentralized-balance)
7. [What gates the whole thing: the binding constraints](#6-what-gates-the-whole-thing-the-binding-constraints)
8. [A 2026 → 2029 roadmap](#7-a-2026--2029-roadmap)
9. [Takeaways](#takeaways)
10. [References](#references)

## Context

This study began with one AWS re:Invent 2025 keynote — *"A Leader's Guide to Advanced Team
Structures in an Agentic World"* (session **SNR307**, by Stephen Brozovich, Jonathan Allen, and
Richard Davis) — and then deliberately went looking for the *independent* evidence that
supports, qualifies, or contradicts its claims. The talk frames the leadership problem as four
intertwined tensions: managing the *probabilistic* nature of AI through continuous iteration and
intelligent oversight; designing *new cross-functional workflows*; balancing *capability
assessment with agile planning* on top of an organization's own domain expertise and data; and
finding the *right mix of centralized guidance and decentralized innovation*
([AWS / Class Central](https://www.classcentral.com/course/youtube-aws-re-invent-2025-a-leader-s-guide-to-advanced-team-structures-in-an-agentic-world-snr307-508173)).

The animating question for the next three years: **what does the org chart look like when a
two-to-five-person team can supervise fifty-to-a-hundred agents?** This note triangulates the
talk's framing against McKinsey, PwC, BCG, and Bain; against academic work from NBER/SSRN and
arXiv; against the World Economic Forum's 2030 scenarios; and against engineering reality from
Anthropic's production multi-agent system. It is a companion to
[[agentic-access-to-the-data-platform]]: that study covers how agents *reach* the data platform
safely; this one covers how the *humans and agents around it* should be organized.

**The central finding.** The agentic shift is not a tooling upgrade layered onto today's org
chart — it is a change to the org chart itself. The unit of work moves from "a person doing a
task" to "a person *directing a fleet of agents* that do the tasks," which collapses the bottom
of the management pyramid, widens spans of control by an order of magnitude, and makes
**oversight capacity** — not headcount — the binding constraint on how fast an organization can
safely move. The evidence is unusually convergent on this direction, and unusually clear that
the *value* is gated: McKinsey finds the advantage comes from redesigning end-to-end workflows
around agents, not from sprinkling agents onto the existing structure
([McKinsey: Seizing the agentic AI advantage](https://www.mckinsey.com/capabilities/quantumblack/our-insights/seizing-the-agentic-ai-advantage)),
while Gartner expects **over 40% of agentic AI projects to be canceled by end of 2027** for lack
of exactly that structural foundation
([Gartner](https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027)).
The teams that win are not the ones with the most agents; they are the ones whose structure makes
agent output **legible, accountable, and correctable** at the speed agents produce it.

**Five takeaways for the org design:**

1. **Design the team around supervision, not production.** When a small team can run an "agent
   factory" of 50–100 agents for an end-to-end process, the scarce resource is human oversight
   bandwidth, so spans of control must be set by *how much agent output a person can actually
   review*, not by legacy ratios ([McKinsey](https://www.mckinsey.com/capabilities/people-and-organizational-performance/our-insights/the-agentic-organization-contours-of-the-next-paradigm-for-the-ai-era);
   [MIT Sloan Management Review](https://sloanreview.mit.edu/article/agentic-ai-at-scale-redefining-management-for-a-superhuman-workforce/)).
2. **Expect a pyramid-to-diamond shift — but treat its permanence as an open question.** Agents
   absorb entry-level execution, narrowing the junior base and thickening a supervisory middle
   ([PwC](https://www.pwc.com/us/en/tech-effect/ai-analytics/agentic-ai-workforce-redesign.html)).
   The best academic model says the diamond may be a *transitional* state — a short-run junior
   hiring freeze — not a guaranteed steady state, which changes how you should plan talent
   ([Friebel et al., SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6570519)).
3. **Separate intent from execution at the team boundary.** Business-facing teams own *intent*
   and domain context; a platform absorbs *operational responsibility* — the "what / how" split
   that lets non-technical teams produce safely
   ([Team Topologies for agentic platforms](https://blog.owulveryck.info/2026/06/22/who-does-what-team-topologies-for-the-agentic-platform.html)),
   mirroring how Anthropic's lead agent owns planning while subagents own execution
   ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)).
4. **Make a human accountable for every autonomous action.** Agents execute within a bounded
   scope; named humans retain accountability and move *above the loop* — orchestrating outcomes
   rather than performing tasks ([McKinsey](https://www.mckinsey.com/capabilities/people-and-organizational-performance/our-insights/the-agentic-organization-contours-of-the-next-paradigm-for-the-ai-era);
   [MIT Sloan Management Review](https://sloanreview.mit.edu/article/agentic-ai-at-scale-redefining-management-for-a-superhuman-workforce/)).
5. **Centralize the guardrails, decentralize the building.** A hub-and-spoke center of excellence
   industrializes context, guardrails, and tooling as self-service; business units own delivery
   and outcomes — the centralized-guidance / decentralized-innovation balance the AWS talk centers
   on ([CIO](https://www.cio.com/article/4106578/2026-the-year-of-scale-or-fail-in-enterprise-ai.html)).

## 1. The shift: from an org chart of people to an org chart of people and agents

The defining move of the agentic paradigm is that **agents become first-class participants in
the workflow**, not features of a product a person operates. Across the evidence, humans move
*"above the loop"* — from *performing tasks* to *orchestrating outcomes, supervising agents,
setting goals, and managing trade-offs* ([McKinsey](https://www.mckinsey.com/capabilities/people-and-organizational-performance/our-insights/the-agentic-organization-contours-of-the-next-paradigm-for-the-ai-era)).
That single sentence rewrites three assumptions the classic org chart was built on:

- **The unit of work changes.** It was "one person, one task." It becomes "one person, one
  *fleet*." A human team of two to five can already supervise an "agent factory" of 50–100
  specialized agents running an end-to-end process — onboarding a customer, launching a product,
  closing the books ([McKinsey](https://www.mckinsey.com/capabilities/people-and-organizational-performance/our-insights/the-agentic-organization-contours-of-the-next-paradigm-for-the-ai-era)).
- **The manager's job changes.** Management was coordinating *people*; it becomes orchestrating
  *people and agents together*. BCG calls this "managing the machines that manage themselves"
  ([BCG](https://www.bcg.com/publications/2025/machines-that-manage-themselves)); MIT Sloan calls
  it management redefined "for a superhuman workforce"
  ([MIT Sloan Management Review](https://sloanreview.mit.edu/article/agentic-ai-at-scale-redefining-management-for-a-superhuman-workforce/)).
- **The constraint changes.** It was headcount and budget. It becomes **oversight capacity** —
  how much agent-generated work a human can meaningfully review, correct, and stand behind. You
  can spin up a hundred agents in an afternoon; you cannot spin up a hundred people's worth of
  judgment.

**A reality check from production, not slideware.** It is tempting to read "agent factory of
50–100 agents" as costless scale. Anthropic's production multi-agent research system is a useful
corrective on the economics and the limits. Their orchestrator-worker design — a lead agent that
plans and spawns parallel subagents — **outperformed a single agent by 90.2%** on their internal
research eval, but **multi-agent systems use about 15× more tokens than a chat**, so only
high-value work justifies the structure. And the failure modes are organizational, not just
technical: the pattern breaks "in domains requiring all agents to share the same context or
involving heavy interdependencies," LLM agents "are not yet great at coordinating and delegating
to other agents in real time," and **human testers caught behavioral issues that automated evals
missed** ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)). Read
across to the org chart: fleets are expensive, they parallelize *breadth* but not tightly-coupled
work, and they still need a human in the review loop. The agent factory is real — but it is a
*managed* factory, not a free one.

This is why "add agents to the existing teams" fails the way bolting self-service BI onto an
ungoverned warehouse failed: the structure, not the technology, is the bottleneck. McKinsey's
data makes the point bluntly — the agentic advantage comes from **redesigning end-to-end
workflows** and **replacing functional silos with cross-functional, autonomous agentic teams**,
launched as focused "lighthouse" transformations rather than scattered pilots
([McKinsey: Seizing the agentic AI advantage](https://www.mckinsey.com/capabilities/quantumblack/our-insights/seizing-the-agentic-ai-advantage)).
The org has to be redesigned around the new unit of work, which is the subject of the rest of
this note.

## 2. The new shape: pyramid → diamond (and whether it lasts)

The most concrete structural prediction in the literature is a change in the *shape* of the
organization. The traditional pyramid — a wide base of junior staff doing execution, narrowing
through management to a small apex — was a direct consequence of execution being labor-intensive.
Agents make execution cheap, so the base erodes.

PwC's framing is blunt: *no more pyramids*. As agents take on entry-level tasks, the base
narrows and the org tends toward a **diamond** — a small leadership team, a **thick supervisory
middle**, and a **narrow base of new talent**
([PwC](https://www.pwc.com/us/en/tech-effect/ai-analytics/agentic-ai-workforce-redesign.html)).
McKinsey's account agrees on direction, and the World Economic Forum's scenario work points the
same way — toward "humans becoming agent orchestrators" even in its most optimistic
"supercharged progress" future, where AI nonetheless yields a *net* gain of ~78 million jobs
globally by 2030 (≈170M created, ≈92M displaced)
([WEF: Four Futures for Jobs](https://www.weforum.org/stories/2026/01/here-are-four-ways-ais-impact-on-job-markets-might-take-shape/)).

| | **Pyramid (pre-agentic)** | **Diamond (agentic, ~2029)** |
| --- | --- | --- |
| **Base** | Wide — juniors do execution | Narrow — agents do most execution |
| **Middle** | Coordination / people-management | Thick — supervision and orchestration of agent fleets |
| **Apex** | Strategy, small | Strategy + guardrail-setting, small |
| **Scarce resource** | Labor / headcount | Oversight capacity / judgment |
| **Growth lever** | Hire more juniors | Add agents + widen each human's safe span |

**The honest caveat — the diamond may be transitional.** The most careful academic treatment
cautions against assuming the diamond is a permanent steady state. Friebel, Huang, Li, Shukla,
and Zhang model AI as raising individual productivity *and* speeding learning, and find the
resulting shape depends on which effect dominates: for a pure *productivity* shock, firms
**preserve the span in the long run — a pyramid stays a pyramid — but in the short run freeze
junior hiring, temporarily bending the pyramid toward a diamond**; faster-learning effects can
push toward other shapes entirely (the paper's title — *"Pyramids, Diamonds, and
Oscillations"*). The diamond, in other words, may be what a firm looks like *mid-adjustment*, not
forever ([Friebel et al., SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6570519)).
For a leader, the planning implication is sharper than the consultant consensus admits: don't
hard-wire the org around a diamond that might revert — but *do* solve the problem the short-run
junior freeze creates immediately.

**That problem is the apprenticeship pipeline.** The pyramid's wide base was also the training
ground — juniors learned judgment by doing the execution that agents now absorb. If the base
thins, so does the path that produces the mid-tenure supervisors the diamond's middle depends on.
The WEF documents the shift directly: early-career roles move *away from* repetitive task
execution and *toward* judgment-based work "early on" — which is opportunity and risk at once,
because the scaffolding that used to build judgment is exactly what's being automated
([WEF: entry-level work](https://www.weforum.org/stories/2026/03/how-ai-is-changing-the-nature-of-entry-level-work/)).
Designing the 2029 org therefore includes designing a *deliberate* replacement for the learning
the entry-level base used to provide for free — rotations, agent-supervision apprenticeships, and
"do it by hand once before you delegate it" norms. This is the single most-cited unsolved problem
in the shift and belongs on the leadership agenda now, not in 2029.

## 3. Team structures for human–agent teams

Below the org-shape question is the team-design question: *who is on a team, and where do the
boundaries go?* Two complementary lenses answer it — one from how software teams already organize,
one from how production agent systems are actually built.

**3.1 Team Topologies, adapted.** The most useful organizational lens is an adaptation of
**Team Topologies** to agentic platforms ([Wulveryck](https://blog.owulveryck.info/2026/06/22/who-does-what-team-topologies-for-the-agentic-platform.html)),
because it already solved the analogous problem — organizing around cognitive load and self-service
platforms — for software teams. The four team types map cleanly:

- **Stream-aligned teams** become *business-driven, not developer-centric*. They no longer need
  to be made of engineers; they are **domain experts operating an agent orchestrator**, owning
  **intent** and domain context. This is the team type that multiplies.
- **Platform teams** industrialize three things as self-service so stream-aligned teams don't each
  reinvent them: **systemic context** (shared instructions, memory), **systemic guardrails**
  (security, compliance, policy), and **tooling** (the agent runtime, evals, deployment). This is
  the centralized backbone — it absorbs *operational responsibility* so business teams carry only
  *intent*.
- **Enabling teams** are deliberately temporary: they teach stream-aligned teams to work with
  agents, then dissolve as proficiency spreads, preventing the platform from becoming a permanent
  bottleneck.
- **Complicated-subsystem teams** isolate the genuinely deep technical work — model selection and
  optimization, evaluation harnesses, fine-tuning — so expertise stays concentrated instead of
  diluting across every product team.

The crucial design move is the **"what / how" boundary**: stream-aligned teams define *what*
(business intent, domain meaning, acceptance criteria); the platform guarantees *how* (reliable,
governed production). That split is what lets a non-technical team safely "ship" with agents
([Wulveryck](https://blog.owulveryck.info/2026/06/22/who-does-what-team-topologies-for-the-agentic-platform.html)).
It is the org-design twin of the [[agentic-access-to-the-data-platform]] finding that agents
should reach data through a *governed semantic layer* rather than raw tables — in both cases a
platform absorbs the risk so the edge can move fast.

**3.2 Inside the team: the orchestrator-worker fleet.** Within a stream-aligned team, the 50–100
agents are not a flat swarm. The dominant production pattern is **orchestrator-worker** (a.k.a.
supervisor-worker): a lead/manager agent receives the goal, decomposes it into a task graph,
delegates sub-tasks to specialized workers that run in parallel, and synthesizes the results —
workers do not talk to each other; all coordination flows through the orchestrator. This is the
architecture Anthropic ships for Claude's Research feature
([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)), and the
emerging research framing of the **"manager agent"** generalizes it: an agent that "decomposes
complex goals into task graphs, allocates tasks to human and AI workers, monitors progress,
adapts to changing conditions, and maintains transparent stakeholder communication"
([arXiv: Manager Agent](https://arxiv.org/abs/2510.02557)).

For org design this matters because the manager-agent layer gives the human supervisor a *single
point of direction and review* instead of a hundred — it is what makes the order-of-magnitude
span of control tractable. The human manages the manager agent, which manages the fleet.
Designing that intermediate layer well — its decomposition logic, escalation rules, and legibility
to the human — is as much an org-design decision as a technical one. And the same source warns
where it breaks: tightly-coupled work that needs shared context does not parallelize, so not every
team should be reorganized into a fleet ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)).

## 4. New roles and how human work changes

As execution moves to agents, human roles shift up the value chain rather than disappearing. The
recurring pattern across sources is humans as **supervisors, strategists, and exception handlers**
([arXiv](https://arxiv.org/abs/2510.02557)). McKinsey names three concrete archetypes —
**supervisors** who direct agents, **specialists** who redesign workflows and manage exceptions,
and **AI-augmented frontline workers** — and adds that the supporting HR machinery (workforce
planning, performance management, learning) has to be rebuilt around them
([McKinsey](https://www.mckinsey.com/capabilities/people-and-organizational-performance/our-insights/the-agentic-organization-contours-of-the-next-paradigm-for-the-ai-era)).
Synthesizing across sources, four roles are crystallizing:

- **Agent supervisor / "agent manager."** Owns a fleet's output: sets goals, reviews and approves
  consequential actions, catches and corrects errors, and is *named-accountable* for what the
  agents do. This is the thick middle of the diamond and the role most people migrate into.
- **Workflow / system designer.** Designs the cross-functional workflows the AWS talk emphasizes —
  decomposing a business process into agent-executable steps with the right human checkpoints.
  Closer to process engineering than to people management.
- **Domain authority.** Provides the judgment, context, and ground truth that probabilistic agents
  lack — the human whose expertise pins down what "good" means and who handles escalated exceptions.
- **Platform / guardrail owner.** Builds and runs the centralized context, guardrails, and tooling
  (Section 3's platform team) — the people who make decentralized building safe.

The governance principle that ties these together: **the people who deploy the agents are
accountable for the agents' behavior** — accountability does not transfer to the software
([MIT Sloan Management Review](https://sloanreview.mit.edu/article/agentic-ai-at-scale-redefining-management-for-a-superhuman-workforce/)).
In practice that means **humans define the harness** (specifications and quality checks), **humans
retain named accountability** for autonomous action, and **agents execute within a bounded scope
where autonomy expands only where policy, review, and ownership are explicit**. Critically,
**performance management has to change with the roles**: reward the *quality of oversight and
orchestration* — how well a person guides agents, unlocks value, and delivers outcomes — not raw
speed or task volume ([McKinsey](https://www.mckinsey.com/capabilities/people-and-organizational-performance/our-insights/the-agentic-organization-contours-of-the-next-paradigm-for-the-ai-era);
[MIT Sloan Management Review](https://sloanreview.mit.edu/article/agentic-ai-at-scale-redefining-management-for-a-superhuman-workforce/)).
An "agent manager" job that implies one person can meaningfully review the output of 200 agents is
a governance failure written into the org chart.

## 5. The operating model: probabilistic work, oversight, and the centralized/decentralized balance

The AWS talk's four tensions are really one operating-model question: **how do you run an
organization whose workforce is fast, scalable, and probabilistic?** Three design principles
answer it.

**5.1 Manage probabilistic work with iteration and tiered oversight, not one-shot trust.** Agents
behave non-deterministically — the same configuration can produce different outputs across runs
because of sampling, tool latency, and context effects
([Acceldata](https://www.acceldata.io/blog/balancing-probabilistic-and-deterministic-intelligence-the-new-operating-model-for-ai-driven-enterprises)) —
so the operating model is *continuous iteration with intelligent oversight* rather than
fire-and-forget delegation. The practical mechanism is an **autonomy maturity curve** (a.k.a. the
"agentic autonomy curve"): agents start by augmenting humans under tight review loops; as they
demonstrate reliability they take bounded actions under supervision; and only some graduate to
acting autonomously within policy constraints with humans auditing outcomes after the fact
([TrustLab](https://www.trustlab.com/post/ai-agents-are-the-new-decision-makers)). Concretely,
tier work by **stakes and reversibility**: low-stakes, reversible work runs highly autonomously
with notification; high-stakes or irreversible work routes through human approval — the same
calibration logic the companion study applies to data access
([[agentic-access-to-the-data-platform]] §3), here applied to people and process. Production
signals (faulty retrieval, bad tool arguments, ambiguous prompts) feed back into prompts, model
choice, and policy — continuous oversight is the *operating loop*, not a launch gate.

**5.2 Set spans of control by oversight capacity.** The diamond only works if each supervisor's
span is set by *how much they can actually review*. The prescription is to **redesign spans of
control with oversight capacity in mind** — explicitly, per role, with honest limits on velocity
and volume, replacing one-time compliance reviews with continuous, iterative oversight
([MIT Sloan Management Review](https://sloanreview.mit.edu/article/agentic-ai-at-scale-redefining-management-for-a-superhuman-workforce/)).
The manager-agent layer (§3.2) raises that ceiling by giving the human a legible single interface
to the fleet; the trust artifacts from the companion study — reasoning transparency, confidence
signals, source attribution — raise it further by making each review faster. **Oversight capacity
is an *engineerable* quantity, and engineering it up is how you scale safely.** The flip side
shows up in the data: organizations expect flatter structures (≈45% of agentic-AI leaders foresee
fewer middle-management layers), but the binding cap on adoption is *how much oversight humans can
actually provide* — making governance itself the potential bottleneck to productivity.

**5.3 Centralize the guardrails; decentralize the building.** The talk's "optimal mix of
centralized guidance and decentralized innovation" resolves onto a **hub-and-spoke** operating
model: a central AI center of excellence acts as the **hub for strategy, enablement, and
governance — not a gatekeeper for approvals** — providing infrastructure, reusable assets,
training, and guardrails, while business units own delivery, funding, and outcomes
([CIO](https://www.cio.com/article/4106578/2026-the-year-of-scale-or-fail-in-enterprise-ai.html)).
This maps directly onto the Team Topologies split: the platform team *is* the hub; the
stream-aligned teams *are* the spokes. Centralize what must be *consistent* — identity, policy,
audit, the semantic layer; decentralize what must be *fast and contextual* — the business
workflows. Getting it wrong in either direction is the classic failure: fully centralized and the
platform becomes the bottleneck; fully decentralized and you get shadow agents with no governance
([[agentic-access-to-the-data-platform]] §1.3) — and in any business with material regulatory
exposure, a purely federated model simply does not hold.

## 6. What gates the whole thing: the binding constraints

The agentic org is not blocked by a shortage of agents. Three constraints decide whether the
structure above delivers value, and each has a number behind it.

- **Governance readiness, not technology, is the gate.** Gartner expects **over 40% of agentic AI
  projects canceled by end of 2027** — citing escalating cost, unclear value, and inadequate risk
  controls, not model capability ([Gartner](https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027)).
  Governance readiness sits lowest among the foundations (~30%, versus ~43% for technical
  infrastructure), which is exactly the structural foundation the org redesign has to supply
  ([CIO](https://www.cio.com/article/4106578/2026-the-year-of-scale-or-fail-in-enterprise-ai.html)).
- **The data foundation is the moat — and the bottleneck.** As frontier models commoditize, the
  durable differentiator is *proprietary data plus domain expertise* wired into governed workflows
  ([Bain](https://www.bain.com/insights/solutions/turn-artificial-intelligence-into-proprietary-intelligence/decision-3-proprietary-data/)).
  But McKinsey finds the same data foundation is what stalls programs at scale — most enterprise
  data is not agent-ready ([McKinsey: foundations at scale](https://www.mckinsey.com/capabilities/mckinsey-technology/our-insights/building-the-foundations-for-agentic-ai-at-scale)).
  This is the AWS talk's "leverage your unique domain expertise and data" point, and the direct
  link to [[agentic-access-to-the-data-platform]] and [[data-platforms-in-2029]]: the platform
  team owns the asset that makes the agents differentiated.
- **Coordination is a real ceiling, not a detail.** Fleets parallelize breadth but not
  tightly-coupled work, agents still coordinate poorly in real time, and automated evals miss
  behavioral problems humans catch — so "more agents" is not "more output" past a point
  ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)). The org design
  has to respect where the technology actually parallelizes.

## 7. A 2026 → 2029 roadmap

Design-first, mirroring the phased approach in the companion study. The point is to build
*oversight capacity and structure* ahead of agent headcount, not behind it.

**Phase 1 — Re-baseline the work (2026).**
Map which workflows are agent-suitable and classify them by stakes and reversibility. Pick one or
two **lighthouse** end-to-end workflows to redesign around agents rather than scattering pilots
([McKinsey](https://www.mckinsey.com/capabilities/quantumblack/our-insights/seizing-the-agentic-ai-advantage)).
Identify where the pyramid base is already thinning and where the apprenticeship pipeline is at
risk. Stand up a small platform/center-of-excellence nucleus rather than letting every team
improvise its own agents.

**Phase 2 — Build the platform and the boundaries (2026–2027).**
Industrialize context, guardrails, and tooling as self-service (the hub). Establish the
"what / how" boundary so business teams own intent and the platform owns operational
responsibility. Pilot stream-aligned human–agent teams with an orchestrator/manager-agent layer
and an explicit human supervisor; instrument oversight (reasoning traces, approvals, action logs)
from day one. Treat agent-readiness of the data foundation as a first-class workstream.

**Phase 3 — Restructure roles and spans (2027–2028).**
Rewrite job descriptions around supervisor / designer / domain-authority / platform-owner roles
with *explicit, realistic* oversight responsibilities. Set spans of control by measured oversight
capacity. Reset performance management to reward orchestration quality, not task volume. Adopt the
autonomy maturity curve so autonomy widens from evidence. Launch the deliberate apprenticeship
replacement for the eroding base.

**Phase 4 — Operate the (possibly transitional) diamond (2028–2029).**
Run the organization as human–agent teams at scale: thick supervisory middle, narrow human base,
centralized guardrails, decentralized building. Hold the shape *loosely* — the academic evidence
says it may revert as learning effects play out, so keep the talent pipeline able to re-widen.
Treat oversight capacity as the planning constraint and the data/governance foundation
([[agentic-access-to-the-data-platform]]) as the prerequisite it gates on. Keep named human
accountability for every autonomous action.

## Takeaways

- **The org chart itself changes, not just the tooling.** The unit of work becomes "a person
  directing a fleet of agents," which collapses the pyramid base toward a **diamond** with a thick
  supervisory middle — though the best academic model warns the diamond may be *transitional*, so
  plan for reversibility.
- **Oversight capacity is the new binding constraint.** You can add agents instantly; you cannot
  add judgment instantly. Set spans of control by how much agent output a human can actually review
  and stand behind — and reward oversight quality, not volume.
- **Separate intent from execution at the team boundary.** Business-facing stream-aligned teams own
  intent and domain context; a central platform / hub owns operational responsibility, guardrails,
  and tooling — the "what / how" split, echoed in production by orchestrator-worker fleets.
- **A manager-agent layer makes the order-of-magnitude span tractable** by giving each human
  supervisor one legible interface to the fleet — but fleets are expensive (~15× tokens) and
  parallelize breadth, not tightly-coupled work.
- **The value is gated by governance and data, not agent count.** Over 40% of agentic projects are
  forecast to be canceled by 2027 for missing structural foundations; the win is redesigning
  end-to-end workflows on a governed data foundation, with a **named human accountable** for every
  autonomous action and a **deliberately rebuilt apprenticeship pipeline** for the eroding base.

## References

Grouped by the role each source plays, and deliberately spread across consulting, academic,
institutional, engineering, and management sources so no single claim rests on one voice.
*Links checked June 2026. Vendor and analyst materials are cited for frameworks and signals, not
as endorsements.*

### Primary prompt

- **A Leader's Guide to Advanced Team Structures in an Agentic World — AWS re:Invent 2025 (SNR307)**
  ([video](https://www.youtube.com/watch?v=O7u6myBRsns) ·
  [listing](https://www.classcentral.com/course/youtube-aws-re-invent-2025-a-leader-s-guide-to-advanced-team-structures-in-an-agentic-world-snr307-508173))
  — the keynote that prompted this study; frames the leader's task as managing probabilistic AI via
  iteration and oversight, designing cross-functional workflows, balancing capability assessment with
  agile planning on proprietary data, and mixing centralized guidance with decentralized innovation.
  *Supports:* the Context framing and the §5 operating-model tensions.
  *Caveat:* a verbatim transcript could not be retrieved (YouTube gates ASR captions); the talk is
  cited at the level of its published abstract/themes, with specific structural claims attributed to
  the independent sources below.

### Org shape, operating model, and the agentic organization

- **The agentic organization: contours of the next paradigm for the AI era — McKinsey** ([mckinsey.com](https://www.mckinsey.com/capabilities/people-and-organizational-performance/our-insights/the-agentic-organization-contours-of-the-next-paradigm-for-the-ai-era))
  — humans move "above the loop" from performing tasks to orchestrating outcomes; a 2–5 person team
  supervising an "agent factory" of 50–100 agents; five pillars (business model, operating model,
  governance, workforce, technology/data) and the supervisor / specialist / AI-augmented-frontline
  role archetypes.
  *Supports:* §1 unit-of-work shift, §2 diamond, §3 agent factory, §4 roles and HR redesign.

- **Seizing the agentic AI advantage — McKinsey (QuantumBlack)** ([mckinsey.com](https://www.mckinsey.com/capabilities/quantumblack/our-insights/seizing-the-agentic-ai-advantage))
  — ROI comes from redesigning end-to-end workflows around agents and replacing functional silos with
  cross-functional autonomous agentic teams, launched as focused "lighthouse" transformations.
  *Supports:* §1 "redesign, don't sprinkle" and the §7 lighthouse-first roadmap.

- **Building the foundations for agentic AI at scale — McKinsey** ([mckinsey.com](https://www.mckinsey.com/capabilities/mckinsey-technology/our-insights/building-the-foundations-for-agentic-ai-at-scale))
  — most enterprises have not scaled agents to value, and most cite data limitations as the roadblock.
  *Supports:* §6 the data foundation as both moat and bottleneck.

- **No more pyramids: rethinking your workforce for the agentic AI era — PwC** ([pwc.com](https://www.pwc.com/us/en/tech-effect/ai-analytics/agentic-ai-workforce-redesign.html))
  — agents absorb entry-level tasks, eroding the pyramid base and pushing the org toward a diamond.
  *Supports:* §2 pyramid→diamond and the apprenticeship-pipeline risk.

- **Leading in the age of AI agents: managing the machines that manage themselves — BCG** ([bcg.com](https://www.bcg.com/publications/2025/machines-that-manage-themselves))
  — managerial roles evolve to orchestrate hybrid human-AI teams; oversight and accountability
  concentrate in the middle.
  *Supports:* §1 the manager's changing job. *Caveat:* cited from its published thesis; the full text
  was not retrievable.

- **Agentic AI at scale: redefining management for a superhuman workforce — MIT Sloan Management Review** ([sloanreview.mit.edu](https://sloanreview.mit.edu/article/agentic-ai-at-scale-redefining-management-for-a-superhuman-workforce/))
  — old human-paced management models fall short; replace one-time compliance reviews with continuous,
  iterative oversight; the people who deploy agents stay accountable; redesign spans of control and
  performance management around oversight quality.
  *Supports:* §4 accountability, §5.1–5.2 oversight and spans of control.
  *Caveat:* a curated expert-panel debate, not measured outcomes.

### Academic and institutional

- **Pyramids, Diamonds, and Oscillations: AI and the Structure of Internal Labor Markets — Friebel, Huang, Li, Shukla & Zhang (SSRN/NBER, Apr 2026)** ([ssrn.com](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6570519))
  — formally models AI as raising productivity and learning speed; finds the diamond is often a
  *short-run* state (firms freeze junior hiring) while long-run span depends on which effect dominates.
  *Supports:* the §2 caveat that the diamond may be transitional — the study's key intellectual
  counterweight to the consultant consensus. *Caveat:* a working paper; model results, not field data.

- **How AI is changing the nature of entry-level work — World Economic Forum** ([weforum.org](https://www.weforum.org/stories/2026/03/how-ai-is-changing-the-nature-of-entry-level-work/))
  — junior roles shift away from repetitive execution toward judgment-based work "early on," straining
  the traditional training pipeline.
  *Supports:* §2 apprenticeship-pipeline risk and §4 role evolution.

- **Four ways AI and talent could reshape jobs by 2030 — World Economic Forum** ([weforum.org](https://www.weforum.org/stories/2026/01/here-are-four-ways-ais-impact-on-job-markets-might-take-shape/))
  — scenario set in which "humans become agent orchestrators"; even the high-AI scenario yields a net
  gain of ~78M jobs by 2030 (≈170M created, ≈92M displaced).
  *Supports:* §2 the orchestrator framing and the net-jobs context. *Caveat:* scenario planning, not
  forecast.

### Team structure and orchestration

- **Who does what? Team Topologies for the agentic platform — Olivier Wulveryck** ([blog.owulveryck.info](https://blog.owulveryck.info/2026/06/22/who-does-what-team-topologies-for-the-agentic-platform.html))
  — maps the four Team Topologies team types and three interaction modes onto agentic systems;
  stream-aligned teams own intent, the platform owns operational responsibility ("what / how" split).
  *Supports:* §3.1 team structures and the intent/execution boundary.
  *Caveat:* a practitioner blog adapting an existing framework; cited for the mapping, not as a standard.

- **How we built our multi-agent research system — Anthropic** ([anthropic.com](https://www.anthropic.com/engineering/multi-agent-research-system))
  — production orchestrator-worker design: a lead agent plans and spawns parallel subagents;
  outperformed a single agent by 90.2% on their research eval but uses ~15× the tokens of a chat;
  fails on tightly-coupled work, agents coordinate poorly in real time, and human review catches what
  evals miss.
  *Supports:* §1 the economics/limits reality check, §3.2 orchestrator-worker, §6 coordination ceiling.

- **Orchestrating human–AI teams: the manager agent as a unifying research challenge — arXiv 2510.02557** ([arxiv.org](https://arxiv.org/abs/2510.02557))
  — the "manager agent" that decomposes goals into task graphs and coordinates human and AI workers;
  humans as supervisors / strategists / exception handlers.
  *Supports:* §3.2 manager-agent layer and §4 role pattern.
  *Caveat:* a research framing of an open problem, not a deployed standard.

### Governance, oversight, and the binding constraints

- **2026: the year of scale or fail in enterprise AI — CIO** ([cio.com](https://www.cio.com/article/4106578/2026-the-year-of-scale-or-fail-in-enterprise-ai.html))
  — the hub-and-spoke operating model: a central CoE as hub for strategy/enablement/governance (not an
  approvals gatekeeper), business units owning delivery; governance readiness (~30%) lags technical
  infrastructure (~43%).
  *Supports:* §5.3 centralized/decentralized balance and §6 governance-readiness gate.

- **AI agents are the new decision-makers: why continuous oversight is not optional — TrustLab** ([trustlab.com](https://www.trustlab.com/post/ai-agents-are-the-new-decision-makers))
  — the agentic autonomy curve: augment under review → bounded actions under supervision → post-hoc
  audit within policy; continuous, policy-driven oversight combining automation and human judgment.
  *Supports:* §5.1 autonomy maturity curve and tiered oversight. *Caveat:* vendor blog, cited for the
  maturity-model framing.

- **Balancing probabilistic and deterministic intelligence — Acceldata** ([acceldata.io](https://www.acceldata.io/blog/balancing-probabilistic-and-deterministic-intelligence-the-new-operating-model-for-ai-driven-enterprises))
  — why agents are non-deterministic (sampling, tool latency, context effects) and what that implies
  for an operating model that pairs probabilistic reasoning with deterministic control.
  *Supports:* §5.1 the nature of probabilistic work.

- **Over 40% of agentic AI projects will be canceled by end of 2027 — Gartner** ([gartner.com](https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027))
  — cancellations driven by cost, unclear value, and inadequate risk controls — not model capability.
  *Supports:* §6 the governance-readiness gate. *Caveat:* a forward-looking analyst prediction.

- **Turn AI into proprietary intelligence — Decision 3: proprietary data — Bain & Company** ([bain.com](https://www.bain.com/insights/solutions/turn-artificial-intelligence-into-proprietary-intelligence/decision-3-proprietary-data/))
  — as models commoditize, proprietary data plus domain expertise becomes the durable moat.
  *Supports:* §6 the data foundation as moat and the AWS "leverage your domain data" point.

### Companion studies

- **[[agentic-access-to-the-data-platform]]** — the data-platform counterpart: how agents reach the
  platform safely via a governed semantic layer, first-class non-human identity, and separate audit.
  This study reuses its autonomy-tiering, progressive-delegation, and centralize-the-guardrails logic
  at the level of teams and process rather than data access.
- **[[data-platforms-in-2029]]** — the platform-evolution counterpart on where the data foundation is
  heading, which §6 names as the moat the platform team owns.

# Alpha Dataflows

Three core flows define the Stitchia alpha environment. Documenting them early
helps keep contracts, scrolls, and dashboards aligned.

## 1. Governance Proposal Flow
1. Author writes/updates scroll describing proposal intent.
2. Validator seals scroll (`./quantum seal`).
3. DAO proposer submits transaction via `StitchiaDAO.propose`.
4. Voting window opens (SYNQ balance + Pulse bonus + Genesis NFT multiplier).
5. Proposal finalises (`Passed` or `Rejected`).
6. Executor multi-sig triggers `markExecuted` with outcome summary.
7. Registry + dashboard refresh to reflect new state.

**Artifacts touched:** Scrolls, ledger, braids, dashboard JSON, on-chain DAO.

## 2. Treasury Recycling (Impact FX) Flow
1. Treasury receives inflow (staking, LP rewards, grants, etc.).
2. Policy scroll defines recycling percentages.
3. Impact Router (mock or contract) splits funds per 30/40/30 template.
4. Pool allocations logged (on-chain event or ledger entry).
5. Impact proof minted/recorded (manual during alpha).
6. Dashboard displays latest allocation ratios.

**Artifacts touched:** Treasury policy scroll, ImpactRouter (or mock script),
dashboard JSON, investor bundle updates.

## 3. Impact Score Submission Flow
1. Metric configuration scrolls list enabled metrics (id, label, weight).
2. DAO sets metrics via `PulseScorer.configureMetric`.
3. Feeders submit impact scores (manual or scripted transactions).
4. Voters query aggregate scores during proposals/votes.
5. Dashboard pulls `PulseScorer.computeAggregate` output for transparency.

**Artifacts touched:** PulseScorer contract, metrics scroll, governance reports.

---

### Artefact Mapping Table

| Flow | Contract / Tooling | Scroll / Document | Frontend Surface |
| --- | --- | --- | --- |
| Governance Proposal | StitchiaDAO.sol, multi-sig | Proposal scrolls, validator workflow | Dashboard governance panel |
| Treasury Recycling | ImpactRouter (mock), treasury scripts | Treasury policy scroll, investor bundle | Treasury lens + impact scoreboard |
| Impact Score Submission | PulseScorer.sol, feeder scripts | Metric config scroll | Impact scoreboard + vote cards |

Use this file to capture new flows (e.g., token distribution, DID onboarding)
as the alpha scope expands.

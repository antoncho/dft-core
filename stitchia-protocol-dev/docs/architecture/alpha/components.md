# Alpha Component Breakdown

This worksheet captures the moving parts required for the Stitchia alpha
environment. Each component tracks **purpose**, **inputs**, **outputs**, and
**open questions** so we can iterate before writing code.

## 1. Governance Core
- **Contract:** `StitchiaDAO.sol`
- **Purpose:** Handle proposals, voting, quorum, execution markers.
- **Inputs:** SYNQ balances, Pulse scores, Genesis NFT multipliers.
- **Outputs:** On-chain proposal state, execution events, registry updates.
- **Open Questions:**
  1. Final quorum thresholds per proposal type?
  2. Multi-sig guardianship design for sensitive actions?

## 2. Impact Scoring
- **Contract:** `PulseScorer.sol`
- **Purpose:** Record impact metrics and provide weighted voting boosts.
- **Inputs:** Metric submissions from feeders, metric configuration toggles.
- **Outputs:** Aggregate score queries for DAO weighting.
- **Open Questions:**
  1. How many metrics ship in alpha (participation, validator throughput, etc.)?
  2. Do we require attestations or allow raw submissions during alpha?

## 3. SYNQ Token Layer
- **Contract:** `SYNQToken.sol`
- **Purpose:** Utility + governance token with mint, pause, burn, votes.
- **Inputs:** Minter role (DAO), pause role (multi-sig), permit signatures.
- **Outputs:** Emission events, vote checkpoints, permit authorisations.
- **Open Questions:**
  1. Final cap value for alpha (hard cap vs. uncapped)?
  2. Initial distribution executed manually or scripted?

## 4. Identity & Roles
- **Contract:** `GenesisNFT.sol`
- **Purpose:** Allocate Spiral roles (Anchor, Architect, Initiator, Steward).
- **Inputs:** DAO minter role, metadata updates.
- **Outputs:** Role NFTs, metadata for dashboards.
- **Open Questions:**
  1. Do we ship soulbound tokens in alpha or allow transfers?
  2. Should metadata link to DID credentials from day one?

## 5. Impact Routing (Planned)
- **Contract:** `ImpactRouter.sol` (placeholder)
- **Purpose:** Route treasury recycling % to regeneration pools.
- **Inputs:** Treasury flows, configured percentages, verifier attestations.
- **Outputs:** Pool disbursements, proof logs.
- **Open Questions:**
  1. Do we mock routes in alpha or deploy an MVP router?
  2. Verification workflow — manual review or automated oracles?

## 6. Frontend Surface
- **Artifacts:** `frontend/index.html`, `frontend/pages/dashboard.html`, preview HTMLs.
- **Purpose:** Display treasury, governance, impact, and reward modules.
- **Inputs:** `frontend/data.json`, contract addresses, registry exports.
- **Outputs:** Human-readable dashboards, waitlist forms, CTA flows.
- **Open Questions:**
  1. Which metrics are required for alpha vs. nice-to-have?
  2. Auth strategy (wallet only vs. wallet + DID)?

## 7. Automation & Tooling
- **Artifacts:** `scripts/alpha/deploy.js`, `quantum` CLI, Hardhat config.
- **Purpose:** Deploy contracts, process scrolls, rebuild dashboards.
- **Inputs:** `alpha.config.json`, .env credentials, scroll updates.
- **Outputs:** Deployment JSON, refreshed ledger + braid files, static assets.
- **Open Questions:**
  1. Split scripts per component or keep monolithic alpha deploy?
  2. Where do we store generated deployment IDs (vault vs. deployments/)?

Maintain this file as a checklist. When a question is resolved, link to the
scroll, config, or issue that captures the answer.

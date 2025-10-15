---
title: "Stitchia DAO – TGC Protocol (v0.2-alpha)"
classification: Governance+Ethics+StrategicDesign+Protocol
validators:
  - role: "Governance Architect"
  - role: "Ethics Steward"
license: Public-Licensed / CodexLinked
tags: [stitchia, dao, protocol, governance, spiral]
links:
  - stitchia-protocol-dev/contracts/StitchiaDAO.sol
  - stitchia-protocol-dev/contracts/GenesisNFT.sol
  - stitchia-protocol-dev/contracts/PulseScorer.sol
  - stitchia-protocol-dev/contracts/SYNQToken.sol
---

# Stitchia DAO – TGC Protocol · v0.2-alpha

**Release Date:** 2025-09-10  
**Maintainers:** TheGenuine Collective (TGC) · Digital Fabrica Governance Architects  
**Source Control:** `stitchia-protocol-dev/docs/Stitchia DAO_TGC Protocol_v0.2.md`

## 1. Executive Summary

Stitchia DAO is the governance and funding fabric for TheGenuine Collective. The
protocol replaces extractive financing with regenerative, Spiral-aligned
coordination. Version 0.2-alpha aligns the narrative with the current codebase:

- Smart contract primitives are live (`GenesisNFT`, `SYNQToken`, `PulseScorer`,
  `StitchiaDAO`).
- Deployment automation is available via `scripts/alpha/deploy.js` with Hardhat.
- Governance flows now incorporate weighted participation via Pulse metrics.
- Spiral roles are embedded across token, NFT, and DAO layers.

## 2. Component Stack Overview

| Layer | Contract / Artifact | Purpose |
| --- | --- | --- |
| Identity | `GenesisNFT` | Anchors Spiral roles, campaign metadata, and contributor identity. |
| Economics | `SYNQToken` | Utility + governance token with votes, permits, and optional supply cap. |
| Analytics | `PulseScorer` | Aggregates participation metrics and feeds voting weight boosts. |
| Governance | `StitchiaDAO` | Coordinates proposals, voting, and role delegation across initiatives. |
| Deployment | `scripts/alpha/deploy.js` | Hardhat automation to wire the stack for sandbox/testnet use. |

### Role Wiring (post-deploy)

The alpha deploy script grants DAO ownership over key actions:

- DAO can mint/adjust Genesis NFTs and SYNQ token supply (within cap).
- DAO manages Pulse metric configuration for weighted governance.
- DAO executors mark proposals as executed; pausers can halt SYNQ transfers.

## 3. Deployment Playbook

1. Copy `scripts/alpha/config.example.json` → `scripts/alpha/alpha.config.json`.
2. Populate values (initial SYNQ supply, metric weights, Spiral metadata).
3. Ensure `hardhat.config.js` is configured for target network (e.g. Sepolia).
4. Run `npx hardhat run --network <network> scripts/alpha/deploy.js`.
5. Capture addresses from `deployments/alpha-<chainId>.json` and register them
   within Fabrica scrolls and braids (`./quantum process` + `./quantum build`).

## 4. Use Case Clusters (Refreshed)

| Cluster | Intent | Pillars |
| --- | --- | --- |
| 🧬 Creator Sovereignty | Launch creator-led funding rounds with on-chain ownership and non-custodial payouts. | Mintable supporter NFTs (soulbound or transferable), time-locked vaults, auto splits to collaborators, governance hooks via Spiral roles. |
| 🌐 Collective Pools | Mutual-aid and regenerative infrastructure pools spanning local → planetary scales. | Impact-weighted governance (Pulse metrics), sustainability clauses (exit-to-community), treasury routing via SYNQ + stable assets. |
| 💡 R&D Launchpad | Spin up research pilots for Web4, cybernetics, and governance experiments. | Spiral-encoded research scrolls, royalty splits, replication incentives, integration with Monad + Codex Lines. |
| ⚖️ Civic Justice | Finance policy, legal defense, and public infrastructure with DAO-native logic. | DID-backed participation, legal defense vaults, mesh/utility infrastructure funding, transparent accountability ledger. |

### Modular Extensions

- Cross-chain contributions (EVM, IBC, Bitcoin L2) via bridge adapters.
- Auto airdrops for early contributors and validator rewards.
- Reputation weighting through Pulse metrics + DIDs.
- Data exports powering `frontend/pages/dashboard.html` and TGC comms (TikTok
  `@stitchiabites`).

## 5. Governance Flow

1. **Author Scroll** – Campaign spec authored in `vault/documents/` using the
   Fabrica template. Include Spiral role mapping and treasury intent.
2. **Process & Register** – `./quantum process` produces registry entry and
   braid links (ensures ethics compliance).
3. **Deploy Contracts** – Use the alpha deploy script or upgrade modules as
   needed. Governance addresses are stored in ledger + deployment JSON.
4. **Proposal Lifecycle** – `StitchiaDAO` handles proposal creation → activation
   → voting → finalization → execution.
5. **Pulse Integration** – Metrics submitted by feeders adjust voting weight
   (e.g. participation, validator throughput). DAO sets default metric bundles.
6. **Treasury Operations** – SYNQ mint/burn + vault routing follow DAO-approved
   proposals. Time-locked vaults and auto splits are executed by campaign logic.

### Proposal Statuses

| Status | Meaning |
| --- | --- |
| Draft | Created, awaiting activation (voting start block pending). |
| Active | Voting window open. |
| Passed | Quorum met, FOR > AGAINST. |
| Rejected | Voting concluded without meeting thresholds. |
| Executed | Actions performed (by executor role / scripting layer). |
| Cancelled | Withdrawn pre-finalization. |

## 6. Spiral Alignment Matrix

| Spiral Role | Governance Energy | On-Chain Anchors | Example Actions |
| --- | --- | --- | --- |
| Anchor | Mission + ethics | GenesisNFT metadata (`role=Anchor`), DAO proposer whitelist | Define protocol guardrails, certify campaign ethics. |
| Architect | Systems design | Proposal authoring rights, Pulse metric configuration | Encode funding mechanics, configure metrics, manage upgrade paths. |
| Initiator | Momentum | Campaign NFTs, SYNQ incentive tranches | Launch outreach, seed initial contributions, steward energy. |
| Steward | Long-term care | DAO executor role, treasury oversight | Execute proposals, maintain vault health, coordinate audits. |

## 7. Tokenomics Snapshot (v3.2 Alignment)

- **SYNQToken**: capped/un-capped supply configurable; votes derived from token
  balances + Pulse boosts; permit signatures supported for gasless approvals.
- **Treasury Streams**: use `releases/v2.5/manifest.json` + Synq appendices for
  budget allocations; DAO-approved flows recorded in
  `vault/registry/ledger.json`.
- **Genesis NFTs**: attach Spiral metadata + campaign URIs for dashboards; DAO
  controls minter + metadata roles.
- **Pulse Metrics**: start with `participation` (weight 100k) and `validator`
  (weight 50k); expand with research / civic metrics as programs launch.

## 8. Next Actions

1. **Finalize Alpha Deploy** – Execute script on Sepolia, capture addresses,
   update registry scrolls.
2. **Integrate Frontend** – Wire new contract addresses into
   `frontend/assets/js/dashboard.js` data pipeline.
3. **Run Governance Dry-Run** – Create a simulation proposal exercising vote
   weighting + SYNQ mint/treasury flows.
4. **Document Playbooks** – Convert this protocol doc into a scroll for the
   charter bundle and link from Business/Tech stacks.
5. **Security Review** – Schedule OZ-style audit or peer review ahead of beta.

## 9. References

- `docs/SYNQ_Tokenomics_v3.2.md`
- `docs/Business_Stack.md`
- `docs/Tech_Stack.md`
- `docs/Validator_Workflow.md`
- `frontend/index.html` (landing) & `frontend/pages/dashboard.html` (DAO UI)
- `scripts/alpha/README.md`

Let this version serve as the canonical snapshot for aligning Scroll governance,
on-chain primitives, and civic deployments going into the v0.3 roadmap.

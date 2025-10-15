# 🧬 Stitchia Protocol

This repository contains the smart contracts, token logic, documentation, and frontend components of the Stitchia Protocol — a regenerative cultural operating system built for decentralized coordination.

- Whitepaper v2.6: `docs/whitepaper/stitchia_whitepaper_v2.6.md`
- Changelog: `docs/whitepaper/CHANGELOG.md`
- Dashboard Spec: `docs/DAO_Dashboard_Spec.md`

Quick start (local):

1. `./quantum init --with-example`
2. `./quantum process scrolls/dao_dashboard_scroll.md`
3. `./quantum build`
4. Open `frontend/index.html` to preview the dashboard.

Releases
--------
- v2.5 docs bundle: `releases/v2.5/stitchia-protocol-docs-v2.5.zip` (see `releases/v2.5/manifest.json` for SHA256)

Alpha Deployment Toolkit
------------------------
- Copy `scripts/alpha/config.example.json` → `scripts/alpha/alpha.config.json`
- Install Hardhat + toolbox (`npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox dotenv`)
- Run `npx hardhat run --network <network> scripts/alpha/deploy.js` to deploy SYNQToken, GenesisNFT, PulseScorer, and StitchiaDAO with the configured parameters.

Investor / Partner Bundle
-------------------------
- `docs/SYNQ_v3.2_DAO_Signature_Edition/` packages tokenomics docs, visuals, models, and appendices for stakeholder review.

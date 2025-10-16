# Alpha Operations Runbook (Draft)

Use this runbook to track the manual steps required to stand up or recover the
alpha environment. Automate tasks as the tooling matures.

## 0. Pre-flight
- [ ] Confirm repository is on `stitchia-protocol-dev` branch.
- [ ] Update whitepaper/changelog references if scope changed.
- [ ] Ensure `.env` contains `RPC_URL` and `PRIVATE_KEY` (never commit).

## 1. Scroll Processing
- [ ] Author/update relevant scrolls in `vault/documents/`.
- [ ] Run `./quantum process <scroll>` for each update.
- [ ] Run `./quantum build` to refresh `frontend/data.json`.

## 2. Deployment Dry Run (No network writes)
- [ ] Inspect `docs/architecture/alpha/configs/synq-alpha.config.yml`.
- [ ] Run `npx hardhat compile` to confirm contracts build.
- [ ] Execute `npx hardhat run --network hardhat scripts/alpha/deploy.js`
      with the Hardhat in-memory network for a smoke test.
- [ ] Capture generated addresses in `deployments/alpha-hardhat.json` (local only).

## 3. Frontend Refresh
- [ ] Open `frontend/index.html` and `frontend/pages/dashboard.html` in a
      browser to verify metrics render.
- [ ] Review preview snapshots under `frontend/previews/` for upcoming layout
      iterations.

## 4. Registry & Docs Sync
- [ ] Commit updated ledger/braid files if ethics seals changed.
- [ ] Update investor bundle artefacts if tokenomics assumptions changed.
- [ ] Push to fork and prepare PR to upstream.

## 5. Incident Notes
Record any issues encountered here. Convert recurring items into GitHub issues
or protocol scroll updates.

| Date | Issue | Notes | Follow-up |
| --- | --- | --- | --- |
|      |       |       |           |

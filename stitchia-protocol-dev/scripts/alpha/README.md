# Stitchia Alpha Deployment Helper

The files in this folder provide an initial automation scaffold for deploying the
core Stitchia contracts (`SYNQToken`, `GenesisNFT`, `PulseScorer`, and
`StitchiaDAO`). They are intentionally minimal so you can iterate quickly while
the on-chain architecture is still taking shape.

## Prerequisites

- Node.js 18+
- `npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox dotenv`
- A Hardhat config in the repository root (example below)
- `alpha.config.json` derived from `config.example.json`
  - `synq.initialSupply` / `cap` numbers are interpreted using `synq.decimals`
  - `pulse.metrics[*].id` is hashed with `keccak256` to produce metric IDs

### Minimal `hardhat.config.js`

```js
require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

module.exports = {
  solidity: "0.8.20",
  networks: {
    sepolia: {
      url: process.env.RPC_URL,
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : []
    }
  },
  paths: {
    sources: "./contracts",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts"
  }
};
```

## Deploy

1. Copy `config.example.json` → `alpha.config.json` and adjust values.
2. Export `RPC_URL` / `PRIVATE_KEY` (or configure Hardhat accounts manually).
3. Run the script with Hardhat:

   ```bash
   npx hardhat run --network sepolia scripts/alpha/deploy.js
   ```

4. Inspect the generated `deployments/alpha-<chainId>.json` for addresses and
   configuration provenance.

During early testing you can re-run the script on a dev network (Hardhat or
Anvil) as many times as needed. For production, consider promoting the output
JSON into version control so downstream services (watchers, dashboards, CLI)
can resolve contract addresses deterministically.

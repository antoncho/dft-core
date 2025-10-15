/*
 * Alpha deployment helper for the Stitchia contracts.
 *
 * Usage (after installing Hardhat + dependencies):
 *   npx hardhat run --network <network> scripts/alpha/deploy.js
 *
 * The script looks for an `alpha.config.json` file alongside this script. If one
 * is not found it falls back to `config.example.json`. Copy the example and
 * tailor values before deploying to live networks.
 */

const fs = require("fs");
const path = require("path");
const { ethers } = require("hardhat");

const CONFIG_FILENAME = process.env.ALPHA_CONFIG || "alpha.config.json";

function resolveConfigPath() {
  const directPath = path.join(__dirname, CONFIG_FILENAME);
  if (fs.existsSync(directPath)) {
    return directPath;
  }

  const fallbackPath = path.join(__dirname, "config.example.json");
  if (!fs.existsSync(fallbackPath)) {
    throw new Error("Missing configuration: provide alpha.config.json or config.example.json");
  }
  return fallbackPath;
}

function parseUnits(value, decimals) {
  if (!value) return 0n;
  return ethers.parseUnits(value.toString(), decimals);
}

function toBytes32Id(name) {
  return ethers.keccak256(ethers.toUtf8Bytes(name));
}

async function main() {
  const configPath = resolveConfigPath();
  const config = JSON.parse(fs.readFileSync(configPath, "utf8"));

  const [deployer] = await ethers.getSigners();
  const network = await ethers.provider.getNetwork();

  console.log("\n🚀 Deploying Stitchia alpha stack");
  console.log(`   Signer:  ${deployer.address}`);
  console.log(`   Network: ${network.name} (${network.chainId})`);

  // ---------------------------------------------------------------------------
  // SYNQ Token
  // ---------------------------------------------------------------------------
  const synqFactory = await ethers.getContractFactory("SYNQToken");
  const initialSupply = parseUnits(config.synq?.initialSupply ?? "0", config.synq?.decimals ?? 18);
  const cap = config.synq?.cap === "0" || !config.synq?.cap
    ? 0n
    : parseUnits(config.synq.cap, config.synq?.decimals ?? 18);

  const synqToken = await synqFactory.deploy(deployer.address, initialSupply, cap);
  await synqToken.waitForDeployment();
  const synqAddress = await synqToken.getAddress();
  console.log(`✔ SYNQToken deployed at ${synqAddress}`);

  // ---------------------------------------------------------------------------
  // Genesis NFT
  // ---------------------------------------------------------------------------
  const genesisFactory = await ethers.getContractFactory("GenesisNFT");
  const genesisBaseUri = config.genesis?.baseURI ?? "";
  const genesisAdmin = deployer.address;
  const genesisContract = await genesisFactory.deploy(genesisBaseUri, genesisAdmin);
  await genesisContract.waitForDeployment();
  const genesisAddress = await genesisContract.getAddress();
  console.log(`✔ GenesisNFT deployed at ${genesisAddress}`);

  // ---------------------------------------------------------------------------
  // Pulse Scorer
  // ---------------------------------------------------------------------------
  const pulseFactory = await ethers.getContractFactory("PulseScorer");
  const pulseContract = await pulseFactory.deploy(deployer.address);
  await pulseContract.waitForDeployment();
  const pulseAddress = await pulseContract.getAddress();
  console.log(`✔ PulseScorer deployed at ${pulseAddress}`);

  // Configure metrics on the scorer
  const metricNameToId = {};
  if (Array.isArray(config.pulse?.metrics)) {
    for (const metric of config.pulse.metrics) {
      const id = toBytes32Id(metric.id);
      metricNameToId[metric.id] = id;
      const tx = await pulseContract.configureMetric(
        id,
        metric.label,
        Number(metric.weight ?? 0),
        Boolean(metric.enabled ?? true)
      );
      await tx.wait();
      console.log(`   ↳ metric configured: ${metric.id} (${metric.label})`);
    }
  }

  // ---------------------------------------------------------------------------
  // Stitchia DAO
  // ---------------------------------------------------------------------------
  const daoFactory = await ethers.getContractFactory("StitchiaDAO");
  const daoContract = await daoFactory.deploy(
    deployer.address,
    genesisAddress,
    pulseAddress
  );
  await daoContract.waitForDeployment();
  const daoAddress = await daoContract.getAddress();
  console.log(`✔ StitchiaDAO deployed at ${daoAddress}`);

  // Configure voting parameters
  const votingDelay = BigInt(config.dao?.votingDelay ?? 1);
  const votingPeriod = BigInt(config.dao?.votingPeriod ?? 40);
  const quorumVotes = BigInt(config.dao?.quorumVotes ?? 0);
  await (await daoContract.setVotingParameters(votingDelay, votingPeriod, quorumVotes)).wait();
  console.log(`   ↳ voting params set (delay=${votingDelay}, period=${votingPeriod}, quorum=${quorumVotes})`);

  // Set default metrics for DAO voting weight boosts
  if (Array.isArray(config.dao?.defaultMetrics) && config.dao.defaultMetrics.length > 0) {
    const metricIds = config.dao.defaultMetrics
      .map((name) => metricNameToId[name])
      .filter((id) => id !== undefined);

    if (metricIds.length > 0) {
      await (await daoContract.setDefaultMetrics(metricIds)).wait();
      console.log(`   ↳ default metrics applied (${metricIds.length} entries)`);
    }
  }

  // ---------------------------------------------------------------------------
  // Role wiring between contracts
  // ---------------------------------------------------------------------------
  const daoRoleTxs = [];

  daoRoleTxs.push(
    genesisContract.grantRole(await genesisContract.MINTER_ROLE(), daoAddress)
  );
  daoRoleTxs.push(
    genesisContract.grantRole(await genesisContract.METADATA_ROLE(), daoAddress)
  );
  daoRoleTxs.push(
    synqToken.grantRole(await synqToken.MINTER_ROLE(), daoAddress)
  );
  daoRoleTxs.push(
    synqToken.grantRole(await synqToken.PAUSER_ROLE(), daoAddress)
  );
  daoRoleTxs.push(
    pulseContract.grantRole(await pulseContract.CONFIG_ROLE(), daoAddress)
  );
  daoRoleTxs.push(
    pulseContract.grantRole(await pulseContract.FEEDER_ROLE(), daoAddress)
  );

  for (const txPromise of daoRoleTxs) {
    const receipt = await (await txPromise).wait();
    console.log(`   ↳ role granted (tx: ${receipt.hash})`);
  }

  // Optionally attach default Genesis metadata to bootstrap dashboards
  if (config.genesis?.defaultRole) {
    const meta = config.genesis.defaultRole;
    console.log("   ↳ default Genesis role metadata prepared for off-chain use:", meta);
  }

  // ---------------------------------------------------------------------------
  // Persist deployment info for future scripts
  // ---------------------------------------------------------------------------
  const outputDir = path.resolve(__dirname, "../../deployments");
  fs.mkdirSync(outputDir, { recursive: true });
  const outputFile = path.join(outputDir, `alpha-${network.chainId}.json`);
  const output = {
    network: {
      name: network.name,
      chainId: Number(network.chainId)
    },
    deployer: deployer.address,
    timestamp: new Date().toISOString(),
    contracts: {
      synqToken: synqAddress,
      genesisNFT: genesisAddress,
      pulseScorer: pulseAddress,
      stitchiaDAO: daoAddress
    },
    config: {
      synq: config.synq,
      genesis: {
        baseURI: config.genesis?.baseURI,
        defaultRole: config.genesis?.defaultRole
      },
      dao: {
        votingDelay: Number(votingDelay),
        votingPeriod: Number(votingPeriod),
        quorumVotes: quorumVotes.toString(),
        defaultMetrics: config.dao?.defaultMetrics ?? []
      }
    }
  };

  fs.writeFileSync(outputFile, JSON.stringify(output, null, 2));
  console.log(`\n📝 Deployment summary written to ${outputFile}`);
  console.log("Done.\n");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

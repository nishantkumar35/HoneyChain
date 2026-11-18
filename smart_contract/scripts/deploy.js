/**
 * deploy.js — Deploy the HoneyChain smart contract to the local Hardhat node.
 *
 * Usage:
 *   1. Start the Hardhat node in a separate terminal:
 *      cd smart_contract && npx hardhat node
 *
 *   2. Run this script:
 *      cd smart_contract && npx hardhat run scripts/deploy.js --network localhost
 *
 *   3. Copy the deployed contract address into your .env file:
 *      CONTRACT_ADDRESS=0x...
 *
 *   4. Copy the first Hardhat account's private key into .env:
 *      DEPLOYER_PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
 *      (The above is Hardhat's default Account #0 key — safe for local dev only)
 */

const hre = require("hardhat");

async function main() {
  console.log("🍯 Deploying HoneyChain smart contract...\n");

  // Get the contract factory
  const HoneyChain = await hre.ethers.getContractFactory("HoneyChain");

  // Deploy the contract
  const honeyChain = await HoneyChain.deploy();
  await honeyChain.waitForDeployment();

  const address = await honeyChain.getAddress();

  console.log("✅ HoneyChain deployed successfully!");
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  console.log(`   Contract Address : ${address}`);
  console.log(`   Network          : ${hre.network.name}`);
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  console.log("\n📋 Next steps:");
  console.log("   1. Copy the contract address above.");
  console.log("   2. Add it to your .env file:");
  console.log(`      CONTRACT_ADDRESS=${address}`);
  console.log("   3. Add Hardhat Account #0 private key to .env:");
  console.log("      DEPLOYER_PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80");
  console.log("   4. Restart your Django development server.\n");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment failed:", error);
    process.exit(1);
  });


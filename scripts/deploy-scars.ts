import { ethers } from "hardhat";

async function main() {
  const SCARS = await ethers.getContractFactory("SCARS");
  const scars = await SCARS.deploy();

  // Wait for deployment transaction to be mined
  const tx = await scars.waitForDeployment();

  // Get the deployed address
  const address = await scars.getAddress();

  console.log(`SCARS deployed to: ${address}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

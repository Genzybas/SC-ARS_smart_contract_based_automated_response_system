import { run } from "hardhat";

async function main() {
  const contractAddress = process.env.SCARS_CONTRACT_ADDRESS as string;

  await run("verify:verify", {
    address: contractAddress,
    constructorArguments: [], // Add args if needed
  });
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

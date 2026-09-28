import { ethers } from "hardhat";
import * as dotenv from "dotenv";
dotenv.config();

async function main() {
  // Replace with your deployed address from localhost or testnet
  const scarsAddress = process.env.SCARS_CONTRACT_ADDRESS as string;

  const scars = await ethers.getContractAt("SCARS", scarsAddress);

  // 1. Report a new threat
  const reportTx = await scars.reportThreat(
    "device-1234",
    "DDoS",
    2, // Severity: 2 = High
    85 // Anomaly Score
  );
  await reportTx.wait();
  console.log("✅ Threat reported.");

  // 2. Get all threats for device
  const threats = await scars.getThreats("device-1234");
  console.log("📄 Threats for device-1234:", threats);

  // 3. Mitigate the first threat (index 0)
  const mitigateTx = await scars.mitigateThreat("device-1234", 0);
  await mitigateTx.wait();
  console.log("✅ Threat mitigated.");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
// This script interacts with the SCARS contract to report, retrieve, and mitigate threats.
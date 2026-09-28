import fs from "fs";

const artifactPath = "artifacts/contracts/SCARS.sol/SCARS.json";
const outputPath = "contracts/abi/scars_abi.json";

const artifact = JSON.parse(fs.readFileSync(artifactPath, "utf8"));
const abi = artifact.abi;

fs.writeFileSync(outputPath, JSON.stringify(abi, null, 2));
console.log(`✅ ABI saved to ${outputPath}`);

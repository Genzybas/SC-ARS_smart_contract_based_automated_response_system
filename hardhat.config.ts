import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import * as dotenv from "dotenv";
import "@nomicfoundation/hardhat-verify";

dotenv.config();

const config: HardhatUserConfig = {
  solidity: "0.8.28",
  networks: {
    localhost: {
      url: "http://127.0.0.1:8545",
    },
    sepolia: {
      url: `https://eth-sepolia.g.alchemy.com/v2/${process.env.ALCHEMY_RPC_URL}`,
      accounts: [`0x${process.env.PRIVATE_KEY as string}`],
    },
  },
  sourcify: {
  enabled: true
},
  etherscan: {
    apiKey: process.env.ETHERSCAN_API_KEY,
  },
};

export default config;
// this is the Hardhat configuration file for deploying and verifying smart contracts on the Ethereum Sepolia testnet. It includes the necessary imports, environment variable loading, and network configurations for local and Sepolia netwoks.
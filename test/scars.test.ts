import { expect } from "chai";
import { ethers } from "hardhat";

describe("SCARS Contract", function () {
  let SCARS, scars: any, owner: any, addr1: any;

  beforeEach(async function () {
    SCARS = await ethers.getContractFactory("SCARS");
    [owner, addr1] = await ethers.getSigners();
    scars = await SCARS.deploy();
    await scars.waitForDeployment();
  });

  it("should allow reporting a threat", async function () {
    const tx = await scars.reportThreat("device001", "DDoS", 2, 95);
    await tx.wait();

    const threats = await scars.getThreats("device001");
    expect(threats.length).to.equal(1);
    expect(threats[0].threatType).to.equal("DDoS");
  });

  it("should allow only admin to mitigate threat", async function () {
    await scars.reportThreat("device002", "Malware", 1, 70);

    await expect(
      scars.connect(addr1).mitigateThreat("device002", 0)
    ).to.be.revertedWith("Not authorized");

    const tx = await scars.mitigateThreat("device002", 0);
    await tx.wait();

    const threats = await scars.getThreats("device002");
    expect(threats[0].mitigated).to.be.true;
  });

  it("should revert if index is invalid", async function () {
    await expect(
      scars.mitigateThreat("device003", 0)
    ).to.be.revertedWith("Invalid index");
  });
});

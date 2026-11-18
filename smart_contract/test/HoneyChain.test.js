const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("HoneyChain Smart Contract", function () {
  let HoneyChain, honeyChain, owner, addr1;

  const testBatchId = "HC-2024-TEST01";
  // Sample 32-byte sha256 hash (in hex)
  const testHash = "0x4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a";
  const alteredHash = "0x1111111111111111111111111111111111111111111111111111111111111111";

  beforeEach(async function () {
    [owner, addr1] = await ethers.getSigners();
    HoneyChain = await ethers.getContractFactory("HoneyChain");
    honeyChain = await HoneyChain.deploy();
    await honeyChain.waitForDeployment();
  });

  describe("Deployment", function () {
    it("Should set the correct deployer as owner", async function () {
      expect(await honeyChain.owner()).to.equal(owner.address);
    });

    it("Should start with 0 total batches", async function () {
      expect(await honeyChain.totalBatches()).to.equal(0);
    });
  });

  describe("Batch Registration", function () {
    it("Should allow the owner to register a new honey batch", async function () {
      await expect(honeyChain.registerBatch(testBatchId, testHash))
        .to.emit(honeyChain, "BatchRegistered")
        .withArgs(testBatchId, testHash, owner.address, (await ethers.provider.getBlock('latest')).timestamp + 1);

      expect(await honeyChain.totalBatches()).to.equal(1);
      expect(await honeyChain.isBatchRegistered(testBatchId)).to.be.true;
      expect(await honeyChain.getBatchHash(testBatchId)).to.equal(testHash);
    });

    it("Should reject registration if called by non-owner", async function () {
      await expect(
        honeyChain.connect(addr1).registerBatch(testBatchId, testHash)
      ).to.be.revertedWith("HoneyChain: caller is not the owner");
    });

    it("Should reject registration if batchId is empty", async function () {
      await expect(
        honeyChain.registerBatch("", testHash)
      ).to.be.revertedWith("HoneyChain: batchId cannot be empty");
    });

    it("Should reject duplicate registration of the same batch ID", async function () {
      await honeyChain.registerBatch(testBatchId, testHash);
      await expect(
        honeyChain.registerBatch(testBatchId, testHash)
      ).to.be.revertedWith("HoneyChain: batch already registered");
    });
  });

  describe("Batch Verification", function () {
    beforeEach(async function () {
      await honeyChain.registerBatch(testBatchId, testHash);
    });

    it("Should return true when hash matches", async function () {
      const [isVerified, isRegistered] = await honeyChain.verifyBatch(testBatchId, testHash);
      expect(isRegistered).to.be.true;
      expect(isVerified).to.be.true;
    });

    it("Should return false when hash does not match (data tampered)", async function () {
      const [isVerified, isRegistered] = await honeyChain.verifyBatch(testBatchId, alteredHash);
      expect(isRegistered).to.be.true;
      expect(isVerified).to.be.false;
    });

    it("Should return false when batch is not registered", async function () {
      const [isVerified, isRegistered] = await honeyChain.verifyBatch("NON-EXISTENT", testHash);
      expect(isRegistered).to.be.false;
      expect(isVerified).to.be.false;
    });
  });
});


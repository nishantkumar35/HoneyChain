// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title HoneyChain
 * @dev Smart contract for registering and verifying honey batch hashes.
 *      Deployed on a local Hardhat blockchain for the HoneyChain college project.
 *
 * Design principles:
 * - Only batch IDs and SHA-256 hashes are stored on-chain.
 * - Full batch details remain in Django/SQLite.
 * - Only the contract owner (deployer) can register batches.
 * - Any caller can verify a batch (public read access).
 * - Once registered, a batch hash CANNOT be overwritten.
 */
contract HoneyChain {

    // =========================================================================
    // State Variables
    // =========================================================================

    /// @dev The account that deployed this contract (the deployer / beekeeper app)
    address public owner;

    /// @dev Maps batch ID string → stored hash (hex bytes32)
    mapping(string => bytes32) private batchHashes;

    /// @dev Track which batch IDs have been registered (to prevent overwriting)
    mapping(string => bool) private batchRegistered;

    /// @dev Total number of registered batches
    uint256 public totalBatches;

    // =========================================================================
    // Events
    // =========================================================================

    /// @notice Emitted when a new batch is registered
    event BatchRegistered(string indexed batchId, bytes32 hash, address registeredBy, uint256 timestamp);

    // =========================================================================
    // Modifiers
    // =========================================================================

    /// @dev Restrict function to contract owner only
    modifier onlyOwner() {
        require(msg.sender == owner, "HoneyChain: caller is not the owner");
        _;
    }

    // =========================================================================
    // Constructor
    // =========================================================================

    constructor() {
        owner = msg.sender;
    }

    // =========================================================================
    // Write Functions
    // =========================================================================

    /**
     * @notice Register a honey batch's SHA-256 hash on the blockchain.
     * @dev    Can only be called by the contract owner.
     *         Once registered, the hash cannot be changed.
     * @param  batchId  The unique batch identifier (e.g., "HC-2024-A3F9")
     * @param  hashHex  The SHA-256 hash as a hex string with 0x prefix
     */
    function registerBatch(string calldata batchId, bytes32 hashHex) external onlyOwner {
        require(bytes(batchId).length > 0, "HoneyChain: batchId cannot be empty");
        require(!batchRegistered[batchId], "HoneyChain: batch already registered");

        batchHashes[batchId]     = hashHex;
        batchRegistered[batchId] = true;
        totalBatches            += 1;

        emit BatchRegistered(batchId, hashHex, msg.sender, block.timestamp);
    }

    // =========================================================================
    // Read Functions
    // =========================================================================

    /**
     * @notice Verify whether a given hash matches the on-chain record.
     * @param  batchId       The batch identifier to verify
     * @param  hashToVerify  The hash to compare against the stored hash
     * @return isVerified    True if the hashes match, false otherwise
     * @return isRegistered  True if the batch has been registered
     */
    function verifyBatch(
        string calldata batchId,
        bytes32 hashToVerify
    ) external view returns (bool isVerified, bool isRegistered) {
        isRegistered = batchRegistered[batchId];
        if (!isRegistered) {
            return (false, false);
        }
        isVerified = (batchHashes[batchId] == hashToVerify);
    }

    /**
     * @notice Get the hash stored on-chain for a batch.
     * @param  batchId  The batch identifier
     * @return The stored bytes32 hash (zero bytes if not registered)
     */
    function getBatchHash(string calldata batchId) external view returns (bytes32) {
        return batchHashes[batchId];
    }

    /**
     * @notice Check if a batch ID has been registered.
     * @param  batchId  The batch identifier
     * @return True if registered, false otherwise
     */
    function isBatchRegistered(string calldata batchId) external view returns (bool) {
        return batchRegistered[batchId];
    }
}


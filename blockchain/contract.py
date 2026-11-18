"""
blockchain/contract.py — Loads the deployed HoneyChain smart contract ABI
and creates a Web3 contract instance.

This module handles connection to the local Hardhat blockchain node.
"""

import json
import logging
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)

# Module-level cache for the Web3 instance and contract
_web3 = None
_contract = None


def get_web3():
    """
    Return a connected Web3 instance (connected to Hardhat local node).
    Returns None if web3 is not installed or connection fails.
    """
    global _web3

    if _web3 is not None:
        return _web3

    try:
        from web3 import Web3
    except ImportError:
        logger.warning(
            "web3 package is not installed. "
            "Install it with: pip install web3\n"
            "Blockchain features will be disabled until web3 is installed."
        )
        return None

    node_url = settings.BLOCKCHAIN_NODE_URL
    try:
        w3 = Web3(Web3.HTTPProvider(node_url))
        if w3.is_connected():
            _web3 = w3
            logger.info(f"Connected to blockchain node: {node_url}")
            return _web3
        else:
            logger.error(
                f"Could not connect to blockchain node at {node_url}. "
                "Make sure Hardhat is running: npx hardhat node"
            )
            return None
    except Exception as e:
        logger.error(f"Web3 connection error: {e}")
        return None


def get_contract():
    """
    Return the deployed HoneyChain contract instance.
    Returns None if connection or ABI loading fails.
    """
    global _contract

    if _contract is not None:
        return _contract

    w3 = get_web3()
    if w3 is None:
        return None

    contract_address = settings.CONTRACT_ADDRESS
    if not contract_address:
        logger.error(
            "CONTRACT_ADDRESS is not set in .env. "
            "Deploy the contract first: cd smart_contract && npx hardhat run scripts/deploy.js --network localhost"
        )
        return None

    abi_path = settings.CONTRACT_ABI_PATH
    if not Path(abi_path).exists():
        logger.error(
            f"Contract ABI file not found at {abi_path}. "
            "Compile the contract first: cd smart_contract && npx hardhat compile"
        )
        return None

    try:
        with open(abi_path, 'r') as f:
            artifact = json.load(f)
        abi = artifact['abi']
        _contract = w3.eth.contract(address=contract_address, abi=abi)
        logger.info(f"Contract loaded at address: {contract_address}")
        return _contract
    except Exception as e:
        logger.error(f"Failed to load contract: {e}")
        return None


def is_blockchain_available() -> bool:
    """Quick check: is the blockchain node reachable?"""
    w3 = get_web3()
    return w3 is not None and w3.is_connected()


def reset_connection():
    """
    Reset the cached Web3 and contract instances.
    Call this if you change the node URL or contract address at runtime.
    """
    global _web3, _contract
    _web3 = None
    _contract = None


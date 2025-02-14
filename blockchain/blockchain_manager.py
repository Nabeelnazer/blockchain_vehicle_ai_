import hashlib
from datetime import datetime
import json
import os
from web3 import Web3
from eth_account import Account
import subprocess

class BlockchainManager:
    def __init__(self, contract_address=None, contract_abi=None):
        """
        Initialize blockchain manager with contract details
        """
        # Connect to local Hardhat node
        self.w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
        
        # Verify connection
        if not self.w3.is_connected():
            raise ConnectionError("Unable to connect to Hardhat Ethereum node")
        
        # Load contract details
        if contract_address and contract_abi:
            self.contract = self.w3.eth.contract(
                address=contract_address, 
                abi=contract_abi
            )
        else:
            # Try to load from deployment info
            deployment_path = os.path.join(
                os.path.dirname(__file__), 
                '..', 
                'deployment-info.json'
            )
            if os.path.exists(deployment_path):
                with open(deployment_path, 'r') as f:
                    deployment_info = json.load(f)
                    self.contract = self.w3.eth.contract(
                        address=deployment_info['address'], 
                        abi=deployment_info['abi']
                    )
            else:
                self.contract = None
        
        # Set default account (first Hardhat account)
        self.w3.eth.default_account = self.w3.eth.accounts[0]
    
    def log_vehicle_entry(self, plate_number, confidence=0.9):
        """
        Log vehicle entry to blockchain
        """
        if not self.contract:
            raise ValueError("Contract not initialized")
        
        try:
            # Estimate gas
            gas_estimate = self.contract.functions.logVehicleEntry(
                plate_number, 
                int(confidence * 100)
            ).estimate_gas()
            
            # Send transaction
            tx_hash = self.contract.functions.logVehicleEntry(
                plate_number, 
                int(confidence * 100)
            ).transact({'gas': gas_estimate})
            
            # Wait for transaction receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                'transaction_hash': tx_receipt.transactionHash.hex(),
                'block_number': tx_receipt.blockNumber
            }
        except Exception as e:
            print(f"Error logging vehicle entry: {e}")
            return None
    
    def log_vehicle_exit(self, plate_number):
        """
        Log vehicle exit to blockchain
        """
        if not self.contract:
            raise ValueError("Contract not initialized")
        
        try:
            # Estimate gas
            gas_estimate = self.contract.functions.logVehicleExit(
                plate_number
            ).estimate_gas()
            
            # Send transaction
            tx_hash = self.contract.functions.logVehicleExit(
                plate_number
            ).transact({'gas': gas_estimate})
            
            # Wait for transaction receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                'transaction_hash': tx_receipt.transactionHash.hex(),
                'block_number': tx_receipt.blockNumber
            }
        except Exception as e:
            print(f"Error logging vehicle exit: {e}")
            return None
    
    def get_vehicle_entries(self, plate_number):
        """
        Retrieve vehicle entries from blockchain
        """
        if not self.contract:
            raise ValueError("Contract not initialized")
        
        try:
            entries = self.contract.functions.getVehicleEntries(plate_number).call()
            return entries
        except Exception as e:
            print(f"Error retrieving vehicle entries: {e}")
            return []
    
    def verify_vehicle_entry(self, plate_number):
        """
        Check if a vehicle has been logged
        """
        entries = self.get_vehicle_entries(plate_number)
        return len(entries) > 0
    
    def get_entries_by_date_range(self, start_date=None, end_date=None):
        """
        Retrieve entries within a specific date range
        
        :param start_date: Optional start date (datetime or ISO format string)
        :param end_date: Optional end date (datetime or ISO format string)
        :return: Filtered entries
        """
        # Convert string dates to datetime if needed
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)
        
        filtered_entries = []
        entries = self.get_vehicle_entries(None)
        for entry in entries:
            if (start_date is None or entry['entry_timestamp'] >= start_date) and \
               (end_date is None or entry['entry_timestamp'] <= end_date):
                filtered_entries.append(entry)
        
        return filtered_entries
    
    def export_entries(self, filename=None):
        """
        Export all entries to a JSON file
        
        :param filename: Optional custom filename
        :return: Path to exported file
        """
        if not filename:
            filename = f"vehicle_entries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            entries = self.get_vehicle_entries(None)
            with open(filename, 'w') as f:
                json.dump(entries, f, indent=4)
            return filename
        except Exception as e:
            print(f"Error exporting entries: {e}")
            return None
    
    def get_entry_by_hash(self, transaction_hash):
        """
        Retrieve entry details by transaction hash
        """
        entries = self.get_vehicle_entries(None)
        for entry in entries:
            if entry['transaction_hash'] == transaction_hash:
                return entry
        return None

    @classmethod
    def from_deployment(cls, contract_address, contract_abi):
        """
        Create BlockchainManager from deployed contract
        """
        return cls(contract_address, contract_abi)

def setup_blockchain():
    """
    Setup blockchain environment
    """
    try:
        # Compile contracts
        subprocess.run(['npx', 'hardhat', 'compile'], check=True)
        
        # Deploy contract
        subprocess.run(['npx', 'hardhat', 'run', 'blockchain/scripts/deploy.js'], check=True)
        
        # Initialize blockchain manager
        return BlockchainManager()
    except Exception as e:
        print(f"Blockchain setup failed: {e}")
        return None

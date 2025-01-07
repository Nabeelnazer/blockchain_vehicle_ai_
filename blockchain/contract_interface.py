from web3 import Web3
import json
import os
from datetime import datetime

class VehicleContractInterface:
    def __init__(self, 
                 contract_address,
                 abi_path='blockchain/contracts/VehicleRegistry.json',
                 provider_url='http://127.0.0.1:7545'):  # Ganache default URL
        
        # Connect to Ethereum
        self.w3 = Web3(Web3.HTTPProvider(provider_url))
        if not self.w3.is_connected():
            raise Exception("Failed to connect to Ethereum network")
        
        print(f"Connected to Ethereum network. Chain ID: {self.w3.eth.chain_id}")
        
        # Load contract ABI
        with open(abi_path) as f:
            contract_json = json.load(f)
            self.abi = contract_json['abi']
        
        # Initialize contract
        self.contract_address = Web3.to_checksum_address(contract_address)
        self.contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=self.abi
        )
        
        # Use the first account from Ganache (should match MetaMask)
        self.account = self.w3.eth.accounts[0]
        balance = self.w3.eth.get_balance(self.account)
        print(f"Using account: {self.account}")
        print(f"Account balance: {Web3.from_wei(balance, 'ether')} ETH")
    
    def register_vehicle_entry(self, entry_data, data_hash):
        """
        Register vehicle entry on blockchain
        """
        try:
            # Prepare transaction
            nonce = self.w3.eth.get_transaction_count(self.account)
            
            # Estimate gas
            gas_estimate = self.contract.functions.registerVehicleEntry(
                entry_data['plate_number'],
                entry_data['timestamp'],
                int(entry_data['confidence'] * 100),
                data_hash
            ).estimate_gas({'from': self.account})
            
            # Build transaction with estimated gas
            transaction = self.contract.functions.registerVehicleEntry(
                entry_data['plate_number'],
                entry_data['timestamp'],
                int(entry_data['confidence'] * 100),
                data_hash
            ).build_transaction({
                'from': self.account,
                'gas': gas_estimate,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': nonce,
            })
            
            # Sign transaction with private key from environment variable
            private_key = os.getenv('ETH_PRIVATE_KEY')
            if not private_key:
                raise Exception("ETH_PRIVATE_KEY environment variable not set")
            
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction, 
                private_key=private_key
            )
            
            # Send transaction and wait for receipt
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            print(f"Transaction sent: {tx_hash.hex()}")
            
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Transaction confirmed in block {tx_receipt['blockNumber']}")
            
            return {
                'transaction_hash': tx_receipt['transactionHash'].hex(),
                'block_number': tx_receipt['blockNumber'],
                'status': 'confirmed' if tx_receipt['status'] == 1 else 'failed',
                'gas_used': tx_receipt['gasUsed']
            }
            
        except Exception as e:
            print(f"Error in blockchain transaction: {str(e)}")
            return None
    
    def verify_vehicle_entry(self, plate_number, data_hash):
        """
        Verify vehicle entry on blockchain
        """
        try:
            return self.contract.functions.verifyVehicleEntry(
                plate_number,
                data_hash
            ).call()
        except Exception as e:
            print(f"Error verifying entry: {str(e)}")
            return False
    
    def get_vehicle_entries(self, plate_number):
        """
        Get all entries for a vehicle
        """
        try:
            return self.contract.functions.getVehicleEntries(plate_number).call()
        except Exception as e:
            print(f"Error getting vehicle entries: {str(e)}")
            return []
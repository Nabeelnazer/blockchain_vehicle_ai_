from web3 import Web3
from eth_account import Account
import json
import os
from dotenv import load_dotenv
import hashlib
import datetime

class BlockchainManager:
    def __init__(self):
        load_dotenv()
        # Connect to Ganache
        self.w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))  # Default Ganache port
        
        # Use the first account from Ganache (which has 300k test ETH)
        if not os.getenv('PRIVATE_KEY'):
            # Get the first account from Ganache
            accounts = self.w3.eth.accounts
            if accounts:
                self.account = self.w3.eth.account.from_key(
                    # This is a sample private key from Ganache, replace with your actual one
                    '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
                )
            else:
                raise Exception("No accounts found in Ganache")
        else:
            self.account = Account.from_key(os.getenv('PRIVATE_KEY'))
        
    def store_ocr_hash(self, plate_data):
        """Store plate detection hash on blockchain"""
        try:
            # Create hash of plate data
            data = {
                'plate': plate_data['text'],
                'timestamp': datetime.datetime.now().isoformat(),
                'confidence': str(plate_data['confidence'])
            }
            result_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
            
            # Prepare transaction
            transaction = {
                'from': self.account.address,
                'to': self.w3.eth.accounts[1],  # Send to second Ganache account
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 2000000,
                'gasPrice': self.w3.eth.gas_price,
                'value': self.w3.to_wei(0.001, 'ether'),  # Small transaction value
                'data': result_hash.encode()
            }
            
            # Sign and send transaction
            signed_txn = self.account.sign_transaction(transaction)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Add verification info
            receipt.verification_hash = result_hash
            receipt.balance = self.w3.from_wei(self.w3.eth.get_balance(self.account.address), 'ether')
            return receipt
            
        except Exception as e:
            raise Exception(f"Blockchain transaction failed: {str(e)}")

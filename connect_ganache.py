from web3 import Web3

# Connect to Ganache
ganache_url = 'http://127.0.0.1:7545'  # Replace with your Ganache RPC URL
w3 = Web3(Web3.HTTPProvider(ganache_url))

# Check if connected
if w3.is_connected():
    print("Connected to Ganache!")
else:
    print("Failed to connect to Ganache.") 
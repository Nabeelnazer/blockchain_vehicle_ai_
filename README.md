# blockchain_vehicle_ai
 using yolov8 for liscence plate detection
 paddle ocr for fetching data
integrating blockchain smartcontract for database.

## Blockchain Details
- Using Ganache local blockchain
- Each detected plate is hashed and stored on-chain
- Transactions include plate text, timestamp, and confidence
- Initial balance: 300k test ETH
- Automatic account setup using Ganache's first account

## Troubleshooting

1. If Ganache connection fails:
   - Ensure Ganache is running
   - Verify the RPC Server address
   - Check if the account has sufficient test ETH

2. If camera doesn't work:
   - Check camera permissions
   - Try different camera index (0, 1, etc.)
   - Verify IP camera URL if using one

## Contributing
Pull requests are welcome. For major changes, please open an issue first.

## License
MIT License

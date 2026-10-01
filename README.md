# blockchain_vehicle_ai
 using yolov8 for liscence plate detection
 paddle ocr for fetching data
integrating blockchain smartcontract for database.

## Running it
1. `pip install -r requirements.txt` and `npm ci`
2. Copy `.env.example` to `.env` and fill it in
3. Start a local chain: `npx hardhat node` (leave it running)
4. Deploy the contract to it: `npm run deploy`, which writes `deployment-info.json`
5. Dashboard: `streamlit run ui/app.py`. API: `python main.py` or `uvicorn api.main:app`

Without the node running, detections are still saved to SQLite; only the on-chain copy is skipped.

## Blockchain Details
- Local Hardhat node at `127.0.0.1:8545`; the app writes with its first account
- Only the deploying account may log entries and exits (`onlyOwner`)
- Each entry stores plate text, timestamp and OCR confidence on-chain

## Troubleshooting

1. If the blockchain connection fails:
   - Ensure `npx hardhat node` is running
   - Redeploy after restarting the node (`npm run deploy`): a fresh node has no contract

2. If camera doesn't work:
   - Check camera permissions
   - Try different camera index (0, 1, etc.)
   - Verify IP camera URL if using one

## Contributing
Pull requests are welcome. For major changes, please open an issue first.

## License
MIT License

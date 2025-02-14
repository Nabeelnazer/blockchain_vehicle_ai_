const hre = require("hardhat");
const fs = require('fs');
const path = require('path');

async function main() {
  // Get signers
  const [deployer] = await hre.ethers.getSigners();
  
  console.log("Deploying contracts with the account:", deployer.address);
  
  // Get the contract factory
  const VehicleRegistry = await hre.ethers.getContractFactory("VehicleRegistry");
  
  // Deploy the contract
  const vehicleRegistry = await VehicleRegistry.deploy();
  
  // Wait for deployment
  await vehicleRegistry.waitForDeployment();
  
  const contractAddress = await vehicleRegistry.getAddress();
  console.log("VehicleRegistry deployed to:", contractAddress);
  
  // Save contract address and ABI to a file
  const deploymentPath = path.join(__dirname, '..', '..', 'deployment-info.json');
  const contractInfo = {
    address: contractAddress,
    abi: JSON.parse(JSON.stringify(vehicleRegistry.interface.fragments))
  };
  
  fs.writeFileSync(deploymentPath, JSON.stringify(contractInfo, null, 2));
  console.log(`Deployment info saved to ${deploymentPath}`);
}

// Recommended pattern to handle async errors
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  }); 
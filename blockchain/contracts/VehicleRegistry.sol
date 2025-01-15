// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VehicleRegistry {
    struct VehicleEntry {
        string plateNumber;
        string timestamp;
        uint256 confidence;
        string dataHash;
        bool exists;
    }
    
    mapping(string => VehicleEntry[]) public vehicleEntries;
    mapping(string => bool) public registeredHashes;
    
    event VehicleRegistered(
        string plateNumber,
        string timestamp,
        uint256 confidence,
        string dataHash
    );
    
    function registerVehicleEntry(
        string memory plateNumber,
        string memory timestamp,
        uint256 confidence,
        string memory dataHash
    ) public returns (bool) {
        require(!registeredHashes[dataHash], "Entry already exists");
        
        VehicleEntry memory entry = VehicleEntry({
            plateNumber: plateNumber,
            timestamp: timestamp,
            confidence: confidence,
            dataHash: dataHash,
            exists: true
        });
        
        vehicleEntries[plateNumber].push(entry);
        registeredHashes[dataHash] = true;
        
        emit VehicleRegistered(plateNumber, timestamp, confidence, dataHash);
        
        return true;
    }
    
    function verifyVehicleEntry(
        string memory plateNumber,
        string memory dataHash
    ) public view returns (bool) {
        return registeredHashes[dataHash];
    }
    
    function getVehicleEntries(
        string memory plateNumber
    ) public view returns (VehicleEntry[] memory) {
        return vehicleEntries[plateNumber];
    }
} 
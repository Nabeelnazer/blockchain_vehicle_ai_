// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract VehicleRegistry {
    // Struct to represent a vehicle entry
    struct VehicleEntry {
        address owner;
        string plateNumber;
        uint256 entryTimestamp;
        uint256 exitTimestamp;
        bool isActive;
        uint256 confidence;
    }

    // Events for tracking vehicle entries
    event VehicleEntered(
        address indexed owner, 
        string plateNumber, 
        uint256 entryTimestamp
    );
    
    event VehicleExited(
        address indexed owner, 
        string plateNumber, 
        uint256 exitTimestamp
    );

    // Mapping to store vehicle entries
    mapping(string => VehicleEntry[]) public vehicleEntries;
    
    // Mapping to track current active entries
    mapping(string => bool) public activeVehicles;

    // Owner of the contract
    address public owner;

    // Constructor
    constructor() {
        owner = msg.sender;
    }

    // Modifier to restrict access to owner
    modifier onlyOwner() {
        require(msg.sender == owner, "Not authorized");
        _;
    }

    // Function to log vehicle entry
    function logVehicleEntry(
        string memory _plateNumber, 
        uint256 _confidence
    ) public returns (uint256) {
        // Prevent re-entry of active vehicles
        require(!activeVehicles[_plateNumber], "Vehicle already in parking");

        VehicleEntry memory newEntry = VehicleEntry({
            owner: msg.sender,
            plateNumber: _plateNumber,
            entryTimestamp: block.timestamp,
            exitTimestamp: 0,
            isActive: true,
            confidence: _confidence
        });

        // Add entry to vehicle's history
        vehicleEntries[_plateNumber].push(newEntry);
        
        // Mark vehicle as active
        activeVehicles[_plateNumber] = true;

        // Emit event
        emit VehicleEntered(msg.sender, _plateNumber, block.timestamp);

        // Return the index of the new entry
        return vehicleEntries[_plateNumber].length - 1;
    }

    // Function to log vehicle exit
    function logVehicleExit(string memory _plateNumber) public {
        require(activeVehicles[_plateNumber], "Vehicle not in parking");

        // Find the last active entry for this plate number
        uint256 lastEntryIndex = vehicleEntries[_plateNumber].length - 1;
        VehicleEntry storage entry = vehicleEntries[_plateNumber][lastEntryIndex];
        
        // Update exit details
        entry.exitTimestamp = block.timestamp;
        entry.isActive = false;

        // Mark vehicle as no longer active
        activeVehicles[_plateNumber] = false;

        // Emit exit event
        emit VehicleExited(msg.sender, _plateNumber, block.timestamp);
    }

    // Function to get vehicle entry history
    function getVehicleEntries(string memory _plateNumber) 
        public 
        view 
        returns (VehicleEntry[] memory) 
    {
        return vehicleEntries[_plateNumber];
    }

    // Function to check if a vehicle is currently in parking
    function isVehicleActive(string memory _plateNumber) 
        public 
        view 
        returns (bool) 
    {
        return activeVehicles[_plateNumber];
    }
} 
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VehicleLog {
    struct VehicleEntry {
        string plateNumber;
        uint256 timestamp;
    }

    VehicleEntry[] public entries;

    function addEntry(string memory plateNumber) public {
        entries.push(VehicleEntry(plateNumber, block.timestamp));
    }

    function getEntries() public view returns (VehicleEntry[] memory) {
        return entries;
    }
}

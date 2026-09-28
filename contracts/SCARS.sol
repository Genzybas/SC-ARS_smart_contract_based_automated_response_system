// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract SCARS {
    struct ThreatReport {
        string deviceID;
        uint256 timestamp;
        string threatType;
        uint8 severity; // 0 = Low, 1 = Medium, 2 = High
        uint256 anomalyScore;
        bool mitigated;
    }

    address public admin;

    // Mapping from device ID hash to threat reports
    mapping(bytes32 => ThreatReport[]) private deviceThreats;

    event ThreatReported(
        string deviceID,
        uint256 timestamp,
        string threatType,
        uint8 severity,
        uint256 anomalyScore
    );

    event ThreatMitigated(string deviceID, uint256 index);

    modifier onlyAdmin() {
        require(msg.sender == admin, "Not authorized");
        _;
    }

    constructor() {
        admin = msg.sender;
    }

    function reportThreat(
        string memory _deviceID,
        string memory _threatType,
        uint8 _severity,
        uint256 _anomalyScore
    ) external {
        bytes32 deviceHash = keccak256(abi.encodePacked(_deviceID));
        ThreatReport memory report = ThreatReport({
            deviceID: _deviceID,
            timestamp: block.timestamp,
            threatType: _threatType,
            severity: _severity,
            anomalyScore: _anomalyScore,
            mitigated: false
        });

        deviceThreats[deviceHash].push(report);

        emit ThreatReported(_deviceID, block.timestamp, _threatType, _severity, _anomalyScore);
    }

    function mitigateThreat(string memory _deviceID, uint256 _index) external onlyAdmin {
        bytes32 deviceHash = keccak256(abi.encodePacked(_deviceID));
        require(_index < deviceThreats[deviceHash].length, "Invalid index");
        deviceThreats[deviceHash][_index].mitigated = true;

        emit ThreatMitigated(_deviceID, _index);
    }

    function getThreats(string memory _deviceID) external view returns (ThreatReport[] memory) {
        bytes32 deviceHash = keccak256(abi.encodePacked(_deviceID));
        return deviceThreats[deviceHash];
    }
}













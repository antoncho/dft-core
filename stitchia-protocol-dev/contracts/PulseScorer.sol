// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";

/// @title PulseScorer
/// @notice Lightweight scoring oracle to aggregate participation metrics for Stitchia DAO governance.
/// @dev Designed as a pluggable component so alternative scoring logic can be deployed later.
contract PulseScorer is AccessControl {
    bytes32 public constant CONFIG_ROLE = keccak256("CONFIG_ROLE");
    bytes32 public constant FEEDER_ROLE = keccak256("FEEDER_ROLE");

    struct MetricConfig {
        string label;   // Human readable label for dashboards.
        uint32 weight;  // Relative weight (0-1e6 range recommended).
        bool enabled;   // Toggle without removing historical data.
    }

    /// @dev metric id (bytes32) => config
    mapping(bytes32 => MetricConfig) private _metrics;

    /// @dev member => metric id => last submitted score value
    mapping(address => mapping(bytes32 => uint256)) private _memberScores;

    event MetricConfigured(bytes32 indexed metricId, string label, uint32 weight, bool enabled);
    event MetricRemoved(bytes32 indexed metricId);
    event ScoreSubmitted(address indexed member, bytes32 indexed metricId, uint256 value, address indexed feeder);

    constructor(address admin) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(CONFIG_ROLE, admin);
        _grantRole(FEEDER_ROLE, admin);
    }

    /// @notice Register or update a metric configuration.
    function configureMetric(
        bytes32 metricId,
        string calldata label,
        uint32 weight,
        bool enabled
    ) external onlyRole(CONFIG_ROLE) {
        require(metricId != bytes32(0), "PULSE: EMPTY_ID");
        require(bytes(label).length > 0, "PULSE: EMPTY_LABEL");

        _metrics[metricId] = MetricConfig({label: label, weight: weight, enabled: enabled});
        emit MetricConfigured(metricId, label, weight, enabled);
    }

    /// @notice Permanently delete a metric (keeps historical member scores untouched).
    function removeMetric(bytes32 metricId) external onlyRole(CONFIG_ROLE) {
        delete _metrics[metricId];
        emit MetricRemoved(metricId);
    }

    /// @notice Submit a new score value for a member / metric pair.
    function submitScore(
        address member,
        bytes32 metricId,
        uint256 value
    ) external onlyRole(FEEDER_ROLE) {
        MetricConfig memory config = _metrics[metricId];
        require(bytes(config.label).length > 0, "PULSE: UNKNOWN_METRIC");
        require(config.enabled, "PULSE: METRIC_DISABLED");

        _memberScores[member][metricId] = value;
        emit ScoreSubmitted(member, metricId, value, _msgSender());
    }

    /// @notice Return the raw score for a member/metric pair.
    function rawScore(address member, bytes32 metricId) external view returns (uint256) {
        return _memberScores[member][metricId];
    }

    /// @notice Retrieve the configuration for a metric id.
    function metric(bytes32 metricId) external view returns (MetricConfig memory) {
        return _metrics[metricId];
    }

    /// @notice Compute a weighted aggregate score for a member using the provided metric ids.
    /// @return totalScore Sum of (score * weight) for each enabled metric.
    /// @return totalWeight Sum of weights used (only enabled metrics are counted).
    function computeAggregate(address member, bytes32[] calldata metricIds)
        external
        view
        returns (uint256 totalScore, uint256 totalWeight)
    {
        uint256 idsLength = metricIds.length;
        for (uint256 i = 0; i < idsLength; ++i) {
            MetricConfig memory config = _metrics[metricIds[i]];
            if (!config.enabled || bytes(config.label).length == 0) {
                continue; // ignore disabled or unknown metrics silently
            }

            totalScore += _memberScores[member][metricIds[i]] * uint256(config.weight);
            totalWeight += uint256(config.weight);
        }
    }

    /// @dev required override for AccessControl metadata.
    function supportsInterface(bytes4 interfaceId)
        public
        view
        override
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}

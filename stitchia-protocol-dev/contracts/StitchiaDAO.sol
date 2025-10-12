// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

interface IGenesisNFT {
    function balanceOf(address owner) external view returns (uint256);
}

interface IPulseScorer {
    function computeAggregate(address member, bytes32[] calldata metricIds)
        external
        view
        returns (uint256 totalScore, uint256 totalWeight);
}

/// @title StitchiaDAO Governance Skeleton
/// @notice Provides a light-weight proposal + voting framework wired into Genesis NFTs and Pulse scoring.
/// @dev This contract focuses on metadata + vote tracking. Execution hooks can be layered on by inheriting.
contract StitchiaDAO is AccessControl {
    using Counters for Counters.Counter;

    bytes32 public constant PROPOSER_ROLE = keccak256("PROPOSER_ROLE");
    bytes32 public constant EXECUTOR_ROLE = keccak256("EXECUTOR_ROLE");
    bytes32 public constant CONFIG_ROLE = keccak256("CONFIG_ROLE");

    enum ProposalStatus {
        Draft,
        Active,
        Passed,
        Rejected,
        Executed,
        Cancelled
    }

    struct Proposal {
        address proposer;
        string title;
        string metadataURI; // Off-chain rich description (IPFS / HTTPS).
        uint64 startBlock;
        uint64 endBlock;
        ProposalStatus status;
        uint256 forVotes;
        uint256 againstVotes;
    }

    struct Vote {
        bool cast;
        bool support;
        uint256 weight;
    }

    Counters.Counter private _proposalIds;

    mapping(uint256 => Proposal) private _proposals;
    mapping(uint256 => mapping(address => Vote)) private _votes;

    bytes32[] public defaultMetricSet;

    uint64 public votingDelay = 1;   // blocks
    uint64 public votingPeriod = 40; // blocks
    uint256 public quorumVotes = 1;  // minimum FOR votes required

    IGenesisNFT public immutable genesisNFT;
    IPulseScorer public pulseScorer;

    event ProposalCreated(uint256 indexed proposalId, address indexed proposer, string title, string metadataURI);
    event ProposalStatusChanged(uint256 indexed proposalId, ProposalStatus indexed previousStatus, ProposalStatus indexed newStatus);
    event VoteCast(uint256 indexed proposalId, address indexed voter, bool support, uint256 weight);
    event MetricsConfigured(bytes32[] metrics);
    event VotingParametersUpdated(uint64 votingDelay, uint64 votingPeriod, uint256 quorumVotes);
    event PulseScorerUpdated(address indexed scorer);

    constructor(address admin, address genesis, address scorer) {
        require(admin != address(0), "DAO: ADMIN_REQUIRED");
        require(genesis != address(0), "DAO: GENESIS_REQUIRED");

        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(PROPOSER_ROLE, admin);
        _grantRole(EXECUTOR_ROLE, admin);
        _grantRole(CONFIG_ROLE, admin);

        genesisNFT = IGenesisNFT(genesis);
        pulseScorer = IPulseScorer(scorer);
    }

    // -------------------- Proposal lifecycle --------------------

    function createProposal(string calldata title, string calldata metadataURI)
        external
        onlyRole(PROPOSER_ROLE)
        returns (uint256 proposalId)
    {
        require(bytes(title).length > 0, "DAO: TITLE_REQUIRED");

        _proposalIds.increment();
        proposalId = _proposalIds.current();

        uint64 start = uint64(block.number) + votingDelay;
        uint64 end = start + votingPeriod;

        Proposal storage proposal = _proposals[proposalId];
        proposal.proposer = _msgSender();
        proposal.title = title;
        proposal.metadataURI = metadataURI;
        proposal.startBlock = start;
        proposal.endBlock = end;
        proposal.status = ProposalStatus.Draft;

        emit ProposalCreated(proposalId, _msgSender(), title, metadataURI);
    }

    function activateProposal(uint256 proposalId) external {
        Proposal storage proposal = _requireProposal(proposalId);
        require(_msgSender() == proposal.proposer || hasRole(CONFIG_ROLE, _msgSender()), "DAO: NOT_AUTHORISED");
        require(proposal.status == ProposalStatus.Draft, "DAO: NOT_DRAFT");
        require(block.number >= proposal.startBlock, "DAO: VOTING_NOT_STARTED");

        _setStatus(proposalId, ProposalStatus.Active);
    }

    function cancelProposal(uint256 proposalId) external {
        Proposal storage proposal = _requireProposal(proposalId);
        require(_msgSender() == proposal.proposer || hasRole(CONFIG_ROLE, _msgSender()), "DAO: NOT_AUTHORISED");
        require(
            proposal.status == ProposalStatus.Draft || proposal.status == ProposalStatus.Active,
            "DAO: NOT_CANCELLABLE"
        );

        _setStatus(proposalId, ProposalStatus.Cancelled);
    }

    // -------------------- Voting --------------------

    function castVote(uint256 proposalId, bool support) external {
        Proposal storage proposal = _requireProposal(proposalId);
        require(proposal.status == ProposalStatus.Active, "DAO: NOT_ACTIVE");
        require(block.number <= proposal.endBlock, "DAO: VOTING_FINISHED");

        Vote storage ballot = _votes[proposalId][_msgSender()];
        require(!ballot.cast, "DAO: ALREADY_VOTED");

        uint256 weight = _votingWeight(_msgSender());
        require(weight > 0, "DAO: NO_WEIGHT");

        ballot.cast = true;
        ballot.support = support;
        ballot.weight = weight;

        if (support) {
            proposal.forVotes += weight;
        } else {
            proposal.againstVotes += weight;
        }

        emit VoteCast(proposalId, _msgSender(), support, weight);
    }

    function finalize(uint256 proposalId) external {
        Proposal storage proposal = _requireProposal(proposalId);
        require(proposal.status == ProposalStatus.Active, "DAO: NOT_ACTIVE");
        require(block.number > proposal.endBlock, "DAO: VOTING_ONGOING");

        if (proposal.forVotes >= quorumVotes && proposal.forVotes > proposal.againstVotes) {
            _setStatus(proposalId, ProposalStatus.Passed);
        } else {
            _setStatus(proposalId, ProposalStatus.Rejected);
        }
    }

    function markExecuted(uint256 proposalId) external onlyRole(EXECUTOR_ROLE) {
        Proposal storage proposal = _requireProposal(proposalId);
        require(proposal.status == ProposalStatus.Passed, "DAO: NOT_PASSED");
        _setStatus(proposalId, ProposalStatus.Executed);
    }

    // -------------------- Configuration --------------------

    function setDefaultMetrics(bytes32[] calldata metrics) external onlyRole(CONFIG_ROLE) {
        delete defaultMetricSet;
        for (uint256 i = 0; i < metrics.length; ++i) {
            defaultMetricSet.push(metrics[i]);
        }
        emit MetricsConfigured(metrics);
    }

    function setVotingParameters(uint64 delay, uint64 period, uint256 quorum) external onlyRole(CONFIG_ROLE) {
        require(period > 0, "DAO: PERIOD_REQUIRED");
        votingDelay = delay;
        votingPeriod = period;
        quorumVotes = quorum;
        emit VotingParametersUpdated(delay, period, quorum);
    }

    function setPulseScorer(address scorer) external onlyRole(CONFIG_ROLE) {
        pulseScorer = IPulseScorer(scorer);
        emit PulseScorerUpdated(scorer);
    }

    // -------------------- Views --------------------

    function proposal(uint256 proposalId) external view returns (Proposal memory snapshot) {
        Proposal storage stored = _proposals[proposalId];
        require(stored.proposer != address(0), "DAO: UNKNOWN_PROPOSAL");
        snapshot = stored;
    }

    function voteReceipt(uint256 proposalId, address voter) external view returns (Vote memory) {
        return _votes[proposalId][voter];
    }

    function proposalCount() external view returns (uint256) {
        return _proposalIds.current();
    }

    // -------------------- Internal helpers --------------------

    function _votingWeight(address account) internal view returns (uint256 weight) {
        weight = genesisNFT.balanceOf(account);

        if (address(pulseScorer) != address(0) && defaultMetricSet.length > 0) {
            (uint256 totalScore, uint256 totalWeight) = pulseScorer.computeAggregate(account, defaultMetricSet);
            if (totalWeight > 0) {
                // Normalize to avoid overweighting metrics: convert to pseudo tokens (score / weight sum).
                weight += totalScore / totalWeight;
            }
        }
    }

    function _requireProposal(uint256 proposalId) internal view returns (Proposal storage proposalRef) {
        proposalRef = _proposals[proposalId];
        require(proposalRef.proposer != address(0), "DAO: UNKNOWN_PROPOSAL");
        return proposalRef;
    }

    function _setStatus(uint256 proposalId, ProposalStatus next) internal {
        Proposal storage proposal = _proposals[proposalId];
        ProposalStatus previous = proposal.status;
        proposal.status = next;
        emit ProposalStatusChanged(proposalId, previous, next);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}

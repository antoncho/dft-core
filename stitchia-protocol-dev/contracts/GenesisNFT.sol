// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/// @title Stitchia Genesis NFT
/// @notice Minimal ERC-721 implementation used to anchor Spiral roles for Stitchia members.
/// @dev This contract purposefully exposes only the primitives required by the DAO stack.
contract GenesisNFT is ERC721URIStorage, AccessControl {
    using Counters for Counters.Counter;

    /// @notice Role that can mint new Genesis NFTs.
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");

    /// @notice Role that can update token level metadata.
    bytes32 public constant METADATA_ROLE = keccak256("METADATA_ROLE");

    /// @dev Simple struct to keep auxiliary Spiral metadata on-chain.
    struct RoleMetadata {
        string spiral;      // e.g. "Regen Spiral"
        string role;        // e.g. "Initiator"
        string generation;  // e.g. "Genesis"
        string uri;         // optional off-chain metadata pointer (IPFS / HTTPS)
    }

    /// @dev Incremental token id tracker.
    Counters.Counter private _tokenIdTracker;

    /// @dev Optional base URI that can be combined with role pointers.
    string private _baseTokenURI;

    /// @dev Storage for auxiliary metadata per token id.
    mapping(uint256 => RoleMetadata) private _roleMetadata;

    event BaseURIUpdated(string indexed previousBaseURI, string indexed newBaseURI);
    event MetadataAttached(
        uint256 indexed tokenId,
        string spiral,
        string role,
        string generation,
        string uri
    );

    constructor(string memory baseURI, address admin)
        ERC721("Stitchia Genesis", "STCH-GEN")
    {
        _baseTokenURI = baseURI;
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(MINTER_ROLE, admin);
        _grantRole(METADATA_ROLE, admin);
    }

    /// @notice Mint a Genesis NFT with optional metadata URI.
    /// @param to recipient wallet.
    /// @param customTokenURI optional fully-qualified token URI. Leave empty to rely on the base URI.
    /// @param metadata Additional Spiral context for dashboards / off-chain services.
    function mintTo(
        address to,
        string calldata customTokenURI,
        RoleMetadata calldata metadata
    ) external onlyRole(MINTER_ROLE) returns (uint256 tokenId) {
        _tokenIdTracker.increment();
        tokenId = _tokenIdTracker.current();

        _safeMint(to, tokenId);

        if (bytes(customTokenURI).length != 0) {
            _setTokenURI(tokenId, customTokenURI);
        }

        _roleMetadata[tokenId] = metadata;
        emit MetadataAttached(tokenId, metadata.spiral, metadata.role, metadata.generation, metadata.uri);
    }

    /// @notice Update metadata after mint (e.g. validator seals, updated docs).
    function updateMetadata(uint256 tokenId, RoleMetadata calldata metadata)
        external
        onlyRole(METADATA_ROLE)
    {
        require(_exists(tokenId), "GENESIS: TOKEN_NOT_FOUND");
        _roleMetadata[tokenId] = metadata;
        emit MetadataAttached(tokenId, metadata.spiral, metadata.role, metadata.generation, metadata.uri);
    }

    /// @notice Adjust the contract wide base URI.
    function setBaseURI(string calldata newBaseURI) external onlyRole(METADATA_ROLE) {
        emit BaseURIUpdated(_baseTokenURI, newBaseURI);
        _baseTokenURI = newBaseURI;
    }

    /// @notice Retrieve auxiliary role metadata for a token id.
    function roleMetadata(uint256 tokenId) external view returns (RoleMetadata memory metadata) {
        require(_exists(tokenId), "GENESIS: TOKEN_NOT_FOUND");
        metadata = _roleMetadata[tokenId];
    }

    /// @notice Total number of tokens minted (including burned ones).
    function totalMinted() external view returns (uint256) {
        return _tokenIdTracker.current();
    }

    /// @dev override base URI from ERC721URIStorage.
    function _baseURI() internal view override returns (string memory) {
        return _baseTokenURI;
    }

    /// @dev required override due to multiple inheritance (AccessControl + ERC721).
    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, AccessControl)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}

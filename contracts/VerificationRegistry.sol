// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VerificationRegistry {
    struct Record {
        string contentHash;
        string sourceUrl;
        uint256 timestamp;
        address submitter;
    }

    mapping(string => Record) private records;

    event RecordStored(
        string indexed contentHash,
        string sourceUrl,
        uint256 timestamp,
        address submitter
    );

    function storeRecord(string memory _contentHash, string memory _sourceUrl) external {
        require(records[_contentHash].timestamp == 0, "Record already exists on-chain");

        records[_contentHash] = Record({
            contentHash: _contentHash,
            sourceUrl: _sourceUrl,
            timestamp: block.timestamp,
            submitter: msg.sender
        });

        emit RecordStored(_contentHash, _sourceUrl, block.timestamp, msg.sender);
    }

    function verifyRecord(string memory _contentHash) external view returns (
        bool exists,
        string memory sourceUrl,
        uint256 timestamp,
        address submitter
    ) {
        Record memory rec = records[_contentHash];
        if (rec.timestamp == 0) {
            return (false, "", 0, address(0));
        }
        return (true, rec.sourceUrl, rec.timestamp, rec.submitter);
    }
}
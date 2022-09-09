// SPDX-FileCopyrightText: 2022 Lido <info@lido.fi>
// SPDX-License-Identifier: GPL-3.0

pragma solidity ^0.8.4;

import "../TrustedCaller.sol";
import "../AllowedRecipientsRegistry.sol";
import "../libraries/EVMScriptCreator.sol";
import "../interfaces/IEVMScriptFactory.sol";

/// @author psirex, zuzueeka
/// @notice Creates EVMScript to add new allowed recipient address to AllowedRecipientsRegistry
contract AddAllowedRecipient is TrustedCaller, IEVMScriptFactory {
    // -------------
    // ERRORS
    // -------------
    string private constant ERROR_ALLOWED_RECIPIENT_ALREADY_ADDED =
        "ALLOWED_RECIPIENT_ALREADY_ADDED";

    // -------------
    // VARIABLES
    // -------------

    /// @notice Address of AllowedRecipientsRegistry
    AllowedRecipientsRegistry public immutable allowedRecipientsRegistry;

    // -------------
    // CONSTRUCTOR
    // -------------

    constructor(address _trustedCaller, address _allowedRecipientsRegistry)
        TrustedCaller(_trustedCaller)
    {
        allowedRecipientsRegistry = AllowedRecipientsRegistry(_allowedRecipientsRegistry);
    }

    // -------------
    // EXTERNAL METHODS
    // -------------

    /// @notice Creates EVMScript to add new allowed recipient address to allowedRecipientsRegistry
    /// @param _creator Address who creates EVMScript
    /// @param _evmScriptCallData Encoded tuple: (address _recipientAddress)
    function createEVMScript(address _creator, bytes memory _evmScriptCallData)
        external
        view
        override
        onlyTrustedCaller(_creator)
        returns (bytes memory)
    {
        (address _recipientAddress, ) = _decodeEVMScriptCallData(_evmScriptCallData);
        require(
            !allowedRecipientsRegistry.isAllowedRecipient(_recipientAddress),
            ERROR_ALLOWED_RECIPIENT_ALREADY_ADDED
        );

        return
            EVMScriptCreator.createEVMScript(
                address(allowedRecipientsRegistry),
                allowedRecipientsRegistry.addAllowedRecipient.selector,
                _evmScriptCallData
            );
    }

    /// @notice Decodes call data used by createEVMScript method
    /// @param _evmScriptCallData Encoded tuple: (address _recipientAddress, string _title)
    /// @return _rewardProgram Address of new recipient address
    function decodeEVMScriptCallData(bytes memory _evmScriptCallData)
        external
        pure
        returns (address, string memory)
    {
        return _decodeEVMScriptCallData(_evmScriptCallData);
    }

    // ------------------
    // PRIVATE METHODS
    // ------------------

    function _decodeEVMScriptCallData(bytes memory _evmScriptCallData)
        private
        pure
        returns (address, string memory)
    {
        return abi.decode(_evmScriptCallData, (address, string));
    }
}
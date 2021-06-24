// SPDX-FileCopyrightText: 2021 Lido <info@lido.fi>
// SPDX-License-Identifier: GPL-3.0

pragma solidity 0.8.4;

library EVMScriptCreator {
    bytes4 private constant SPEC_ID = hex"00000001";

    function createEVMScript(
        address _to,
        bytes4 _methodId,
        bytes memory _methodCallData
    ) external pure returns (bytes memory _commands) {
        return
            abi.encodePacked(
                SPEC_ID,
                _to,
                uint32(_methodCallData.length) + 4,
                _methodId,
                _methodCallData
            );
    }

    function createEVMScript(
        address _to,
        bytes4 _methodId,
        bytes[] memory _evmScriptCallData
    ) external pure returns (bytes memory _evmScript) {
        for (uint256 i = 0; i < _evmScriptCallData.length; ++i) {
            _evmScript = bytes.concat(
                _evmScript,
                abi.encodePacked(
                    _to,
                    uint32(_evmScriptCallData[i].length) + 4,
                    _methodId,
                    _evmScriptCallData[i]
                )
            );
        }
        _evmScript = bytes.concat(SPEC_ID, _evmScript);
    }
}
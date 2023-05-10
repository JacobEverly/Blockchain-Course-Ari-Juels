pragma solidity^0.5.0;

contract HelloWorldContract {
    bytes32 public ownerflag;
    bytes32 public userflag;

    event HelloWorld(string, bytes32);

    constructor(bytes32 _ownerflag) public {
        ownerflag = _ownerflag;
    }

    function helloworld(string memory _yourstring, bytes32 _yourflag) public {
        emit HelloWorld(_yourstring, _yourflag);
        userflag = _yourflag;
    }
}

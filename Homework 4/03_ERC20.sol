pragma solidity^0.5.0;

contract TestToken {
    string constant name = "IC3 2017 Bootcamp Token";
    string constant symbol = "IC3";
    uint8 constant decimals = 18;
    uint public total;

    struct Allowed {
        mapping (address => uint256) _allowed;
    }

    mapping (address => Allowed) allowed;
    mapping (address => uint256) balances;

    event Transfer(address indexed _from, address indexed _to, uint256 _value);
    event Approval(address indexed _owner, address indexed _spender, uint256 _value);

    constructor() public payable {
        require(msg.value > 4999999999999999);
        balances[0x0000000000000000000000000000000000000000] = msg.value;
        total += msg.value;
    }

    function balanceOf(address _owner) public view returns (uint256 balance) {
        return balances[_owner];
    }

    function deposit() public payable returns (bool success) {
        if (balances[msg.sender] + msg.value < msg.value) return false;
        if (total + msg.value < msg.value) return false;
        balances[msg.sender] += msg.value;
        total += msg.value;
        return true;
    }

    function withdraw(uint256 _value) public payable returns (bool success) {
        if (balances[msg.sender] < _value) return false;
        msg.sender.call.value(_value)("");
        balances[msg.sender] -= _value;
        total -= _value;
        return true;
    }

    function transfer(address _to, uint256 _value) public returns (bool success) {
        if (balances[msg.sender] < _value) return false;

        if (balances[_to] + _value < _value) return false;
        balances[msg.sender] -= _value;
        balances[_to] += _value;

        emit Transfer(msg.sender, _to, _value);

        return true;
    }


    function approve(address _spender, uint256 _value) public returns (bool success) {
        allowed[msg.sender]._allowed[_spender] = _value;
        emit Approval(msg.sender, _spender, _value);
        return true;
    }

    function allowance(address _owner, address _spender) public view returns (uint256 remaining) {
        return allowed[_owner]._allowed[_spender];
    }

    function transferFrom(address _from, address _to, uint256 _value) public returns (bool success) {
        if (balances[_from] < _value) return false;
        if ( allowed[_from]._allowed[msg.sender] < _value) return false;
        if (balances[_to] + _value < _value) return false;

        balances[_from] -= _value;
        balances[_to] += _value;
        allowed[_from]._allowed[msg.sender] -= _value;
        return true;
    }

}

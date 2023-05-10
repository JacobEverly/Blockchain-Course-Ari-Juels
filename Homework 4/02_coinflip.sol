pragma solidity^0.5.1;

contract CoinFlip {
    address public player1;
    address public player2;
    mapping(address => bool) public deposited;
    mapping(address => uint256) public deposits;
    mapping(address => bool) public extended;
    uint256 public gamestart;
    uint256 public gameend;
    uint256 public mintoextend;
    uint256 public captoadd;
    uint256 public balance;
    bool public gameover;
    address public winner;

    constructor(address _p2) public payable {
        mintoextend = 0.005 ether;
        captoadd = 0.01 ether;
        gameover = false;
        player1 = 0x0000000000000000000000000000000000000000;
        player2 = _p2;
        balance += msg.value;
        deposits[0x0000000000000000000000000000000000000000] = msg.value;
        deposited[0x0000000000000000000000000000000000000000] = true;
    }

    function starthash() public view returns (bytes32 h) {
        return blockhash(gamestart);
    }

    function endhash() public view returns (bytes32 h) {
        return blockhash(gameend);
    }

    /* players are allowed to name a champion to play
     * in the coliseum in their stead */
    function delegate(address delegateaddress) public {
        require(msg.sender == player1 || msg.sender == player2);
        if(msg.sender == player1) {
            player1 = delegateaddress;
        }
        else {
            player2 = delegateaddress;
        }
    }

    function deposit() public payable {
        require(!gameover);
        require(msg.sender == player1 || msg.sender == player2);
        require(!deposited[player1] || !deposited[player2]);
        deposits[msg.sender] = msg.value;
        deposited[msg.sender] = true;
        balance += msg.value;
        if (deposited[player1] && deposited[player2]) {
            gamestart = block.number;
            gameend = block.number + 5;
        }
    }

    /* Players can only extend the game with a monetary deposit
        to prevent arbitrary game extending (DoS). */
    function extend() public payable {
        require(!gameover);
        require(msg.sender == player1 || msg.sender == player2);
        require(!extended[player1] || !extended[player2] );
        if (msg.value > mintoextend) {
            /* Extend by 5 blocks */
            gameend = block.number + 2;
            if (msg.value > captoadd) {
                /* Refund money above the deposit cap */
                balance += (captoadd - mintoextend);
                msg.sender.call.value(msg.value - captoadd)("");
            } else {
                balance += msg.value;
            }
        }
        extended[msg.sender] = true;
    }

    /* Calculate the winner of the coin flip and
        reward them with the balance of the contract */
    function resolve() public {
        require(!gameover);
        require(block.number > gameend);
        gameover = true;
        uint256 win = ((uint256)(blockhash(gamestart) ^ blockhash(gameend))) % 10;
        if (win == 1) {
            winner = player2;
            player2.call.value(balance)("");
        } else {
            winner = player1;
            player1.call.value(balance)("");
        }
    }

}

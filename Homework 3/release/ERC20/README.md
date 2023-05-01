----------------------------------------------------------------
** NOTE: Tests may be difficult to run on Windows system. You can instead test by deploying your contract to a testnet and interacting with it. See the pdf for details. **
----------------------------------------------------------------

# Installing and Running Locally

You MUST have Python>=3.8 installed and solc>=0.8.x.

Several options to install solidity are given here: http://solidity.readthedocs.io/en/develop/installing-solidity.html. At the end, ```solc --version``` should give you a good output.

After correctly impementing the withdraw function, all tests in the file `run_tests.py` should pass.

## Linux users

Note: Tested with python3.9 on a Linux machine.

1. `sudo apt install python3.9-dev`
2. Create and activate a virtual environment with python3.9
3. `pip install eth_tester web3[tester]`

You should now be able to run tests with `python run_tests.py`.

## Mac users

Install ethereum with pip:
```
  pip3 install eth_tester web3
  pip3 install py-evm
  brew tap ethereum/ethereum
  brew install ethereum
```
## Windows Users:

Microsoft Visual C++ 14.0 or greater is required
Follow https://geth.ethereum.org/docs/install-and-build/installing-geth
```
  python -m pip install eth_tester web3
```

Then, run tests with run_tests.py


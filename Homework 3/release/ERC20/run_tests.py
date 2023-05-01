import unittest, os
#from eth_tester import EthereumTester, PyEVMBackend
import web3
from web3 import Web3, EthereumTesterProvider
import json

class TestERC20Challenge(unittest.TestCase):

    def setUp(self):
        self.tester_provider = EthereumTesterProvider()
        self.eth_tester = self.tester_provider.ethereum_tester
        self.w3 = Web3(self.tester_provider)
        self.test_accounts_tuple = self.eth_tester.get_accounts()
        self.deploy_address = str(self.test_accounts_tuple[0])
        self.w3.geth.personal.unlock_account(self.deploy_address, "")

        os.system('solc --combined-json abi,bin ERC20.sol > compile.json')
        
        with open('compile.json') as json_file:
            data = json_file.read()
            abi = data['contracts']['ERC20.sol:MyToken']['abi']
            bytecode = data['contracts']['ERC20.sol:MyToken']['bin']
        
        self.contract = self.w3.eth.contract(abi=abi, bytecode=bytecode)
        tx_hash = self.contract.constructor().transact({'from': self.deploy_address, 'gas': 2000000})
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, 180)
        self.contract_address = tx_receipt.contractAddress
        self.contract = self.w3.eth.contract(abi=abi, address=tx_receipt.contractAddress)
        self.account1 = str(self.test_accounts_tuple[1])
        self.account2 = str(self.test_accounts_tuple[2])
        self.account3 = str(self.test_accounts_tuple[2])

    def tearDown(self):
        os.system('rm -f compile.json')

    def test_initial_state(self):
        # Check total supply is 0
        self.assertEqual(self.eth_tester.get_balance(self.account1), 1000000000000000000000000)
        self.assertEqual(self.contract.caller().totalSupply(), 0)
        # Check several account balances as 0
        self.assertEqual(self.contract.functions.balanceOf(self.account1).call(), 0)
        self.assertEqual(self.contract.functions.balanceOf(self.account2).call(), 0)
        self.assertEqual(self.contract.functions.balanceOf(self.account3).call(), 0)
        # Check several allowances as 0
        self.assertEqual(self.contract.functions.allowance(self.account1, self.account1).call(), 0)
        self.assertEqual(self.contract.functions.allowance(self.account1, self.account2).call(), 0)
        self.assertEqual(self.contract.functions.allowance(self.account1, self.account3).call(), 0)
        self.assertEqual(self.contract.functions.allowance(self.account2, self.account3).call(), 0)


    def test_deposit(self):
        initial_a1_balance = self.eth_tester.get_balance(self.account1) # self.s.head_state.get_balance(self.t.a1)
        initial_a2_balance = self.eth_tester.get_balance(self.account1) # self.s.head_state.get_balance(self.t.a2)
        # Test scenario where a1 deposits 2 tokens/2k wei  , withdraws twice (check balance consistency)
        self.assertEqual(self.eth_tester.get_balance(self.contract_address), 0) # self.assertEqual(self.c.balanceOf(self.t.a1), 0)
        deposit_tx_hash = self.contract.functions.deposit().transact({"from":self.account1, "value":2000, "gas":200000}) # self.assertIsNone(self.c.deposit(value=2000, sender=self.t.k1))
        deposit_tx_receipt = self.w3.eth.wait_for_transaction_receipt(deposit_tx_hash)
        self.assertEqual(self.contract.functions.balanceOf(self.account1).call(), 2) # self.assertEqual(self.c.balanceOf(self.t.a1), 2)
        # Check that 2000 Wei have been debited from a1
        # print(deposit_tx_receipt)
        # print(initial_a1_balance, self.eth_tester.get_balance(self.account1), deposit_tx_receipt['gasUsed'])
        self.assertEqual(self.eth_tester.get_balance(self.contract_address), 2000) # self.assertEqual(self.s.head_state.get_balance(self.c.address), 2000)
        self.assertEqual(self.contract.functions.balanceOf(self.account1).call(), 2)
        # self.assertEqual(initial_a1_balance - self.eth_tester.get_balance(self.account1) - deposit_tx_receipt['gasUsed'], 2000) # self.assertEqual(initial_a1_balance - self.s.head_state.get_balance(self.t.a1), 2000)
        # ... and added to the contract
        withdraw_tx_hash = self.contract.functions.withdraw(2).transact({"from": self.account1, "gas":200000}) # self.assertTrue(self.c.withdraw(2, sender=self.t.k1))
        withdraw_tx_receipt = self.w3.eth.wait_for_transaction_receipt(withdraw_tx_hash)
        self.assertEqual(self.contract.functions.balanceOf(self.account1).call(), 0) # self.assertEqual(self.c.balanceOf(self.t.a1), 0)
        # a1 should have all his money back
        # self.assertEqual(self.eth_tester.get_balance(self.account1), initial_a1_balance - deposit_tx_receipt['gasUsed'] - withdraw_tx_receipt['gasUsed']) # self.assertEqual(self.s.head_state.get_balance(self.t.a1), initial_a1_balance)
        withdraw_tx_hash = self.contract.functions.withdraw(2200).transact({"from": self.account1, "gas":200000})
        withdraw_tx_receipt = self.w3.eth.wait_for_transaction_receipt(withdraw_tx_hash)
        #check withdraw fails
        self.assertFalse(withdraw_tx_receipt['status']) # self.assert_tx_failed(lambda: self.c.withdraw(2, sender=self.t.k1))
        self.assertEqual(self.contract.functions.balanceOf(self.account1).call(), 0) # self.assertEqual(self.c.balanceOf(self.t.a1), 0)
        # Test scenario where a2 deposits 0, withdraws (check balance consistency, false withdraw)
        deposit_tx_hash = self.contract.functions.deposit().transact({"from":self.account2, "value":0, "gas":200000}) # self.assertIsNone(self.c.deposit(value=0, sender=self.t.k2))
        deposit_tx_receipt = self.w3.eth.wait_for_transaction_receipt(deposit_tx_hash)
        self.assertEqual(self.contract.functions.balanceOf(self.account2).call(), 0) # self.assertEqual(self.c.balanceOf(self.t.a2), 0)
        # self.assertEqual(self.eth_tester.get_balance(self.account2), initial_a2_balance - deposit_tx_receipt['gasUsed']) # self.assertEqual(self.s.head_state.get_balance(self.t.a2), initial_a2_balance)
        withdraw_tx_hash = self.contract.functions.withdraw(2).transact({"from": self.account2, "gas":200000})
        withdraw_tx_receipt = self.w3.eth.wait_for_transaction_receipt(withdraw_tx_hash)
        self.assertFalse(withdraw_tx_receipt['status']) # self.assert_tx_failed(lambda: self.c.withdraw(2, sender=self.t.k2))

    def test_totalSupply(self):
        # Test total supply initially, after deposit, between two withdraws, and after failed withdraw
        self.assertEqual(self.contract.functions.totalSupply().call(), 0)
        deposit_tx_hash = self.contract.functions.deposit().transact({"from":self.account1, "value":2000, "gas":200000}) # self.assertIsNone(self.c.deposit(value=2000, sender=self.t.k1))
        deposit_tx_receipt = self.w3.eth.wait_for_transaction_receipt(deposit_tx_hash)
        self.assertEqual(self.contract.functions.totalSupply().call(), 2)
        withdraw_tx_hash = self.contract.functions.withdraw(1).transact({"from": self.account1, "gas":200000}) # self.assertTrue(self.c.withdraw(1, sender=self.t.k1))
        withdraw_tx_receipt = self.w3.eth.wait_for_transaction_receipt(withdraw_tx_hash)
        self.assertEqual(self.contract.functions.totalSupply().call(), 1)
        # Ensure total supply is equal to balance
        self.assertEqual(self.contract.functions.totalSupply().call() * 1000, self.eth_tester.get_balance(self.contract_address))
        withdraw_tx_hash = self.contract.functions.withdraw(1).transact({"from": self.account1, "gas":200000}) # self.assertTrue(self.c.withdraw(1, sender=self.t.k1))
        withdraw_tx_receipt = self.w3.eth.wait_for_transaction_receipt(withdraw_tx_hash)
        self.assertEqual(self.contract.functions.totalSupply().call(), 0)
        withdraw_tx_hash = self.contract.functions.withdraw(1).transact({"from": self.account1, "gas":200000}) # self.assertTrue(self.c.withdraw(1, sender=self.t.k1))
        withdraw_tx_receipt = self.w3.eth.wait_for_transaction_receipt(withdraw_tx_hash)
        self.assertFalse(withdraw_tx_receipt['status']) # self.assert_tx_failed(lambda: self.c.withdraw(1, sender=self.t.k1))
        self.assertEqual(self.contract.functions.totalSupply().call(), 0)
        # Test that 0-valued deposit can't affect supply
        deposit_tx_hash = self.contract.functions.deposit().transact({"from":self.account1, "value":0, "gas":200000}) # self.assertIsNone(self.c.deposit(value=0, sender=self.t.k1))
        deposit_tx_receipt = self.w3.eth.wait_for_transaction_receipt(deposit_tx_hash)
        self.assertEqual(self.contract.functions.totalSupply().call(), 0)

    def test_transfer(self):
        # Test interaction between deposit/withdraw and transfer
        withdraw_tx_hash = self.contract.functions.withdraw(1).transact({"from": self.account2, "gas":200000}) # self.assertTrue(self.c.withdraw(1, sender=self.t.k1))
        withdraw_tx_receipt = self.w3.eth.wait_for_transaction_receipt(withdraw_tx_hash)
        self.assertFalse(withdraw_tx_receipt['status']) # self.assert_tx_failed(lambda: self.c.withdraw(1, sender=self.t.k2))
        deposit_tx_hash = self.contract.functions.deposit().transact({"from":self.account1, "value":2000, "gas":200000}) # self.assertIsNone(self.c.deposit(value=2000, sender=self.t.k1))
        deposit_tx_receipt = self.w3.eth.wait_for_transaction_receipt(deposit_tx_hash)
        withdraw_tx_hash = self.contract.functions.withdraw(1).transact({"from": self.account1, "gas":200000}) # self.assertTrue(self.c.withdraw(1, sender=self.t.k1))
        withdraw_tx_receipt = self.w3.eth.wait_for_transaction_receipt(withdraw_tx_hash)
        transfer_tx_hash = self.contract.functions.transfer(self.account2, 1).transact({"from": self.account1, "gas":200000}) # self.assertTrue(self.c.transfer(self.t.a2, 1, sender=self.t.k1))
        transfer_tx_receipt = self.w3.eth.wait_for_transaction_receipt(transfer_tx_hash)
        withdraw_tx_hash = self.contract.functions.withdraw(1).transact({"from": self.account1, "gas":200000}) # self.assertTrue(self.c.withdraw(1, sender=self.t.k1))
        withdraw_tx_receipt = self.w3.eth.wait_for_transaction_receipt(withdraw_tx_hash)
        self.assertFalse(withdraw_tx_receipt['status']) # self.assert_tx_failed(lambda: self.c.withdraw(1, sender=self.t.k1))
        withdraw_tx_hash = self.contract.functions.withdraw(1).transact({"from": self.account2, "gas":200000}) # self.assertTrue(self.c.withdraw(1, sender=self.t.k1))
        withdraw_tx_receipt = self.w3.eth.wait_for_transaction_receipt(withdraw_tx_hash)
        self.assertTrue(withdraw_tx_receipt['status']) # self.assertTrue(self.c.withdraw(1, sender=self.t.k2))
        withdraw_tx_hash = self.contract.functions.withdraw(1).transact({"from": self.account2, "gas":200000}) # self.assertTrue(self.c.withdraw(1, sender=self.t.k1))
        withdraw_tx_receipt = self.w3.eth.wait_for_transaction_receipt(withdraw_tx_hash)
        self.assertFalse(withdraw_tx_receipt['status']) # self.assert_tx_failed(lambda: self.c.withdraw(1, sender=self.t.k2))
        # Ensure transfer fails with insufficient balance
        transfer_tx_hash = self.contract.functions.transfer(self.account1, 1).transact({"from": self.account2, "gas":200000}) # self.assertTrue(self.c.transfer(self.t.a2, 1, sender=self.t.k1))
        transfer_tx_receipt = self.w3.eth.wait_for_transaction_receipt(transfer_tx_hash)
        self.assertFalse(transfer_tx_receipt['status']) # self.assert_tx_failed(lambda: self.c.transfer(self.t.a1, 1, sender=self.t.k2))
        # Ensure 0-transfer always succeeds
        transfer_tx_hash = self.contract.functions.transfer(self.account1, 0).transact({"from": self.account2, "gas":200000}) # self.assertTrue(self.c.transfer(self.t.a2, 1, sender=self.t.k1))
        transfer_tx_receipt = self.w3.eth.wait_for_transaction_receipt(transfer_tx_hash)
        self.assertTrue(transfer_tx_receipt['status']) # self.assertTrue(self.c.transfer(self.t.a1, 0, sender=self.t.k2))


    def test_transferFromAndAllowance(self):
        # Test interaction between deposit/withdraw and transferFrom
        withdraw_tx_hash = self.contract.functions.withdraw(1).transact({"from": self.account2, "gas":200000}) # self.assertTrue(self.c.withdraw(1, sender=self.t.k1))
        withdraw_tx_receipt = self.w3.eth.wait_for_transaction_receipt(withdraw_tx_hash)
        self.assertFalse(withdraw_tx_receipt['status']) # self.assert_tx_failed(lambda: self.c.withdraw(1, sender=self.t.k2))
        deposit_tx_hash = self.contract.functions.deposit().transact({"from":self.account1, "value":1000, "gas":200000}) # self.assertIsNone(self.c.deposit(value=1000, sender=self.t.k1))
        deposit_tx_receipt = self.w3.eth.wait_for_transaction_receipt(deposit_tx_hash)
        deposit_tx_hash = self.contract.functions.deposit().transact({"from":self.account2, "value":1000, "gas":200000}) # self.assertIsNone(self.c.deposit(value=1000, sender=self.t.k2))
        deposit_tx_receipt = self.w3.eth.wait_for_transaction_receipt(deposit_tx_hash)
        withdraw_tx_hash = self.contract.functions.withdraw(1).transact({"from": self.account1, "gas":200000}) # self.assertTrue(self.c.withdraw(1, sender=self.t.k1))
        withdraw_tx_receipt = self.w3.eth.wait_for_transaction_receipt(withdraw_tx_hash)
        self.assertTrue(withdraw_tx_receipt['status']) # self.assertTrue(self.c.withdraw(1, sender=self.t.k1))
        # This should fail; no allowance or balance (0 always succeeds)
        transferFrom_tx_hash = self.contract.functions.transferFrom(self.account1, self.account3, 1).transact({"from": self.account2, "gas":200000}) 
        transferFrom_tx_receipt = self.w3.eth.wait_for_transaction_receipt(transferFrom_tx_hash)
        self.assertFalse(transferFrom_tx_receipt['status']) # self.assert_tx_failed(lambda: self.c.transferFrom(self.t.a1, self.t.a3, 1, sender=self.t.k2))
        transferFrom_tx_hash = self.contract.functions.transferFrom(self.account1, self.account3, 0).transact({"from": self.account2, "gas":200000}) 
        transferFrom_tx_receipt = self.w3.eth.wait_for_transaction_receipt(transferFrom_tx_hash)
        self.assertTrue(transferFrom_tx_receipt['status']) # self.assertTrue(self.c.transferFrom(self.t.a1, self.t.a3, 0, sender=self.t.k2))
        # Correct call to approval should update allowance (but not for reverse pair)
        approve_tx_hash = self.contract.functions.approve(self.account2, 1).transact({"from": self.account1, "gas":200000})
        approve_tx_receipt = self.w3.eth.wait_for_transaction_receipt(approve_tx_hash)# self.assertTrue(self.c.approve(self.t.a2, 1, sender=self.t.k1))
        self.assertEqual(self.contract.functions.allowance(self.account1, self.account2).call(), 1)
        self.assertEqual(self.contract.functions.allowance(self.account2, self.account1).call(), 0)
        # transferFrom should succeed when allowed, fail with wrong sender
        transferFrom_tx_hash = self.contract.functions.transferFrom(self.account2, self.account3, 1).transact({"from": self.account3, "gas":200000})
        transferFrom_tx_receipt = self.w3.eth.wait_for_transaction_receipt(transferFrom_tx_hash)
        self.assertFalse(transferFrom_tx_receipt['status']) # self.assert_tx_failed(lambda: self.c.transferFrom(self.t.a2, self.t.a3, 1, sender=self.t.k3))
        self.assertEqual(self.contract.functions.balanceOf(self.account2).call(), 1) # self.assertEqual(self.c.balanceOf(self.t.a2), 1)
        approve_tx_receipt = self.w3.eth.wait_for_transaction_receipt(self.contract.functions.approve(self.account1, 1).transact({"from": self.account2, "gas":200000}))# self.assertTrue(self.c.approve(self.t.a1, 1, sender=self.t.k2))
        transferFrom_tx_receipt = self.w3.eth.wait_for_transaction_receipt(self.contract.functions.transferFrom(self.account2, self.account3, 1).transact({"from": self.account1, "gas":200000}))
        self.assertTrue(transferFrom_tx_receipt['status']) # self.assertTrue(self.c.transferFrom(self.t.a2, self.t.a3, 1, sender=self.t.k1))
        # Allowance should be correctly updated after transferFrom
        self.assertEqual(self.contract.functions.allowance(self.account2, self.account1).call(), 0)
        # transferFrom with no funds should fail despite approval
        withdraw_tx_receipt = self.w3.eth.wait_for_transaction_receipt(self.contract.functions.withdraw(1).transact({"from": self.account2, "gas":200000}))
        approve_tx_hash = self.contract.functions.approve(self.account1, 1).transact({"from": self.account2, "gas":200000})
        approve_tx_receipt = self.w3.eth.wait_for_transaction_receipt(approve_tx_hash)# self.assertTrue(self.c.approve(self.t.a1, 1, sender=self.t.k2))
        self.assertEqual(self.contract.functions.allowance(self.account2, self.account1).call(), 1)
        transferFrom_tx_receipt = self.w3.eth.wait_for_transaction_receipt(self.contract.functions.transferFrom(self.account2, self.account3, 1).transact({"from": self.account1, "gas":200000}))
        self.assertFalse(transferFrom_tx_receipt['status']) # self.assert_tx_failed(lambda: self.c.transferFrom(self.t.a2, self.t.a3, 1, sender=self.t.k1))
        # 0-approve should not change balance or allow transferFrom to change balance
        self.w3.eth.wait_for_transaction_receipt(self.contract.functions.deposit().transact({"from":self.account1, "value":1000, "gas":200000}))# self.assertIsNone(self.c.deposit(value=1000, sender=self.t.k2))
        self.assertEqual(self.contract.functions.allowance(self.account2, self.account1).call(), 1)
        self.w3.eth.wait_for_transaction_receipt(self.contract.functions.approve(self.account1, 0).transact({"from": self.account2, "gas":200000}))# self.assertTrue(self.c.approve(self.t.a1, 0, sender=self.t.k2))
        self.assertEqual(self.contract.functions.allowance(self.account2, self.account1).call(), 0)# self.assertEqual(self.c.allowance(self.t.a2, self.t.a1, sender=self.t.k2), 0)
        transferFrom_tx_receipt = self.w3.eth.wait_for_transaction_receipt(self.contract.functions.transferFrom(self.account2, self.account3, 1).transact({"from": self.account1, "gas":200000}))
        self.assertFalse(transferFrom_tx_receipt['status']) # self.assert_tx_failed(lambda: self.c.transferFrom(self.t.a2, self.t.a3, 1, sender=self.t.k1))
        # Test that if non-zero approval exists, 0-approval is NOT required to proceed
        # a non-conformant implementation is described in countermeasures at
        # https://docs.google.com/document/d/1YLPtQxZu1UAvO9cZ1O2RPXBbT0mooh4DYKjA_jp-RLM/edit#heading=h.m9fhqynw2xvt
        # the final spec insists on NOT using this behavior
        self.assertEqual(self.contract.functions.allowance(self.account2, self.account1).call(), 0)
        self.w3.eth.wait_for_transaction_receipt(self.contract.functions.approve(self.account1, 1).transact({"from": self.account2, "gas":200000})) # self.assertTrue(self.c.approve(self.t.a1, 1, sender=self.t.k2))
        self.assertEqual(self.contract.functions.allowance(self.account2, self.account1).call(), 1)
        self.w3.eth.wait_for_transaction_receipt(self.contract.functions.approve(self.account1, 2).transact({"from": self.account2, "gas":200000})) # self.assertTrue(self.c.approve(self.t.a1, 2, sender=self.t.k2))
        self.assertEqual(self.contract.functions.allowance(self.account2, self.account1).call(), 2)# self.assertEqual(self.c.allowance(self.t.a2, self.t.a1, sender=self.t.k2), 2)
        # Check that approving 0 then amount also works
        self.w3.eth.wait_for_transaction_receipt(self.contract.functions.approve(self.account1, 0).transact({"from": self.account2, "gas":200000})) # self.assertTrue(self.c.approve(self.t.a1, 0, sender=self.t.k2))
        self.assertEqual(self.contract.functions.allowance(self.account2, self.account1).call(), 0)
        self.w3.eth.wait_for_transaction_receipt(self.contract.functions.approve(self.account1, 5).transact({"from": self.account2, "gas":200000})) # self.assertTrue(self.c.approve(self.t.a1, 5, sender=self.t.k2))
        self.assertEqual(self.contract.functions.allowance(self.account2, self.account1).call(), 5)


    # Leaving this as TODO  - would have to figure out how to turn off rules in pyevm and grant an account infinite money
    # def test_maxInts(self):
    #     MAX_UINT256 = 115792089237316195423570985008687907853269984665640564039457584007913129639935
    #     initial_a1_balance = self.eth_tester.get_balance(self.account1) # self.s.head_state.get_balance(self.t.a1)
    #     deposit_tx_receipt = self.w3.eth.wait_for_transaction_receipt(self.contract.functions.deposit().transact({"from":self.account1, "value":MAX_UINT256, "gas":200000})) # self.c.deposit(value=int(MAX_UINT256), sender=self.t.k1)))
    #     self.assertEqual(initial_a1_balance - self.eth_tester.get_balance(self.account1), MAX_UINT256 - 935)
    #     self.assertEqual(self.c.balanceOf(self.t.a1), 115792089237316195423570985008687907853269984665640564039457584007913129639)
    #     # Check that corresponding deposit is allowed after withdraw
    #     self.assertTrue(self.c.withdraw(1, sender=self.t.k1))
    #     self.assertIsNone(self.c.deposit(value=1, sender=self.t.k2))

    # def test_payability(self):
    #     # Make sure functions are appopriately payable (or not)
    #     # Payable functions - ensure success
    #     deposit_tx_receipt = self.w3.eth.wait_for_transaction_receipt(self.contract.functions.deposit().transact({"from":self.account1, "value":2000, "gas":200000}))# self.assertIsNone(self.c.deposit(value=1000, sender=self.t.k2))
    #     self.assertTrue(deposit_tx_receipt['status']) # self.assertIsNone(self.c.deposit(value=2000, sender=self.t.k1))
    #     # Non payable functions - ensure all fail with value, succeed without
    #     # self.w3.eth.wait_for_transaction_receipt(self.contract.functions.withdraw(0).transact({"from": self.account1, "value":2, "gas":200000}))
    #     #self.assertRaises(web3.exceptions.ValidationError, self.contract.functions.withdraw(0).transact({"from": self.account1, "value":2, "gas":200000}))  
    #     self.assertFalse(self.w3.eth.wait_for_transaction_receipt(self.contract.functions.withdraw(0).transact({"from": self.account1, "value":2, "gas":200000}))['status'])

    #     withdraw_tx_receipt = self.w3.eth.wait_for_transaction_receipt(self.contract.functions.withdraw(0).transact({"from": self.account1, "value":0, "gas":200000}))
    #     self.assertTrue(withdraw_tx_receipt['status']) # self.assertTrue(self.c.withdraw(0, value=0, sender=self.t.k1))
        
    #     #self.assertRaises(web3.exceptions.ValidationError, self.contract.functions.totalSupply().transact,{"from": self.account1, "value":2, "gas":200000})
    #     self.assertFalse(self.w3.eth.wait_for_transaction_receipt(self.contract.functions.totalSupply().transact({"from": self.account1, "value":2, "gas":200000}))['status'])
        
    #     tx_receipt = self.w3.eth.wait_for_transaction_receipt(self.contract.functions.totalSupply().transact({"from": self.account1, "value":0, "gas":200000}))
    #     self.assertTrue(tx_receipt['status']) # self.assertEqual(self.c.totalSupply(value=0, sender=self.t.k1), 2)
        
    #     self.assertFalse(self.w3.eth.wait_for_transaction_receipt(self.contract.functions.balanceOf(self.account1).transact({"from": self.account1, "value":2, "gas":200000}))['status'])# self.assert_tx_failed(lambda: self.c.balanceOf(self.t.a1, value=2, sender=self.t.k1))
        
    #     tx_receipt = self.w3.eth.wait_for_transaction_receipt(self.contract.functions.balanceOf(self.account1).transact({"from": self.account1, "value":0, "gas":200000}))
    #     self.assertTrue(tx_receipt['status'])# self.assertEqual(self.c.balanceOf(self.t.a1, value=0, sender=self.t.k1), 2)
        
    #     self.assertFalse(self.w3.eth.wait_for_transaction_receipt(self.contract.functions.transfer(self.account2, 0).transact({"from": self.account1, "value":2, "gas":200000}))['status'])# self.assert_tx_failed(lambda: self.c.transfer(self.t.a2, 0, value=2, sender=self.t.k1))
        
    #     tx_receipt = self.w3.eth.wait_for_transaction_receipt(self.contract.functions.transfer(self.account2, 0).transact({"from": self.account1, "value":0, "gas":200000}))
    #     self.assertTrue(tx_receipt['status'])# self.assertTrue(self.c.transfer(self.t.a2, 0, value=0, sender=self.t.k1))
        
    #     self.assertFalse(self.w3.eth.wait_for_transaction_receipt(self.contract.functions.approve(self.account2, 1).transact({"from": self.account1, "value":2, "gas":200000}))['status']) # self.assert_tx_failed(lambda: self.c.approve(self.t.a2, 1, value=2, sender=self.t.k1))
        
    #     tx_receipt = self.w3.eth.wait_for_transaction_receipt(self.contract.functions.approve(self.account2, 1).transact({"from": self.account1, "value":0, "gas":200000}))
    #     self.assertTrue(tx_receipt['status'])# self.assertTrue(self.c.approve(self.t.a2, 1, value=0, sender=self.t.k1))
        
    #     self.assertFalse(self.w3.eth.wait_for_transaction_receipt(self.contract.functions.allowance(self.account1, self.account2).transact({"from": self.account1, "value":2, "gas":200000}))['status']) # self.assert_tx_failed(lambda: self.c.allowance(self.t.a1, self.t.a2, value=2, sender=self.t.k1))
        
    #     tx_receipt = self.w3.eth.wait_for_transaction_receipt(self.contract.functions.allowance(self.account1, self.account2).transact({"from": self.account1, "value":0, "gas":200000}))
    #     self.assertTrue(tx_receipt['status'])# self.assertTrue(self.c.transfer(self.t.a2, 0, value=0, sender=self.t.k1))
        
    #     self.assertFalse(self.w3.eth.wait_for_transaction_receipt(self.contract.functions.transferFrom(self.account1, self.account2, 0).transact({"from": self.account1, "value":2, "gas":200000}))['status'])# self.assert_tx_failed(lambda: self.c.transferFrom(self.t.a1, self.t.a2, 0, value=2, sender=self.t.k1))
        
    #     tx_receipt = self.w3.eth.wait_for_transaction_receipt(self.contract.functions.transferFrom(self.account1, self.account2, 0).transact({"from": self.account1, "value":0, "gas":200000}))
    #     self.assertTrue(tx_receipt['status'])# self.assertTrue(self.c.transferFrom(self.t.a1, self.t.a2, 0, value=0, sender=self.t.k1))

    # def test_raw_logs(self):
    #     # Check that deposit appropriately emits Deposit event
    #     transfer_event_filter = self.contract.events.Transfer.createFilter(fromBlock='latest')
    #     approval_event_filter = self.contract.events.Approval.createFilter(fromBlock='latest')
    #     deposit_tx_receipt = self.w3.eth.wait_for_transaction_receipt(self.contract.functions.deposit().transact({"from":self.account1, "value":3000, "gas":200000}))# self.assertIsNone(self.c.deposit(value=1000, sender=self.t.k2))
    #     self.assertTrue(deposit_tx_receipt['status']) # self.assertIsNone(self.c.deposit(value=2000, sender=self.t.k1))
    #     transfer_event_list = transfer_event_filter.get_new_entries()
    #     self.assertEqual(len(transfer_event_list), 1)
    #     self.assertEqual(transfer_event_list[0]['event'], "Transfer")
    #     self.assertEqual(transfer_event_list[0]['args']['_from'], "0x0000000000000000000000000000000000000000")
    #     self.assertEqual(transfer_event_list[0]['args']['_to'], self.account1)
    #     self.assertEqual(transfer_event_list[0]['args']['_value'], 3)

    #     # Check that withdraw appropriately emits Withdraw event
    #     withdraw_tx_receipt = self.w3.eth.wait_for_transaction_receipt(self.contract.functions.withdraw(2).transact({"from":self.account1, "gas":200000}))
    #     self.assertTrue(withdraw_tx_receipt['status'])
    #     transfer_event_list = transfer_event_filter.get_new_entries()
    #     self.assertEqual(len(transfer_event_list), 1)
    #     self.assertEqual(transfer_event_list[0]['event'], "Transfer")
    #     self.assertEqual(transfer_event_list[0]['args']['_from'], self.account1)
    #     self.assertEqual(transfer_event_list[0]['args']['_to'],  "0x0000000000000000000000000000000000000000")
    #     self.assertEqual(transfer_event_list[0]['args']['_value'], 2)

    #     # Check that transfer appropriately emits Transfer event
    #     transfer_tx_receipt = self.w3.eth.wait_for_transaction_receipt(self.contract.functions.transfer(self.account2, 1).transact({"from":self.account1, "gas":200000}))
    #     self.assertTrue(transfer_tx_receipt['status'])
    #     transfer_event_list = transfer_event_filter.get_new_entries()
    #     self.assertEqual(len(transfer_event_list), 1)
    #     self.assertEqual(transfer_event_list[0]['event'], "Transfer")
    #     self.assertEqual(transfer_event_list[0]['args']['_from'], self.account1)
    #     self.assertEqual(transfer_event_list[0]['args']['_to'], self.account2)
    #     self.assertEqual(transfer_event_list[0]['args']['_value'], 1)

    #     transfer_tx_receipt = self.w3.eth.wait_for_transaction_receipt(self.contract.functions.transfer(self.account1, 1).transact({"from":self.account2, "gas":200000}))
    #     self.assertTrue(transfer_tx_receipt['status'])
    #     transfer_event_list = transfer_event_filter.get_new_entries()
    #     self.assertEqual(len(transfer_event_list), 1)
    #     self.assertEqual(transfer_event_list[0]['event'], "Transfer")
    #     self.assertEqual(transfer_event_list[0]['args']['_from'], self.account2)
    #     self.assertEqual(transfer_event_list[0]['args']['_to'], self.account1)
    #     self.assertEqual(transfer_event_list[0]['args']['_value'], 1)

    #     # Check that approving amount emits events
    #     approve_tx_receipt = self.w3.eth.wait_for_transaction_receipt(self.contract.functions.approve(self.account1, 1).transact({"from":self.account2, "gas":200000}))
    #     self.assertTrue(approve_tx_receipt['status'])
    #     approval_event_list = approval_event_filter.get_new_entries()
    #     self.assertEqual(len(approval_event_list), 1)
    #     self.assertEqual(approval_event_list[0]['event'], "Approval")
    #     self.assertEqual(approval_event_list[0]['args']['_owner'], self.account2)
    #     self.assertEqual(approval_event_list[0]['args']['_spender'], self.account1)
    #     self.assertEqual(approval_event_list[0]['args']['_value'], 1)

    #     approve_tx_receipt = self.w3.eth.wait_for_transaction_receipt(self.contract.functions.approve(self.account2, 1).transact({"from":self.account3, "gas":200000}))
    #     self.assertTrue(approve_tx_receipt['status'])
    #     approval_event_list = approval_event_filter.get_new_entries()
    #     self.assertEqual(len(approval_event_list), 1)
    #     self.assertEqual(approval_event_list[0]['event'], "Approval")
    #     self.assertEqual(approval_event_list[0]['args']['_owner'], self.account3)
    #     self.assertEqual(approval_event_list[0]['args']['_spender'], self.account2)
    #     self.assertEqual(approval_event_list[0]['args']['_value'], 1)

    #     # Check that transferFrom appropriately emits Transfer event
    #     self.assertEqual(self.contract.functions.allowance(self.account3, self.account2).call(), 1)
    #     deposit_tx_receipt = self.w3.eth.wait_for_transaction_receipt(self.contract.functions.deposit().transact({"from":self.account3, "value":1000, "gas":200000}))# self.assertIsNone(self.c.deposit(value=1000, sender=self.t.k2))
    #     self.assertTrue(deposit_tx_receipt['status']) # self.assertIsNone(self.c.deposit(value=2000, sender=self.t.k1))
    #     transfer_event_list = transfer_event_filter.get_new_entries()
    #     transferFrom_tx_receipt = self.w3.eth.wait_for_transaction_receipt(self.contract.functions.transferFrom(self.account3, self.account2, 1).transact({"from":self.account2, "gas":200000}))
    #     self.assertTrue(transferFrom_tx_receipt['status'])
    #     transfer_event_list = transfer_event_filter.get_new_entries()
    #     self.assertEqual(len(transfer_event_list), 1)
    #     self.assertEqual(transfer_event_list[0]['event'], "Transfer")
    #     self.assertEqual(transfer_event_list[0]['args']['_from'], self.account3)
    #     self.assertEqual(transfer_event_list[0]['args']['_to'], self.account2)
    #     self.assertEqual(transfer_event_list[0]['args']['_value'], 1)

    #     # Check that no other ERC-compliant calls emit any events
    #     transfer_event_list = transfer_event_filter.get_new_entries()
    #     approval_event_list = approval_event_filter.get_new_entries()
    #     self.assertEqual(self.contract.functions.totalSupply().call(), 2)
    #     self.assertEqual(self.contract.functions.balanceOf(self.account1).call(), 1)
    #     self.assertEqual(self.contract.functions.allowance(self.account3, self.account2).call(), 0)
    #     transfer_event_list = transfer_event_filter.get_new_entries()
    #     approval_event_list = approval_event_filter.get_new_entries()
    #     self.assertEqual(len(transfer_event_list), 0)
    #     self.assertEqual(len(approval_event_list), 0)

    #     # Check that failed (Withdraw, Transfer) calls emit no events
    #     transfer_event_list = transfer_event_filter.get_new_entries()
    #     withdraw_tx_receipt = self.w3.eth.wait_for_transaction_receipt(self.contract.functions.withdraw(67).transact({"from":self.account1, "gas":200000}))
    #     self.assertFalse(withdraw_tx_receipt['status'])
    #     transfer_tx_receipt = self.w3.eth.wait_for_transaction_receipt(self.contract.functions.transfer(self.account2, 67).transact({"from":self.account1, "gas":200000}))
    #     self.assertFalse(transfer_tx_receipt['status'])
    #     transferFrom_tx_receipt = self.w3.eth.wait_for_transaction_receipt(self.contract.functions.transferFrom(self.account3, self.account2, 67).transact({"from":self.account2, "gas":200000}))
    #     self.assertFalse(transferFrom_tx_receipt['status'])
    #     transfer_event_list = transfer_event_filter.get_new_entries()
    #     self.assertEqual(len(transfer_event_list), 0)


    def test_failed_send_in_withdraw(self):
        external_code = """
            contract ERC20 {
                function deposit() public payable;
                function withdraw(uint256 _value) public returns (bool success);
            }

            contract Dummy {

                address private erc20_addr;
                uint256 val;

                constructor(address _erc20_addr) public {
                    erc20_addr = _erc20_addr;
                }

                function my_deposit() public payable {
                    val = msg.value;
                    ERC20(erc20_addr).deposit.value(val)();
                }

                function my_withdraw() public returns (bool success) {
                    return ERC20(erc20_addr).withdraw(val / 1000);
                }

                function() external payable {
                    revert();
                }
            }
        """

        dummy_abi = """[{"constant": false, "inputs": [], "name": "my_deposit", "outputs": [], "payable": true, "stateMutability": "payable", "type": "function" }, { "constant": false, "inputs": [], "name": "my_withdraw", "outputs": [ { "name": "success", "type": "bool" } ], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "inputs": [ { "name": "_erc20_addr", "type": "address" } ], "payable": false, "stateMutability": "nonpayable", "type": "constructor" }, { "payable": true, "stateMutability": "payable", "type": "fallback" } ]"""
        dummy_bytecode = "608060405234801561001057600080fd5b506040516020806102cb8339810180604052602081101561003057600080fd5b8101908080519060200190929190505050806000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff1602179055505061023a806100916000396000f3fe608060405260043610610046576000357c0100000000000000000000000000000000000000000000000000000000900480637246b2ff1461004b578063a974788514610055575b600080fd5b610053610084565b005b34801561006157600080fd5b5061006a61012d565b604051808215151515815260200191505060405180910390f35b346001819055506000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1663d0e30db06001546040518263ffffffff167c01000000000000000000000000000000000000000000000000000000000281526004016000604051808303818588803b15801561011257600080fd5b505af1158015610126573d6000803e3d6000fd5b5050505050565b60008060009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16632e1a7d4d6103e860015481151561017b57fe5b046040518263ffffffff167c010000000000000000000000000000000000000000000000000000000002815260040180828152602001915050602060405180830381600087803b1580156101ce57600080fd5b505af11580156101e2573d6000803e3d6000fd5b505050506040513d60208110156101f857600080fd5b810190808051906020019092919050505090509056fea165627a7a7230582065bd68b7c2866b879522372801137c6c376c00ab2cc7b847aef50ee16d858e660029"

        # deploy the contract and pass the ERC20 contract's address as argument
        ext = self.w3.eth.contract(abi=dummy_abi, bytecode=dummy_bytecode)
        tx_hash = ext.constructor(self.contract_address).transact({'from': self.deploy_address, 'gas': 2000000})
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, 180)
        ext = self.w3.eth.contract(abi=dummy_abi, address=tx_receipt.contractAddress)

        # deposit should work
        tx_hash = ext.functions.my_deposit().transact({'from': self.account1, 'value':2000, 'gas': 2000000}) # self.assertIsNone(ext.my_deposit(value=2000))
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        # withdraw should throw
        tx_hash = ext.functions.my_withdraw().transact({'from': self.account1, 'gas': 2000000}) # self.assertIsNone(ext.my_deposit(value=2000))
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.assertFalse(tx_receipt['status'])# self.assert_tx_failed(lambda: ext.my_withdraw())

        # re-deploy the contract with a working default function
        # external_code2 = external_code.replace("throw", "return")

        dummy2_abi = """[{"constant": false, "inputs": [], "name": "my_deposit", "outputs": [], "payable": true, "stateMutability": "payable", "type": "function" }, { "constant": false, "inputs": [], "name": "my_withdraw", "outputs": [ { "name": "success", "type": "bool" } ], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "inputs": [ { "name": "_erc20_addr", "type": "address" } ], "payable": false, "stateMutability": "nonpayable", "type": "constructor" }, { "payable": true, "stateMutability": "payable", "type": "fallback" } ]"""
        dummy2_bytecode = "608060405234801561001057600080fd5b506040516020806102c88339810180604052602081101561003057600080fd5b8101908080519060200190929190505050806000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555050610237806100916000396000f3fe608060405260043610610046576000357c0100000000000000000000000000000000000000000000000000000000900480637246b2ff14610048578063a974788514610052575b005b610050610081565b005b34801561005e57600080fd5b5061006761012a565b604051808215151515815260200191505060405180910390f35b346001819055506000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1663d0e30db06001546040518263ffffffff167c01000000000000000000000000000000000000000000000000000000000281526004016000604051808303818588803b15801561010f57600080fd5b505af1158015610123573d6000803e3d6000fd5b5050505050565b60008060009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16632e1a7d4d6103e860015481151561017857fe5b046040518263ffffffff167c010000000000000000000000000000000000000000000000000000000002815260040180828152602001915050602060405180830381600087803b1580156101cb57600080fd5b505af11580156101df573d6000803e3d6000fd5b505050506040513d60208110156101f557600080fd5b810190808051906020019092919050505090509056fea165627a7a7230582093169cbec5d04871619c21570a4a729c6fb4cb98028161fe608b38fa075431ec0029"
        ext2 = self.w3.eth.contract(abi=dummy2_abi, bytecode=dummy2_bytecode)
        tx_hash = ext2.constructor(self.contract_address).transact({'from': self.deploy_address, 'gas': 2000000})
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, 180)
        ext2 = self.w3.eth.contract(abi=dummy2_abi, address=tx_receipt.contractAddress)

        # deposit should work
        tx_hash = ext2.functions.my_deposit().transact({'from': self.account1, 'value':2000, 'gas': 2000000}) # self.assertIsNone(ext2.my_deposit(value=2000))
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        # withdraw should work
        self.assertEqual(self.eth_tester.get_balance(ext2.address), 0)
        #event_filter = self.w3.eth.filter({"address": ext2.address})
        tx_hash = ext2.functions.my_withdraw().transact({'from': self.account1, 'gas': 2000000}) # self.assertIsNone(ext2.my_deposit(value=2000))
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.assertTrue(tx_receipt['status'])# self.assert_tx_failed(lambda: ext2.my_withdraw())
        #print(event_filter.get_all_entries()) # no events
        self.assertEqual(self.eth_tester.get_balance(ext2.address), 2000)



if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestERC20Challenge)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    tests_run = result.testsRun
    failures_list = result.failures + result.errors
    test_failures = len(failures_list)
    score = int(tests_run - test_failures)
    print("Final Score:",score)


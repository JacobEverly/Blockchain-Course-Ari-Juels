from typing import Optional, List
from hashlib import sha256

def verify(obj: str, proof: str, commitment: str) -> bool:
	raise NotImplementedError	

class Prover:
	def __init__(self):
		pass
	
	# Build a merkle tree and return the commitment
	def build_merkle_tree(self, objects: List[str]) -> str:
		raise NotImplementedError

	def get_leaf(self, index: int) -> Optional[str]:
		raise NotImplementedError

	def generate_proof(self, index: int) -> Optional[str]:
		raise NotImplementedError
import hashlib

class Prover:
    def __init__(self):
        self.levels = []

    def build_merkle_tree(self, objects):
        self.levels = []
        num_levels = len(objects).bit_length()
        self.levels = [[] for i in range(num_levels)]
        self.levels[0] = [hashlib.sha256(o.encode()).hexdigest() for o in objects]

        for i in range(1, num_levels):
            level = self.levels[i]
            prev_level = self.levels[i-1]
            for j in range(0, len(prev_level), 2):
                if j+1 == len(prev_level):
                    level.append(prev_level[j])
                else:
                    combined = prev_level[j] + prev_level[j+1]
                    level.append(hashlib.sha256(combined.encode()).hexdigest())

        return self.levels[-1][0]

    def get_leaf(self, index):
        if index < len(self.levels[0]):
            return self.levels[0][index]
        else:
            return None

    def generate_proof(self, index):
        if index < len(self.levels[0]):
            proof = []
            level = 0
            node_index = index
            while node_index > 0:
                is_right_child = node_index % 2
                sibling_index = node_index - 1 if is_right_child else node_index + 1
                sibling = self.levels[level][sibling_index] if sibling_index < len(self.levels[level]) else None
                proof.append((is_right_child, sibling))
                node_index = (node_index - 1) // 2
                level += 1
            return proof
        else:
            return None

def verify(object, proof, commitment):
    if proof is None:
        return False
    digest = hashlib.sha256(object.encode()).hexdigest()
    for is_right_child, sibling in proof:
        if is_right_child:
            combined = sibling + digest
        else:
            combined = digest + sibling
        digest = hashlib.sha256(combined.encode()).hexdigest()
    return digest == commitment


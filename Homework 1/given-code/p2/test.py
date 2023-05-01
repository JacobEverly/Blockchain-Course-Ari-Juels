import sys
import random
import string
from merkle import Prover, verify
from collections import defaultdict
from matplotlib import pyplot as plt
from hashlib import sha256
from math import log2, ceil
from copy import deepcopy

def test_basic(objects):
    _leaf_passed, _trivial_pi_passed = 0, 0
    try:
        p = Prover()
        p.build_merkle_tree(deepcopy(objects))
        n = len(objects)
        positive_indices = [random.randint(0, n-1) for x in range(4)]
        positive_indices += [0,n-1]
        negative_indices = [random.randint(n, 2*n) for x in range(2)]
        negative_indices += [n]
        for i in positive_indices:
            try:
                ret = p.get_leaf(i)
                if ret == objects[i] or ret == sha256(objects[i].encode()).hexdigest():
                    _leaf_passed += 1
            except:
                pass
        for i in negative_indices:
            try:
                ret = p.generate_proof(i)
                if ret is None:
                    _trivial_pi_passed += 1
            except:
                pass
            try:
                ret = p.get_leaf(i)
                if ret is None:
                    _leaf_passed += 1
            except:
                pass
    except:
        pass
    return _leaf_passed, _trivial_pi_passed

def test_verify(objects):
    _passed = 0
    try:
        p = Prover()
        c = p.build_merkle_tree(deepcopy(objects))
        n = len(objects)
        indices = [random.randint(0, n-1) for x in range(4)]
        indices += [0,n-1]

        for idx in indices:
            try:
                pi = p.generate_proof(idx)        
                obj_hash = sha256(objects[idx].encode()).hexdigest()
                if verify(objects[idx], pi, c) or verify(obj_hash, pi, c):
                    _passed += 1
            except:
                pass
    except:
        pass
    return _passed

print(test_basic(['a']), "passed in (9, 3) cases")
print(test_verify(['a']), " passed in 6 cases")

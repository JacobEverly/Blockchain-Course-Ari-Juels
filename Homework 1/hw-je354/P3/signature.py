import string
import random
import hashlib

# return the hash of a string
def SHA(s: string) -> string:
    return hashlib.sha256(s.encode()).hexdigest()

# transfer a hex string to integer
def toDigit(s: string) -> int:
    return int(s, 16)

# generate 2^d (si^{-1}, si) pairs based on seed r
def KeyPairGen(d: int, r: int) -> dict:
    pairs = {}
    random.seed(r)
    for i in range(1 << d):
        cur = random.randbytes(32).hex()
        while cur in pairs:
            cur = random.randbytes(32).hex()
        pairs[cur] = SHA(cur)
    return pairs

class MTSignature:
    def __init__(self, d: int, k: int):
        self.d = d
        self.k = k
        self.n = 2**(self.d-1).bit_length()
        self.treenodes = [None] * (d+1)
        for i in range(d+1):
            self.treenodes[i] = [None] * (1 << i)
        self.sk = [None] * (1 << d)
        self.pk = None # same as self.treenodes[0][0]

    # Populate the fields self.treenodes, self.sk and self.pk. Returns self.pk.
    def KeyGen(self, seed):
        self.seed = seed.to_bytes(32, byteorder='big')
        keypairs = KeyPairGen(self.d, seed)
        for index, key in enumerate(keypairs):
            self.treenodes[self.d][index] = keypairs[key]
            self.sk[index] = key
            
        for i in range(self.d-1, -1, -1):
            for j in range(len(self.treenodes[i])):
                left = self.treenodes[i+1][2*j]
                right = self.treenodes[i+1][min(2*j+1, 2*j+1)]
                # self.treenodes[i][j] = hashlib.sha256(bytes.fromhex(left + right)).hexdigest()
                self.treenodes[i][j] = SHA(format(j, "b").zfill(256) + left + right)
                
        # self.sk = hashlib.sha256(self.seed).hexdigest()
        self.pk = self.treenodes[0][0]
        
        return self.pk


    # Returns the path SPj for the index j
    # The order in SPj follows from the leaf to the root.
    def Path(self, j: int) -> str:
        SPj = ""
        cur = self.sk[j][0]
        for i in range(self.d, 0, -1):
            if j % 2 == 0:
                sibling = self.treenodes[i][j+1]
            else:
                sibling = self.treenodes[i][j-1]
            SPj += sibling
            j //= 2
        return SPj

    # Returns the signature. The format of the signature is as follows: ([sigma], [SP]).
    # The first is a sequence of sigma values and the second is a list of sibling paths.
    # Each sibling path is in turn a d-length list of tree node values. 
    # All values are 64 bytes. Final signature is a single string obtained by concatenating all values.
    def Sign(self, m: str) -> str:
        
        private = ""
        sp = ""
        
        for i in range(1, self.k+1):
            value = toDigit(SHA(format(i, "b").zfill(256) + m)) % (1 << self.d)
            private += self.sk[value]
            sp += self.Path(value)
            
        return private + sp

mt = MTSignature(d=10, k=2)
pk = mt.KeyGen(2023)
m = "Jacob wants to send Ari 100 USDC to get an A in his class."
signed = mt.Sign(m)

counter = 0
while True:
    fm = "Ari wants to send Jacob {} LINK".format(counter)
    forgedsign = mt.Sign(fm)
    if forgedsign == signed:
        with open("forgery.txt", "w") as f:
            f.write(fm + "\n")
            f.write(m + "\n")
            print("Forged Messages Written.")
        break
    counter += 1
    
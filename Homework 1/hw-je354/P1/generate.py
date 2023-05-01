import hashlib
import random
import string
import secrets

k = 4  # number of preimages
n = 28  # number of leading bits for collision
netid = "je354"  # your NetID

def find_collision():
    print(bin(int(hashlib.sha256(netid.encode("ascii")).hexdigest(), base=16)).lstrip('0b').zfill(256)[:16])
    watermark = (hashlib.sha256(netid.encode("ascii")).hexdigest()[:4])
    watermark_bytes = bytes.fromhex(watermark)
    hashes = {}
    counter = 0
    while True:
        preimage = secrets.token_bytes(6)
        # preimage = str(preimage)
        # hash = hashlib.sha256((watermark + preimage).encode('ascii'))
        hash = bin(int(hashlib.sha256((watermark_bytes + preimage)).hexdigest(), base=16)).lstrip('0b').zfill(256)[:n]
        if hash in hashes:
            hashes[hash].append(hex(int.from_bytes((watermark_bytes + preimage), "big")).lstrip('0x'))
            if len(hashes[hash]) == 4:
                print(hash)
                return  hashes[hash]
        else:
            hashes[hash] = [hex(int.from_bytes((watermark_bytes + preimage), "big")).lstrip('0x')]
        counter += 1

print(find_collision())

coins = find_collision()

with open("coin.txt", "w") as f:
    for ci in coins :
        f.write(ci + "\n")
print("Coin written to file.")


# Function to generate a random netid
def generate_netid():
    letters = [chr(i) for i in range(ord('a'), ord('z')+1)]
    digits = [str(i) for i in range(10)]
    l1 = random.choice(letters)
    l2 = random.choice(letters)
    i = random.choice([2, 3])
    j = ''.join(random.choices(digits, k=2))
    return f'{l1}{l2}{i}{j}'

def forged_watermark():
        # calculate the watermark from the NetID
        watermark = bin(int(hashlib.sha256(netid.encode("ascii")).hexdigest(), base=16)).lstrip('0b').zfill(256)[:16]
        #fakes dictionary to store the fake netids
        fakes = {}
        counter = 0
        while True:
            # calculate watermark for the Fake NetID
            fake_netid = generate_netid()
            fake_hash = bin(int(hashlib.sha256(fake_netid.encode("ascii")).hexdigest(), base=16)).lstrip('0b').zfill(256)[:16]
            hash = fake_hash
            if  hash == watermark and netid != fake_netid:
                return [fake_netid]

forged = forged_watermark()

with open("forged-watermark.txt", "w") as f:
    for netid in forged :
        f.write(netid + "\n")
print("Coin written to file.")

import hashlib

hash1 = hashlib.sha3_256()
hash1.update(b"This is my string")
print("hash1: ")
print(hash1.hexdigest())

hash2 = hashlib.sha3_256()
hash2.update(b"Dit is my string TOO")
print("hash2: ")
print(hash2.hexdigest())
hash3 = hashlib.sha3_256()

hash3.update(b"This is my string")
print("hash3: ")
print(hash3.hexdigest() + '\n')

print("hash and hash2 are equal: ")
print(hash1.hexdigest() == hash2.hexdigest() + '\n')

print("hash and hash3 are equal: ")
print(hash1.hexdigest() == hash3.hexdigest() + '\n')

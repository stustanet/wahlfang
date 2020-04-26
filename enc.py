alphabet = "0123456789abcdefghjknpqrstuvwxyz"

decodeMap = {}
for index, i in enumerate(alphabet):
    decodeMap[i] = index

def encode(i, length=None):
    i = int(i)
    out = ""
    while i > 0:
        idx = i & 0x1f
        out = alphabet[idx] + out
        i >>= 5
    if length:
        if len(out) > length:
            raise ValueError("value too large for given length")
        out = alphabet[0] * (length-len(out)) + out
    return out

def decode(s):
    i = 0
    for c in s:
        i <<= 5
        i += decodeMap[c]
    return i

e = encode(999999, 4)
print(e)
d = decode(e)
print(d)

e = encode(0, 4)
print(e)
d = decode(e)
print(d)


e = encode(12345, 4)
print(e)
d = decode(e)
print(d)
